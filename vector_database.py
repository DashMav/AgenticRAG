import os
import openai
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import Pinecone
from pinecone import Pinecone as PineconeClient
from typing import Optional

load_dotenv()
openai.api_key = os.environ.get('OPENAI_API_KEY')
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
PINECONE_INDEX_NAME = os.environ.get('PINECONE_INDEX_NAME', 'rag-ai-agent')

# Global variable for vector database
_vector_db = None

def get_vector_db():
    """
    Returns the global vector database instance.
    """
    global _vector_db
    if _vector_db is None:
        if PINECONE_API_KEY:
            pinecone = PineconeClient(api_key=PINECONE_API_KEY)
            if PINECONE_INDEX_NAME in pinecone.list_indexes().names():
                _vector_db = Pinecone.from_existing_index(
                    index_name=PINECONE_INDEX_NAME,
                    embedding=OpenAIEmbeddings()
                )
                print(f"Loaded existing Pinecone index '{PINECONE_INDEX_NAME}'")
            else:
                print(f"Pinecone index '{PINECONE_INDEX_NAME}' not found. Please create it first.")
        else:
            print("PINECONE_API_KEY not found in environment variables.")
    return _vector_db

def save_to_pinecone(chunks, overwrite=False):
    """
    Save documents to Pinecone DB
    Args:
        chunks: Document chunks to save
        overwrite: Whether to overwrite existing index (not supported by Pinecone in this way, handled by deleting and recreating)
    """
    global _vector_db
    
    if not PINECONE_API_KEY:
        raise ValueError("PINECONE_API_KEY is not set.")

    pinecone = PineconeClient(api_key=PINECONE_API_KEY)

    if overwrite and PINECONE_INDEX_NAME in pinecone.list_indexes().names():
        pinecone.delete_index(PINECONE_INDEX_NAME)
        print(f"Deleted existing Pinecone index '{PINECONE_INDEX_NAME}'")
        _vector_db = None

    if PINECONE_INDEX_NAME not in pinecone.list_indexes().names():
        pinecone.create_index(name=PINECONE_INDEX_NAME, dimension=1536) # OpenAI embeddings are 1536 dimensional
        print(f"Created new Pinecone index '{PINECONE_INDEX_NAME}'")

    _vector_db = Pinecone.from_documents(
        documents=chunks,
        embedding=OpenAIEmbeddings(),
        index_name=PINECONE_INDEX_NAME
    )
    print(f"Added {len(chunks)} chunks to Pinecone index '{PINECONE_INDEX_NAME}'.")
    
    return _vector_db

def query_data(query_text: str, similarity_threshold: float = 0.7, k: int = 3):    
    vector_db = get_vector_db()
    
    if vector_db is None:
        print("No vector database available. Please create one first.")
        return []
    
    results = vector_db.similarity_search_with_relevance_scores(query=query_text, k=k)
    if len(results) == 0 or results[0][1] < similarity_threshold:
        print(f"Unable to find matching results.")
        return []
    results = sorted(results, key=lambda x: x[1], reverse=True)[:k]
    return results

def close_vector_db():
    """
    Close the vector database and release resources
    """
    global _vector_db
    if _vector_db is not None:
        _vector_db = None
        print("Vector database connection closed.")
        
# ----------------------------
# File upload and processing
def load_documents(files_paths:list):
    """
    load files"""
    documents = []
    for file_path in files_paths:
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith('.md'):
            loader = UnstructuredMarkdownLoader(file_path)
        elif file_path.endswith('.txt'):
            try:
                loader = TextLoader(file_path, encoding='utf-8')
                documents.extend(loader.load())
            except UnicodeDecodeError:
                try:
                    loader = TextLoader(file_path, encoding='latin-1')
                    documents.extend(loader.load())
                except Exception as e:
                    print(f"Error loading {file_path}: {str(e)}")
                    continue
            continue  
        else:
            raise ValueError(f"Unsupported file type: {file_path}")
        
        documents.extend(loader.load())
    
    print(f"Loaded {len(documents)} documents from {len(files_paths)} files.")
    return documents

def text_spliter(documents):
    """
    split documents to chunks"""
    text_spliter=RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True
    )
    chunks=text_spliter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks

def process_files(files_paths=None, overwrite=False):
    """
    Process files and save to vector database
    """
    try:
        if files_paths:
            documents = load_documents(files_paths)
        else:
            raise ValueError("Either files_path or directory_path must be provided.")
        
        chunks = text_spliter(documents)
        
        save_to_pinecone(chunks, overwrite=overwrite)
    except Exception as e:
        print(f"Error processing files: {e}")
        return False, str(e)
    return True, "Files processed and saved to vector database successfully."
    
get_vector_db()
