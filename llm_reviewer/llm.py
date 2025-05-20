from langchain_ollama import ChatOllama
from enum import Enum
from langchain_core.prompts import ChatPromptTemplate
import os
import importlib.resources as importlib
from langchain_openai import ChatOpenAI
from typing import Optional, Union
from pydantic import SecretStr


class AcceptableLLMModels(Enum):
    CODE_MODEL = os.environ["CODE_MODEL"]
    CONVERSATION_MODEL = os.environ["CONVERSATION_MODEL"]


class AcceptableLLMProviders(Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"


class PromptTemplate(Enum):
    CONTEXT = "context.md"
    RESPONSE = "response.md"


PROMPT_PATH = "llm_reviewer.prompts"


class LLM:
    def __init__(
        self,
        model: AcceptableLLMModels,
        provider: AcceptableLLMProviders = AcceptableLLMProviders.OLLAMA,
    ):
        self.__llm_model = model
        self.model: Optional[Union[ChatOllama, ChatOpenAI]] = None
        self.__load(provider)

    def __load(self, provider: AcceptableLLMProviders):
        if provider == AcceptableLLMProviders.OLLAMA:
            self.model = ChatOllama(
                model=self.__llm_model.value,
                base_url=os.environ["API_URL"],
                temperature=0.3,
            )
        elif provider == AcceptableLLMProviders.OPENAI:
            self.model = ChatOpenAI(
                model=self.__llm_model.value,
                base_url=os.environ["API_URL"],
                temperature=0,
                max_completion_tokens=700,
                timeout=None,
                api_key=SecretStr(os.environ["API_KEY"]),
            )

    @staticmethod
    def load_prompt(prompt: PromptTemplate):
        with importlib.open_text(PROMPT_PATH, prompt.value) as prompt_template:
            file = prompt_template.read()

        return ChatPromptTemplate.from_template(file)
