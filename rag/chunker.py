def split_text_recursive(text: str, chunk_size: int = 800, chunk_overlap: int = 150) -> list[str]:
    """
    Recursively splits text into chunks of specified size and overlap.
    Uses separators in order: double newlines, single newlines, sentences, spaces.
    """
    if not text or len(text) <= chunk_size:
        return [text] if text else []

    separators = ["\n\n", "\n", ". ", " "]
    chunks = []
    
    # Simple sliding window chunker with separator awareness
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        
        if end < text_len:
            # Try to find a natural break near the end
            best_break = -1
            search_window = text[start:end]
            
            for sep in separators:
                pos = search_window.rfind(sep)
                if pos != -1 and pos > (chunk_size // 3):  # Avoid splitting too early
                    best_break = start + pos + len(sep)
                    break
            
            if best_break != -1:
                end = best_break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start pointer forward accounting for overlap
        if end >= text_len:
            break
        
        start = max(start + 1, end - chunk_overlap)

    return chunks

def chunk_page_blocks(page_blocks: list[dict], chunk_size: int = 800, chunk_overlap: int = 150) -> list[dict]:
    """
    Takes page blocks from parser and chunks text while maintaining chunk_index and page numbers.
    Input: [{'text': '...', 'page': 1}]
    Output: [{'text': '...', 'chunk_index': 0, 'page': 1}]
    """
    all_chunks = []
    global_chunk_index = 0

    for block in page_blocks:
        page_num = block.get('page')
        raw_text = block.get('text', '')

        if not raw_text:
            continue

        text_chunks = split_text_recursive(raw_text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        for chunk_text in text_chunks:
            all_chunks.append({
                'text': chunk_text,
                'chunk_index': global_chunk_index,
                'page': page_num
            })
            global_chunk_index += 1

    return all_chunks
