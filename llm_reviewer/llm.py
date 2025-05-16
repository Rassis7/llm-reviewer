from langchain_ollama import ChatOllama
from enum import Enum
from langchain_core.prompts import ChatPromptTemplate
import os
import importlib.resources as importlib

# from langchain_openai import ChatOpenAI


class AcceptableLLMModels(Enum):
    CODE_MODEL = os.environ["CODE_MODEL"]
    CONVERSATION_MODEL = os.environ["GEMMA_MODEL"]


class PromptTemplate(Enum):
    CONTEXT = "context.md"
    RESPONSE = "response.md"


PROMPT_PATH = "llm_reviewer.prompts"


class LLM:
    def __init__(self, model: AcceptableLLMModels):
        self.__llm_model = model
        self.model = None
        self.__load()

    def __load(self):
        self.model = ChatOllama(
            model=self.__llm_model.value,
            base_url=os.environ["OLLAMA_API_URL"],
            temperature=0.3,
        )
        # self.model = ChatOpenAI(
        #     model="gpt-4o-mini",
        #     temperature=0,
        #     max_completion_tokens=700,
        #     timeout=None,
        #     max_retries=2,
        #     api_key=os.environ["OPENAI_API_KEY"],
        # )

    @staticmethod
    def load_prompt(prompt: PromptTemplate):
        with importlib.open_text(PROMPT_PATH, prompt.value) as prompt_template:
            file = prompt_template.read()

        return ChatPromptTemplate.from_template(file)
