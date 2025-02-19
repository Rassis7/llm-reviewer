from langchain_chroma import Chroma
from llm_reviewer.embeddings import Embeddings
from uuid import uuid4
from typing import Optional, List, TypeVar
from langchain_core.documents import Document
from abc import ABC, abstractmethod

Self = TypeVar("Self", bound="Base")  # type: ignore


class IVectorStore(ABC):
    @abstractmethod
    def load(
        self: Self,
        path: str,
        collection_name: str,
        embeddings: Embeddings,
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
        self: Self, query: str, embeddings: Embeddings, k: int = 2
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
        embedding: Embeddings,
        documents: Optional[List[Document]] = None,
    ) -> Self:
        """
        Initializes or loads a Chroma vector database.

        - If documents exist, creates a new database.
        - If not, loads the existing persistence.
        """
        store = None
        if documents and len(documents) > 0:
            store = Chroma.from_documents(
                documents=documents,
                embedding=embedding,
                persist_directory=path,
                collection_name=collection_name,
            )
            print("🪣 Created vector store")
        else:
            store = Chroma(
                persist_directory=path,
                embedding_function=embedding,
                collection_name=collection_name,
            )
            print("🪣 Got vector store")

        return VectorStore(store)  # type: ignore

    def save_documents(self, documents: List[dict]):
        """
        Adds new documents to Chroma and persists the update.
        """
        if not self.store:
            raise ValueError("VectorStore não foi carregado. Chame `load()` primeiro.")

        uuids = [str(uuid4()) for _ in documents]
        self.store.add_documents(documents=documents, ids=uuids)
        self.store.persist()
        print("✅ Saved documents")

    def get_query(self, query: str, k: int = 2) -> List[dict]:
        """
        Performs a similarity search in the vector bank.
        """
        if not self.store:
            raise ValueError("VectorStore não foi carregado. Chame `load()` primeiro.")

        print("⚡️ getting query")
        return self.store.similarity_search(query, k=k)

    def get_retriever_from_similar(
        self, query: str, embeddings: Embeddings, k: int = 2
    ) -> Chroma:
        """
        Searches for documents similar to the query and creates a new retriever with them.
        """
        if not self.store:
            raise ValueError("VectorStore não foi carregado. Chame `load()` primeiro.")

        similar_documents = self.store.similarity_search(query, k=k)

        temp_store = Chroma.from_documents(
            documents=similar_documents, embedding=embeddings
        )

        print("⚡️ getting similar retriever")
        return temp_store.as_retriever()
