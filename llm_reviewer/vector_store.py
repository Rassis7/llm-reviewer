from langchain_chroma import Chroma
from llm_reviewer.embeddings import Embedding
from uuid import uuid4
from typing import Optional, List, Dict, TypeVar
from langchain_core.documents import Document
from abc import ABC, abstractmethod

Self = TypeVar("Self", bound="Base")  # type: ignore


class IVectorStore(ABC):
    @abstractmethod
    def load(
        self: Self,
        path: str,
        collection_name: str,
        embeddings: Embedding,
        documents: Optional[List[Document]] = None,
    ) -> Self:
        raise NotImplementedError

    @abstractmethod
    def save_documents(self: Self, documents) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_query(self: Self, query: str, k: int) -> List[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_retriever_from_similar(
        self: Self, query: str, embeddings: Embedding, k: int = 2
    ) -> Chroma:
        raise NotImplementedError


class VectorStore(IVectorStore):
    store: Optional[Chroma] = None

    def __init__(self, store: Optional[Chroma] = None):
        self.store = store if store else None

    def load(
        self: Self,
        path: str,
        collection_name: str,
        embedding: Embedding,
        documents: Optional[List[Document]] = None,
    ) -> Self:
        """
        Inicializa ou carrega um banco de vetores Chroma.

        - Se houver documentos, cria um novo banco de dados.
        - Se não houver, carrega a persistência existente.
        """
        store = None
        if documents and len(documents) > 0:
            store = Chroma.from_documents(
                documents=documents,
                embedding=embedding,
                persist_directory=path,
                collection_name=collection_name,
            )
        else:
            store = Chroma(
                persist_directory=path,
                embedding_function=embedding,
                collection_name=collection_name,
            )

        return VectorStore(store)  # type: ignore

    def save_documents(self, documents: List[dict]):
        """
        Adiciona novos documentos ao Chroma e persiste a atualização.
        """
        if not self.store:
            raise ValueError("VectorStore não foi carregado. Chame `load()` primeiro.")

        uuids = [str(uuid4()) for _ in documents]
        self.store.add_documents(documents=documents, ids=uuids)
        self.store.persist()

    def get_query(self, query: str, k: int = 2) -> List[dict]:
        """
        Realiza uma busca por similaridade no banco de vetores.
        """
        if not self.store:
            raise ValueError("VectorStore não foi carregado. Chame `load()` primeiro.")

        return self.store.similarity_search(query, k=k)

    def get_retriever_from_similar(
        self, query: str, embeddings: Embedding, k: int = 2
    ) -> Chroma:
        """
        Busca documentos similares à consulta e cria um novo retriever com eles.
        """
        if not self.store:
            raise ValueError("VectorStore não foi carregado. Chame `load()` primeiro.")

        similar_documents = self.store.similarity_search(query, k=k)

        temp_store = Chroma.from_documents(
            documents=similar_documents, embedding=embeddings
        )

        return temp_store.as_retriever()
