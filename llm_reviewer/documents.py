from langchain_docling import DoclingLoader
from typing import Optional
import os
import json
import re
import importlib.resources


def convert_to_markdown(file_name: Optional[str] = None):
    docs_dir = os.path.join(os.path.dirname(__file__), "../llm_reviewer/docs")
    file_paths = [
        os.path.join(docs_dir, f)
        for f in os.listdir(docs_dir)
        if os.path.isfile(os.path.join(docs_dir, f))
    ]

    files = [f"{docs_dir}/{file_name}"] if file_name else file_paths
    loader = DoclingLoader(files)
    documents = loader.load()
    markdown_docs = [doc.page_content for doc in documents]
    return markdown_docs


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


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

            print("📂 JSON response saved in 'llm_reviewer.response.code_review.json'")
            return array_obj

        except json.JSONDecodeError as e:
            print("❌ JSON Decode error:", e)

    else:
        print("❌ No JSON found")

    return None
