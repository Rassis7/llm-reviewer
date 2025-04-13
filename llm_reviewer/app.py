from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.runnables import (
    RunnableLambda,
    RunnablePassthrough,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from llm_reviewer.llm import LLM, AcceptableLLMModels, PromptTemplate
from llm_reviewer.vector_store import VectorStore
from llm_reviewer.embeddings import Embeddings
from typing import Optional, List
import os
import importlib.resources
import json
import re


def load_file(file_name: str) -> str:

    with importlib.resources.open_text("llm_reviewer.files", file_name) as file:
        content = file.read()
    return content


def load_store(documents: Optional[List[Document]] = None) -> VectorStore:
    print("🪣 Loading vector store...")
    embedding = Embeddings.load()

    return VectorStore().load(
        path=os.environ["DB_PATH"],
        collection_name=os.environ["COLLECTION_NAME"],
        embedding=embedding,
        documents=documents,
    )


def create_vector_loader() -> VectorStore:
    print("🪣 Creating vector loader")
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
    print(f"👀 Pull Request JSON response: {chain_output}")

    match = re.search(r"\[\s*\{.*\}\s*\]", chain_output, re.DOTALL)
    if match:
        json_str = match.group(0).strip()
        try:
            array_obj = json.loads(json_str)
            print("✅ JSON processed with success!")

            with importlib.resources.path(
                "llm_reviewer.files", "code_review.json"
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
    pull_request = load_file("pull-request.txt")

    embedding = Embeddings.load()

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
        print(f"🔥 Response: {response_str}")

        with importlib.resources.path("llm_reviewer.files", "code_review.md") as path:
            with path.open("w", encoding="utf-8") as file:
                file.write(response_str)
    else:
        print("❌ No response generated")


if __name__ == "__main__":
    main()
