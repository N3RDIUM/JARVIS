import chromadb
from embeddings import OllamaEmbeddings

class VectorDB:
	def __init__(self):
		self.client = chromadb.Client()
		self.collection = self.client.create_collection(name="jarvis", embedding_function=OllamaEmbeddings())
  
	def add(self, doc, meta, id):
		self.collection.add(documents=[doc], metadatas=[meta], ids=[id])
  
	def query(self, query):
		return self.collection.query(query_texts=[query], n_results=1)
