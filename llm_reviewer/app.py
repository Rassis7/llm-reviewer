from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from llm_reviewer.llm import LLM, AcceptableLLMModels
from llm_reviewer.vector_store import VectorStore
from llm_reviewer.embeddings import Embedding, AcceptableEmbeddings
from typing import Optional, List, Dict
import os


def load_file(file_name: str) -> str:
    import importlib.resources

    with importlib.resources.open_text("llm_reviewer.files", file_name) as file:
        content = file.read()
    return content


def load_embeddings():
    generic_embedding = Embedding(embedding=AcceptableEmbeddings.HUGGING_FACE)
    return generic_embedding.embedding


def load_store(documents: Optional[List[Document]] = None) -> VectorStore:
    embedding = load_embeddings()

    return VectorStore().load(
        path=os.environ["DB_PATH"],
        collection_name=os.environ["COLLECTION_NAME"],
        embedding=embedding,
        documents=documents,
    )


def create_vector_loader() -> VectorStore:
    goo_code_rules = load_file("good-code.md")
    doc = Document(page_content=goo_code_rules)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = text_splitter.split_documents([doc])

    return load_store(documents)


def load_knowledge_base() -> VectorStore:
    if os.path.exists(os.environ["DB_PATH"]):
        db = load_store()
        return db
    else:
        new_db = create_vector_loader()
        return new_db


def load_llm():
    llm = LLM(model=AcceptableLLMModels.GPT4)
    return llm.model


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def main():
    knowledgeBase = load_knowledge_base()
    llm = load_llm()
    prompt = LLM.load_prompt()
    pull_request = load_file("pull-request.txt")

    embedding = load_embeddings()

    retriever = knowledgeBase.get_retriever_from_similar(
        query=pull_request, embeddings=embedding
    )

    rag_chain = (
        {"context": retriever | format_docs, "input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    pull_request = load_file("pull-request.txt")

    response = rag_chain.invoke(pull_request)
    print(f"RESPONSE: {response}")


if __name__ == "__main__":
    main()
