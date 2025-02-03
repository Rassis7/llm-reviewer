from langchain_ollama import ChatOllama, embeddings
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
            model=self.__llm_model.value, base_url=os.environ["OLLAMA_API_URL"]
        )

    def __load_gpt(self):
        self.model = ChatOpenAI(
            model=self.__llm_model.value,
            temperature=0.2,
            max_tokens=500,
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

    @staticmethod
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
