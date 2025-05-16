from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.runnables import (
    RunnableLambda,
    RunnablePassthrough,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_docling import DoclingLoader

from llm_reviewer.git import Git
from llm_reviewer.llm import LLM, AcceptableLLMModels, PromptTemplate
from llm_reviewer.vector_store import VectorStore
from llm_reviewer.embeddings import Embedding, AcceptableEmbeddings

from typing import Optional, List
import os
import importlib.resources
import json
import re


def load_embeddings():
    generic_embedding = Embedding(embedding=AcceptableEmbeddings.OPEN_AI)
    return generic_embedding.embedding


def load_store(documents: Optional[List[Document]] = None) -> VectorStore:
    print("🪣 Loading vector store...")
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
    print("🪣 Creating vector loader")
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


def load_conversation_model():
    print("🤖 Loading conversation llm model")
    llm = LLM(model=AcceptableLLMModels.CONVERSATION_MODEL)
    return llm.model


def load_code_model():
    print("🧑‍💻 Loading coder llm model")
    llm = LLM(model=AcceptableLLMModels.CODE_MODEL)
    return llm.model


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def map_review_to_format(chain_output):
    print(f"🔍 Mapping review to format")
    return {"reviewed_code": chain_output}


def format_and_save_json_response(chain_output):
    match = re.search(r"\[\s*\{.*\}\s*\]", chain_output, re.DOTALL)
    if match:
        json_str = match.group(0).strip()
        try:
            array_obj = json.loads(json_str)
            print("✅ JSON processed with success!")

            with importlib.resources.path(
                "llm_reviewer.response", "code_review.json"
            ) as path:
                with path.open("w", encoding="utf-8") as file:
                    json.dump(array_obj, file, indent=4, ensure_ascii=False)

            print("📂 JSON response saved in 'code_review.json'")
            return array_obj

        except json.JSONDecodeError as e:
            print("❌ JSON Decode error:", e)

    else:
        print("❌ No JSON found")

    return None


def main():
    knowledgeBase = load_knowledge_base()
    llm_code_model = load_code_model()
    context_prompt = LLM.load_prompt(prompt=PromptTemplate.CONTEXT)
    llm_conversation_model = load_conversation_model()
    response_prompt = LLM.load_prompt(prompt=PromptTemplate.RESPONSE)

    token = os.environ["GIT_TOKEN"]
    fetcher = Git(token=token)
    pull_request = fetcher.get_diff(
        project_id=os.environ["GIT_PROJECT_ID"],
        merge_request_iid=os.environ["GIT_MERGE_REQUEST_IID"],
    )

    embedding = load_embeddings()

    retriever = knowledgeBase.get_retriever_from_similar(
        query=pull_request, embeddings=embedding
    )

    mapping_step = RunnableLambda(map_review_to_format)
    format_json_step = RunnableLambda(format_and_save_json_response)

    code_review_chain = (
        {"context": retriever | format_docs, "input": RunnablePassthrough()}
        | context_prompt
        | llm_code_model
        | StrOutputParser()
    )

    output_format_chain = (
        {"reviewed_code": RunnablePassthrough()}
        | response_prompt
        | llm_conversation_model
        | StrOutputParser()
    )

    final_chain = (
        code_review_chain | format_json_step | mapping_step | output_format_chain
    )

    response = final_chain.invoke(pull_request)

    if response:
        response_str = str(response)

        with importlib.resources.path(
            "llm_reviewer.response", "code_review.md"
        ) as path:
            with path.open("w", encoding="utf-8") as file:
                file.write(response_str)

        print(f"🔥 Created code_review.md file")
    else:
        print("❌ No response generated")


if __name__ == "__main__":
    main()
