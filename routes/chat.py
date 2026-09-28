from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models import db, Case, Message
from rag import retrieve, generate_answer

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat/<case_id>', methods=['GET'])
def chat_view(case_id):
    """Render consultation chat interface for specific case ID."""
    case = Case.query.filter_by(case_id=case_id).first_or_404()
    messages = Message.query.filter_by(case_id=case.id).order_by(Message.created_at.asc()).all()
    return render_template('chat.html', case=case, messages=messages)

@chat_bp.route('/chat/<case_id>/message', methods=['POST'])
def send_message(case_id):
    """Handle incoming chat message via RAG hybrid retrieval & grounded generation."""
    case = Case.query.filter_by(case_id=case_id).first_or_404()

    # Support both JSON payload and standard form data
    if request.is_json:
        data = request.get_json() or {}
        user_content = data.get('content', '').strip()
    else:
        user_content = request.form.get('content', '').strip()

    if not user_content:
        if request.is_json:
            return jsonify({'error': 'Message content cannot be empty'}), 400
        flash('Message content cannot be empty', 'error')
        return redirect(url_for('chat.chat_view', case_id=case_id))

    # 1. Save User Message
    user_msg = Message(
        case_id=case.id,
        role='user',
        content=user_content
    )
    db.session.add(user_msg)
    db.session.flush()

    # 2. Fetch Recent Conversation History (Last 5 messages)
    history_records = Message.query.filter_by(case_id=case.id).order_by(Message.created_at.asc()).all()
    history_dicts = [{'role': m.role, 'content': m.content} for m in history_records]

    # 3. Case-Isolated Hybrid Retrieval (BM25 + Dense FAISS + RRF)
    retrieved_chunks = retrieve(query=user_content, case_id=case.id, top_k=5)

    # 4. Formulate Case Context
    case_context = {
        'customer_name': case.customer.name,
        'location': case.customer.location,
        'jurisdiction': case.customer.jurisdiction,
        'consultancy_type': case.consultancy_type,
        'problem_description': case.problem_description
    }

    # 5. Grounded Asad Answer Generation
    rag_result = generate_answer(
        question=user_content,
        retrieved_chunks=retrieved_chunks,
        case_context=case_context,
        chat_history=history_dicts
    )
    assistant_content = rag_result['answer']

    # 6. Save Assistant Response Message
    assistant_msg = Message(
        case_id=case.id,
        role='assistant',
        content=assistant_content
    )
    db.session.add(assistant_msg)
    db.session.commit()

    if request.is_json:
        return jsonify({
            'status': 'success',
            'user_message': user_msg.to_dict(),
            'assistant_message': assistant_msg.to_dict(),
            'sources': rag_result.get('sources', [])
        })

    return redirect(url_for('chat.chat_view', case_id=case_id))
