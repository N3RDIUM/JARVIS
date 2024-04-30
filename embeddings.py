import ollama
from chromadb import Documents, EmbeddingFunction, Embeddings

def embed(text):
    embedding = ollama.embeddings(model='llama3', prompt=text)['embedding']
    return embedding

class OllamaEmbeddings(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        return [embed(doc) for doc in input]
	