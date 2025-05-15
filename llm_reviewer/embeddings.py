from langchain_openai import OpenAIEmbeddings


class AcceptableEmbeddings:
    OPEN_AI = "OPEN_AI"


class Embedding:
    embedding = None

    def __init__(self, embedding: AcceptableEmbeddings):
        self.__load(embedding)

    def __load_open_ai(self):
        self.embedding = OpenAIEmbeddings(model="text-embedding-3-large")

    def __load(self, embedding: AcceptableEmbeddings):
        if embedding == AcceptableEmbeddings.OPEN_AI:
            self.__load_open_ai()
        else:
            print("No embedding loaded")
            return None
