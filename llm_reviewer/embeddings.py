from langchain_huggingface import HuggingFaceEmbeddings


class Embeddings:

    @staticmethod
    def load():
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
        return embeddings
