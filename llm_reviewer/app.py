from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from llm_reviewer.llm import LLM, AcceptableLLMModels
from llm_reviewer.git import Git
from llm_reviewer.vector_store import VectorStore
from llm_reviewer.embeddings import Embedding, AcceptableEmbeddings
from typing import Optional, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_docling import DoclingLoader

import os


def load_embeddings():
    generic_embedding = Embedding(embedding=AcceptableEmbeddings.OPEN_AI)
    return generic_embedding.embedding


def load_store(documents: Optional[List[Document]] = None) -> VectorStore:
    embedding = load_embeddings()

    return VectorStore().load(
        path=os.environ["DB_PATH"],
        collection_name=os.environ["COLLECTION_NAME"],
        embedding=embedding,
        documents=documents,
    )


def normalize_documents():
    docs_dir = os.path.join(os.path.dirname(__file__), "../llm_reviewer/docs")
    file_paths = [
        os.path.join(docs_dir, f)
        for f in os.listdir(docs_dir)
        if os.path.isfile(os.path.join(docs_dir, f))
    ]
    loader = DoclingLoader(file_paths)
    documents = loader.load()
    markdown_docs = [doc.page_content for doc in documents]
    return markdown_docs


def create_vector_loader() -> VectorStore:
    documents = normalize_documents()
    docs = [Document(page_content=doc) for doc in documents]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = text_splitter.split_documents(docs)
    return load_store(split_docs)


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


def load_prompt():
    prompt_template = """
            You are a senior developer tasked with reviewing the code below. You have two essential elements for your analysis:
            - Context: A description of the guidelines and best practices that must be followed.  
            - Code (Input): The code you will be reviewing.  

            Based on these elements, your goal is to identify and highlight only the aspects of the code that do not comply with the provided context. 
            This includes improper practices, code smells, potential bugs, and syntax improvements.  

            Avoid suggesting the adoption of new libraries or technologies that are not included in the given context.  

            Context: {context}  

            Code (Input): {input}  

            Instructions: 
                - Analyze the code based on the provided context.  
                - Point out only the discrepancies in relation to the given context.  
                - Do not suggest introducing new libraries or technologies outside the context.  
                - Always specify which file the line belongs to and display the line of code being reviewed.
                - If there is no improvement observed in the file, just ignore it
                - Do not add any comments or suggestions that deviate from what is explicitly stated in your instructions.
        """
    prompt = ChatPromptTemplate.from_template(prompt_template)
    return prompt


def main():
    try:
        knowledgeBase = load_knowledge_base()
        llm = load_llm()
        prompt = load_prompt()

        token = os.environ["GIT_TOKEN"]
        fetcher = Git(token=token)
        pull_request = fetcher.get_diff(
            project_id=19655,
            merge_request_iid=68,
        )

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

        response = rag_chain.invoke(pull_request)

        with open("output.md", "w") as f:
            f.write(response)

    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
