from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from llm_reviewer.llm import LLM, AcceptableLLMModels
from llm_reviewer.vector_store import VectorStore
from llm_reviewer.embeddings import Embedding, AcceptableEmbeddings
from typing import Optional, List
from langchain_core.prompts import ChatPromptTemplate

import os


def load_file(path: str, file_name: str) -> str:
    import importlib.resources

    with importlib.resources.open_text(f"llm_reviewer.{path}", file_name) as file:
        content = file.read()
    return content


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


def create_vector_loader() -> VectorStore:
    goo_code_rules = load_file("docs", "good-code.md")
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
        """
    prompt = ChatPromptTemplate.from_template(prompt_template)
    return prompt


def main():
    try:
        knowledgeBase = load_knowledge_base()
        llm = load_llm()
        prompt = load_prompt()
        pull_request = load_file("files", "pull-request.txt")

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
        print(f"RESPONSE: {response}")
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
