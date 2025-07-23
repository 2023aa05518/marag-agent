from langchain_community.embeddings import HuggingFaceEmbeddings
from ragas.embeddings import LangchainEmbeddingsWrapper

embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
ragas_embeddings = LangchainEmbeddingsWrapper(embeddings)

print('HuggingFace embeddings initialized successfully')
print(f'Embedding dimension: {len(embeddings.embed_query("test"))}')
