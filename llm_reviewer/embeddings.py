from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_ollama import embeddings as OllamaEmbeddings


class AcceptableEmbeddings:
    HUGGING_FACE = "HUGGING_FACE"
    OPEN_AI = "OPEN_AI"
    OLLAMA = "OLLAMA"


class Embedding:
    embedding = None

    def __init__(self, embedding: AcceptableEmbeddings):
        self.__load(embedding)

    def __load_hugging_face(self):
        self.embedding = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )

    def __load_open_ai(self):
        self.embedding = OpenAIEmbeddings(model="text-embedding-3-small")

    def __load_ollama(self):
        self.embedding = OllamaEmbeddings.OllamaEmbeddings(model="ollama3")

    def __load(self, embedding: AcceptableEmbeddings):
        if embedding == AcceptableEmbeddings.HUGGING_FACE:
            self.__load_hugging_face()
        elif embedding == AcceptableEmbeddings.OPEN_AI:
            self.__load_open_ai()
        elif embedding == AcceptableEmbeddings.OLLAMA:
            self.__load_ollama()
        else:
            print("No embedding loaded")
            return None
