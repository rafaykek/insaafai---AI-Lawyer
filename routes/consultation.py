import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from models import db, Customer, Case, Document, Message
from rag import ingest_document

consultation_bp = Blueprint('consultation', __name__)

def allowed_file(filename, allowed_extensions):
    """Check if the uploaded file has a permitted extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_unique_case_id():
    """Ensure generated case ID is unique in database."""
    while True:
        candidate_id = Case.generate_case_id()
        existing = Case.query.filter_by(case_id=candidate_id).first()
        if not existing:
            return candidate_id

def create_initial_asad_welcome(customer_name, location, consultancy_type, problem_description, filenames):
    """Generate dynamic welcome message from Asad using case details."""
    if filenames:
        docs_str = ", including " + ", ".join(filenames)
    else:
        docs_str = "."

    message_text = (
        f"Hello {customer_name}. I understand that you're based in {location} "
        f"and you've contacted us regarding a {consultancy_type.lower()} matter "
        f"involving: '{problem_description}'.\n\n"
        f"I've also received the documents you've provided{docs_str}\n\n"
        f"I can help you analyse the information you've provided and understand "
        f"the relevant aspects of your case.\n\n"
        f"What would you like help with today?"
    )
    return message_text

@consultation_bp.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    """Handle customer onboarding form rendering and submission."""
    if request.method == 'GET':
        return render_template('onboarding.html')

    # Process Form Submission
    name = request.form.get('name', '').strip()
    location = request.form.get('location', '').strip()
    jurisdiction = request.form.get('jurisdiction', '').strip()
    consultancy_type = request.form.get('consultancy_type', '').strip()
    problem_description = request.form.get('problem_description', '').strip()

    # Form Validation
    if not name or not location or not jurisdiction or not consultancy_type or not problem_description:
        flash('Please fill in all required fields.', 'error')
        return render_template('onboarding.html'), 400

    # 1. Create Customer
    customer = Customer(
        name=name,
        location=location,
        jurisdiction=jurisdiction
    )
    db.session.add(customer)
    db.session.flush()  # Obtain customer.id before committing

    # 2. Create Case with Unique Case ID
    case_id_str = generate_unique_case_id()
    case = Case(
        case_id=case_id_str,
        customer_id=customer.id,
        consultancy_type=consultancy_type,
        problem_description=problem_description
    )
    db.session.add(case)
    db.session.flush()  # Obtain case.id

    # 3. Handle Uploaded Documents
    saved_filenames = []
    uploaded_files = request.files.getlist('documents')
    allowed_exts = current_app.config['ALLOWED_EXTENSIONS']
    upload_dir = current_app.config['UPLOAD_FOLDER']

    os.makedirs(upload_dir, exist_ok=True)

    for file in uploaded_files:
        if file and file.filename != '':
            if allowed_file(file.filename, allowed_exts):
                original_filename = secure_filename(file.filename)
                # Store with case_id prefix to prevent name collision in uploads folder
                unique_filename = f"{case_id_str}_{original_filename}"
                file_path = os.path.join(upload_dir, unique_filename)
                file.save(file_path)

                doc = Document(
                    case_id=case.id,
                    filename=original_filename,
                    filepath=file_path,
                    document_type=original_filename.split('.')[-1].lower() if '.' in original_filename else 'unknown'
                )
                db.session.add(doc)
                db.session.flush()  # Obtain doc.id for chunk relationships
                
                # Ingest document into RAG chunking pipeline
                ingest_document(doc)
                
                saved_filenames.append(original_filename)

    # 4. Create Initial Assistant Message (Asad)
    welcome_content = create_initial_asad_welcome(
        customer_name=name,
        location=location,
        consultancy_type=consultancy_type,
        problem_description=problem_description,
        filenames=saved_filenames
    )

    initial_msg = Message(
        case_id=case.id,
        role='assistant',
        content=welcome_content
    )
    db.session.add(initial_msg)

    # Commit all records atomically
    db.session.commit()

    return redirect(url_for('consultation.view_case', case_id=case_id_str))

@consultation_bp.route('/case/<case_id>')
def view_case(case_id):
    """Render case summary page."""
    case = Case.query.filter_by(case_id=case_id).first_or_404()
    return render_template('case.html', case=case)
