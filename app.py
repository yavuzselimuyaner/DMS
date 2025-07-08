from flask import Flask, request, redirect, url_for, render_template, flash, send_file, session
import os
from werkzeug.utils import secure_filename
import json
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
import datetime

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
METADATA_FILE = 'uploads/metadata.json'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:yavuz@localhost:3306/dms2'
db = SQLAlchemy(app)
# Simple user system (for demo)
USERS = {
    'admin': {'password': 'adminpass', 'role': 'admin'},
    'user': {'password': 'userpass', 'role': 'user'}
}

def is_admin():
    return session.get('role') == 'admin'

def is_logged_in():
    return 'username' in session

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_metadata(metadata):
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = USERS.get(username)
        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            flash('Login successful!')
            return redirect(url_for('upload_file'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.')
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if not is_logged_in():
        return redirect(url_for('login'))
    query = request.args.get('q', '').lower()
    sort_by = request.args.get('sort', 'name')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    page = request.args.get('page', 1, type=int)
    per_page = 9
    documents = Document.query
    if query:
        documents = documents.filter(Document.title.ilike(f'%{query}%'))
    if date_from:
        from_dt = datetime.datetime.strptime(date_from, '%Y-%m-%d')
        documents = documents.filter(Document.upload_date >= from_dt)
    if date_to:
        to_dt = datetime.datetime.strptime(date_to, '%Y-%m-%d')
        to_dt = to_dt.replace(hour=23, minute=59, second=59)
        documents = documents.filter(Document.upload_date <= to_dt)
    if sort_by == 'date':
        documents = documents.order_by(Document.upload_date.desc())
    else:
        documents = documents.order_by(Document.title.asc())
    documents = documents.all()
    # Pagination
    total = len(documents)
    page_count = (total // per_page) + (1 if total % per_page else 0)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_documents = documents[start:end]
    if request.method == 'POST':
        files = request.files.getlist('file')
        explanation = request.form.get('explanation', '').strip()
        if not files or files[0].filename == '':
            flash('No selected file')
            return redirect(request.url)
        user = None
        if 'username' in session:
            user = db.session.query(User).filter_by(username=session['username']).first()
        uploaded_count = 0
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_data = file.read()
                doc = Document(
                    title=filename,
                    description=explanation,
                    upload_date=datetime.datetime.now(),
                    file_path='',
                    uploaded_by=user.id if user else None,
                    document_type_id=None,
                    access_level='private',
                    file_data=file_data
                )
                db.session.add(doc)
                uploaded_count += 1
        if uploaded_count > 0:
            db.session.commit()
            flash(f'{uploaded_count} file(s) successfully uploaded')
        else:
            flash('No valid files uploaded')
        return redirect(url_for('upload_file'))
    # TXT dosyaları için önizleme (ilk 3 satır)
    previews = {}
    for doc in documents:
        ext = os.path.splitext(doc.title)[1].lower()
        if ext == '.txt' and doc.file_data:
            try:
                content = doc.file_data.decode('utf-8', errors='ignore')
                previews[doc.id] = '\n'.join(content.splitlines()[:3])
            except Exception:
                previews[doc.id] = ''
        else:
            previews[doc.id] = ''
    return render_template('index.html', documents=documents, paginated_documents=paginated_documents, sort_by=sort_by, query=query, date_from=date_from, date_to=date_to, is_admin=is_admin(), previews=previews, page=page, per_page=per_page, page_count=page_count, total=total)

@app.route('/delete/<int:doc_id>', methods=['POST'])
def delete_file(doc_id):
    if not is_admin():
        flash('Unauthorized')
        return redirect(url_for('upload_file'))
    doc = Document.query.get(doc_id)
    if doc:
        db.session.delete(doc)
        db.session.commit()
        flash('File deleted')
    else:
        flash('File not found')
    return redirect(url_for('upload_file'))

@app.route('/download/<int:doc_id>')
def download_file(doc_id):
    doc = Document.query.get(doc_id)
    if not doc or not doc.file_data:
        flash('File not found')
        return redirect(url_for('upload_file'))
    # PDF önizleme için as_attachment parametresi kontrolü
    preview = request.args.get('preview', '0') == '1'
    return send_file(BytesIO(doc.file_data), download_name=doc.title, as_attachment=not preview)

@app.route('/preview/<int:doc_id>')
def preview_file(doc_id):
    if not is_logged_in():
        return redirect(url_for('login'))
    doc = Document.query.get(doc_id)
    if not doc or not doc.file_data:
        flash('File not found')
        return redirect(url_for('upload_file'))
    ext = os.path.splitext(doc.title)[1].lower()
    if ext == '.pdf':
        return render_template('preview_pdf.html', filename=doc.title, doc_id=doc.id)
    elif ext == '.txt':
        content = doc.file_data.decode('utf-8', errors='ignore')
        return render_template('preview_txt.html', filename=doc.title, content=content, doc_id=doc.id)
    elif ext == '.docx':
        try:
            from docx import Document as DocxDocument
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
                tmp.write(doc.file_data)
                tmp_path = tmp.name
            docx_doc = DocxDocument(tmp_path)
            paragraphs = [p.text for p in docx_doc.paragraphs if p.text.strip()]
            content = '\n'.join(paragraphs)
            os.remove(tmp_path)
        except Exception as e:
            content = f'Error reading DOCX: {e}'
        return render_template('preview_docx.html', filename=doc.title, content=content, doc_id=doc.id)
    else:
        flash('Preview not supported for this file type.')
        return redirect(url_for('upload_file'))

# SQLAlchemy Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime)

class DocumentType(db.Model):
    __tablename__ = 'document_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    upload_date = db.Column(db.DateTime)
    file_path = db.Column(db.Text, nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    document_type_id = db.Column(db.Integer, db.ForeignKey('document_types.id'))
    access_level = db.Column(db.String(20), default='private')
    file_data = db.Column(db.LargeBinary)  # <-- YENİ: Dosya verisi (BLOB)

class Permission(db.Model):
    __tablename__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'))
    can_view = db.Column(db.Boolean, default=True)
    can_edit = db.Column(db.Boolean, default=False)
    can_delete = db.Column(db.Boolean, default=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'document_id'),)

if __name__ == '__main__':
    app.run(debug=True)
