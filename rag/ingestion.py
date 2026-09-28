from models import db, Document, Case, Chunk
from rag.parser import extract_text
from rag.chunker import chunk_page_blocks

def ingest_document(document: Document, chunk_size: int = 800, chunk_overlap: int = 150) -> list[Chunk]:
    """
    Ingests a Document record:
    1. Extracts text from file path
    2. Cleans & chunks text
    3. Deletes existing chunks for re-ingestion safety
    4. Creates and persists Chunk records with metadata in database
    """
    if not document or not document.filepath:
        raise ValueError("Invalid Document record provided for ingestion")

    # Fetch associated Case to ensure case_id context is present
    case = Case.query.get(document.case_id)
    if not case:
        raise ValueError(f"No associated Case found for document ID {document.id}")

    # 1. Parse and extract text (page-preserved if PDF)
    page_blocks = extract_text(document.filepath)

    # 2. Chunk text with metadata tracking
    chunks_data = chunk_page_blocks(page_blocks, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    # 3. Re-ingestion Safety: Remove any old chunks for this document
    Chunk.query.filter_by(document_id=document.id).delete()

    # 4. Create and store Chunk database records
    created_chunks = []
    for data in chunks_data:
        chunk_rec = Chunk(
            case_id=case.id,
            document_id=document.id,
            filename=document.filename,
            document_type=document.document_type,
            chunk_index=data['chunk_index'],
            page=data['page'],
            text=data['text']
        )
        db.session.add(chunk_rec)
        created_chunks.append(chunk_rec)

    db.session.commit()
    return created_chunks
