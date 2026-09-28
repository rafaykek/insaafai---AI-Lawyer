import os
from config import Config

SYSTEM_PROMPT = """You are Asad, the AI Legal Consultant for InsaafAI.

Answer using the provided case information and retrieved source material.

Do not invent facts.

If the retrieved context does not contain enough information, clearly say that the available information is insufficient.

Distinguish between:
- information from customer documents
- information from the legal knowledge base
- uncertainty

Do not make unsupported legal claims."""

def format_sources(retrieved_chunks: list[dict]) -> list[str]:
    """Formats unique source citations using actual retrieved chunk metadata."""
    sources = []
    seen = set()
    for chunk in retrieved_chunks:
        filename = chunk.get('filename', 'Document')
        page = chunk.get('page')
        page_str = f"Page {page}" if page is not None else "Document"
        citation = f"Doc: {filename} — {page_str}"
        if citation not in seen:
            seen.add(citation)
            sources.append(citation)
    return sources

def generate_answer(question: str, retrieved_chunks: list[dict], case_context: dict, chat_history: list = None) -> dict:
    """
    Grounded response generation for Asad using retrieved chunks and Groq Cloud / Gemini LLM.
    Returns dict: {'answer': str, 'sources': list[str]}
    """
    # 1. No-Context Check: If no chunks retrieved, avoid hallucination
    if not retrieved_chunks:
        return {
            'answer': "I don't have enough information in the documents currently available for this case to answer that reliably.",
            'sources': []
        }

    sources = format_sources(retrieved_chunks)

    # 2. Format Context Blocks
    case_info_str = (
        f"Customer: {case_context.get('customer_name', 'Client')}\n"
        f"Location: {case_context.get('location', 'N/A')}\n"
        f"Jurisdiction: {case_context.get('jurisdiction', 'N/A')}\n"
        f"Consultancy Type: {case_context.get('consultancy_type', 'N/A')}\n"
        f"Problem Description: {case_context.get('problem_description', 'N/A')}"
    )

    history_str = ""
    if chat_history:
        recent = chat_history[-5:]
        history_lines = [f"{msg.get('role', 'user').capitalize()}: {msg.get('content', '')}" for msg in recent]
        history_str = "\n".join(history_lines)

    retrieved_context_blocks = []
    for idx, chunk in enumerate(retrieved_chunks, 1):
        page_info = f"Page {chunk.get('page')}" if chunk.get('page') is not None else "No Page"
        retrieved_context_blocks.append(
            f"[Source {idx}: {chunk.get('filename')} ({page_info})]\n{chunk.get('text')}"
        )
    context_str = "\n\n".join(retrieved_context_blocks)

    user_prompt_content = (
        f"CUSTOMER CASE CONTEXT:\n{case_info_str}\n\n"
        f"RECENT CONVERSATION HISTORY:\n{history_str if history_str else 'None'}\n\n"
        f"RETRIEVED CASE DOCUMENTS CONTEXT:\n{context_str}\n\n"
        f"CUSTOMER QUESTION:\n{question}"
    )

    # 3. LLM Invocation: Priority 1 - Groq Cloud API
    groq_api_key = Config.GROQ_API_KEY
    groq_model = Config.GROQ_MODEL or 'openai/gpt-oss-120b'

    if groq_api_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_api_key)
            completion = client.chat.completions.create(
                model=groq_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt_content}
                ],
                temperature=0.2,
                max_completion_tokens=1024
            )
            if completion and completion.choices and completion.choices[0].message.content:
                answer_text = completion.choices[0].message.content.strip()
                if sources and "Sources:" not in answer_text and "Doc:" not in answer_text:
                    sources_formatted = "\n".join(sources)
                    answer_text += f"\n\n**Sources:**\n{sources_formatted}"
                return {'answer': answer_text, 'sources': sources}
        except Exception as e:
            print(f"[Warning] Groq API call failed: {e}")

    # Priority 2: Google GenAI API Fallback
    genai_api_key = os.environ.get('GEMINI_API_KEY') or Config.LLM_API_KEY
    if genai_api_key and not genai_api_key.startswith('gsk_'):
        try:
            from google import genai
            client = genai.Client(api_key=genai_api_key)
            full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt_content}\n\nAsad Response:"
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=full_prompt
            )
            if response and response.text:
                answer_text = response.text.strip()
                if sources and "Sources:" not in answer_text:
                    sources_formatted = "\n".join(sources)
                    answer_text += f"\n\n**Sources:**\n{sources_formatted}"
                return {'answer': answer_text, 'sources': sources}
        except Exception as e:
            print(f"[Warning] Gemini API call failed: {e}")

    # Priority 3: Grounded Synthesis Fallback
    synthesis_lines = [
        f"Based on your case documents ({', '.join([c.get('filename') for c in retrieved_chunks[:2]])}):\n"
    ]
    for chunk in retrieved_chunks[:3]:
        page_tag = f"(Page {chunk.get('page')})" if chunk.get('page') is not None else ""
        synthesis_lines.append(f"• According to {chunk.get('filename')} {page_tag}:\n  \"{chunk.get('text')[:250]}...\"\n")

    synthesis_lines.append(
        "I recommend reviewing these specific clauses with legal counsel for detailed enforcement."
    )
    
    answer_text = "\n".join(synthesis_lines)
    if sources:
        sources_formatted = "\n".join(sources)
        answer_text += f"\n\n**Sources:**\n{sources_formatted}"

    return {
        'answer': answer_text,
        'sources': sources
    }
