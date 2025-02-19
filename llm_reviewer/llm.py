from langchain_ollama import ChatOllama
from enum import Enum
from langchain_core.prompts import ChatPromptTemplate
import os
import importlib.resources as importlib


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
            # temperature=float(os.environ["TEMPERATURE"] or 0.5),
            # max_tokens=int(os.environ["MAX_TOKENS"] or 100),
            # top_p=float(os.environ["TOP_P"] or 0.9),
            # top_k=int(os.environ["TOP_K"] or 50),
            # presence_penalty=float(os.environ["PRESENCE_PENALTY"] or 0.0),
            # frequency_penalty=float(os.environ["FREQUENCY_PENALTY"] or 0.0),
        )

    @staticmethod
    def load_prompt(prompt: PromptTemplate):
        with importlib.open_text(PROMPT_PATH, prompt.value) as prompt_template:
            file = prompt_template.read()

        return ChatPromptTemplate.from_template(file)
