import pytest
from unittest.mock import patch
from langchain.schema import Document
from src.loader.doc_loader import main_pipeline

@patch('src.loader.doc_loader.load_pdf_documents')
def test_main_pipeline(mock_load_pdf_documents):
    """
    Tests the main_pipeline function in doc_loader.py.
    It mocks the load_pdf_documents function to avoid dependency on actual PDF files.
    """
    # 1. Setup mock to return some test documents
    long_text = "This is a long text to test the chunking functionality. " * 50
    mock_docs = [
        Document(page_content="This is a short page.", metadata={"page": 1, "doc_name": "test_doc1"}),
        Document(page_content=long_text, metadata={"page": 2, "doc_name": "test_doc1"}),
        Document(page_content="Another short page.", metadata={"page": 1, "doc_name": "test_doc2"}),
    ]
    mock_load_pdf_documents.return_value = mock_docs

    # 2. Run the pipeline
    doc_collection = main_pipeline()

    # 3. Assertions to check the output
    assert "ids" in doc_collection
    assert "documents" in doc_collection
    assert "metadatas" in doc_collection

    assert len(doc_collection["ids"]) == len(doc_collection["documents"]) == len(doc_collection["metadatas"])
    
    # Check if chunking happened. The number of chunks should be > number of docs.
    assert len(doc_collection["ids"]) > len(mock_docs)

    # Check metadata structure for each chunk
    for metadata in doc_collection["metadatas"]:
        assert "doc_name" in metadata
        assert "page_number" in metadata
        assert "chunk_index" in metadata

    # Check id structure for each chunk
    for i, chunk_id in enumerate(doc_collection["ids"]):
        metadata = doc_collection["metadatas"][i]
        expected_id = f"{metadata['doc_name']}_page{metadata['page_number']}_chunk{metadata['chunk_index']}"
        assert chunk_id == expected_id 