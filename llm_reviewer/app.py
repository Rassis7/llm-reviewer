from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.runnables import (
    RunnableLambda,
    RunnablePassthrough,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from llm_reviewer.git import Git
from llm_reviewer.llm import (
    LLM,
    AcceptableLLMModels,
    PromptTemplate,
    AcceptableLLMProviders,
)
from llm_reviewer.vector_store import VectorStore
from llm_reviewer.embeddings import Embedding, AcceptableEmbeddings
from llm_reviewer.documents import (
    convert_to_markdown,
    format_docs,
    format_and_save_json_response,
)

from typing import Optional, List
import os
import importlib.resources

import streamlit as st


def load_embeddings():
    generic_embedding = Embedding(embedding=AcceptableEmbeddings.OPEN_AI)
    return generic_embedding.embedding


def load_store(documents: Optional[List[Document]] = None) -> VectorStore:
    st.write("🪣 Loading vector store")
    print("🪣 Loading vector store")

    embedding = load_embeddings()
    return VectorStore().load(
        path=os.environ["DB_PATH"],
        collection_name=os.environ["COLLECTION_NAME"],
        embedding=embedding,
        documents=documents,
    )


def create_vector_loader() -> VectorStore:
    st.write("🪣 Creating vector loader")
    print("🪣 Creating vector loader")
    documents = convert_to_markdown()
    docs = [Document(page_content=doc) for doc in documents]

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = text_splitter.split_documents(docs)

    return load_store(split_docs)


def save_vector_store_documents(file_name: Optional[str] = None):
    st.write("🪣 Saving vector store")
    print("🪣 Saving vector store")

    embedding = load_embeddings()
    vector_store = VectorStore().load(
        path=os.environ["DB_PATH"],
        collection_name=os.environ["COLLECTION_NAME"],
        embedding=embedding,
    )

    documents = convert_to_markdown(file_name=file_name)
    docs = [Document(page_content=doc) for doc in documents]

    vector_store.save_documents(docs)


def load_knowledge_base() -> VectorStore:
    if os.path.exists(os.environ["DB_PATH"]):
        db = load_store()
        return db
    else:
        new_db = create_vector_loader()
        return new_db


def load_conversation_model():
    st.write("🤖 Loading conversation llm model")
    print("🤖 Loading conversation llm model")
    llm = LLM(
        model=AcceptableLLMModels.CONVERSATION_MODEL,
        provider=AcceptableLLMProviders.OPENAI,
    )
    return llm.model


def load_code_model():
    st.write("🧑‍💻 Loading coder llm model")
    print("🧑‍💻 Loading coder llm model")
    llm = LLM(
        model=AcceptableLLMModels.CODE_MODEL, provider=AcceptableLLMProviders.OPENAI
    )
    return llm.model


def map_review_to_format(chain_output):
    st.write(f"🔍 Mapping review to format")
    print(f"🔍 Mapping review to format")
    return {"reviewed_code": chain_output}


def get_pull_request_diff():
    git = Git(token=os.environ["GIT_TOKEN"])
    return git.get_diff(
        project_id=os.environ["GIT_PROJECT_ID"],
        merge_request_iid=os.environ["GIT_MERGE_REQUEST_IID"],
    )


def write_merge_request_comment(comment: str):
    git = Git(token=os.environ["GIT_TOKEN"])
    git.write_comment(
        project_id=os.environ["GIT_PROJECT_ID"],
        merge_request_iid=os.environ["GIT_MERGE_REQUEST_IID"],
        comment=comment,
    )


def run_review():
    knowledgeBase = load_knowledge_base()
    llm_code_model = load_code_model()
    context_prompt = LLM.load_prompt(prompt=PromptTemplate.CONTEXT)
    llm_conversation_model = load_conversation_model()
    response_prompt = LLM.load_prompt(prompt=PromptTemplate.RESPONSE)

    pull_request = get_pull_request_diff()

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
                # write_merge_request_comment(comment=response_str)

        st.write(f"🔥 Created code_review.md file")
        print(f"🔥 Created code_review.md file")
        return response_str
    else:
        st.write("❌ No response generated")
        print("❌ No response generated")
        return None


if __name__ == "__main__":
    run_review()
