from langchain_ollama import ChatOllama
from enum import Enum
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os


class AcceptableLLMModels(Enum):
    LLAMA = "llama3.2:1b"
    GPT4 = "gpt-4o"
    GPT_MINI = "gpt-4o-mini"


class LLM:
    def __init__(self, model: AcceptableLLMModels):
        self.__llm_model = model
        self.model = None
        self.__load()

    def __load_llama(self):
        self.model = ChatOllama(
            temperature=0,
            model=self.__llm_model.value,
            base_url=os.environ["OLLAMA_API_URL"],
        )

    def __load_gpt(self):
        self.model = ChatOpenAI(
            model=self.__llm_model.value,
            temperature=0,
            max_completion_tokens=700,
            timeout=None,
            max_retries=2,
            api_key=os.environ["OPENAI_API_KEY"],
        )

    def __load(self):
        if self.__llm_model == AcceptableLLMModels.LLAMA:
            return self.__load_llama()
        if (
            self.__llm_model == AcceptableLLMModels.GPT4
            or self.__llm_model == AcceptableLLMModels.GPT_MINI
        ):
            return self.__load_gpt()
        else:
            print("No llm model loaded")
