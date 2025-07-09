from flask import Flask, request, redirect, url_for, render_template, flash, send_file, session
import os
from werkzeug.utils import secure_filename
import json
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import base64

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

def generate_thumbnail(file_data, file_ext):
    """Generate thumbnail for different file types"""
    try:
        if file_ext == '.pdf':
            # PDF thumbnail using PyMuPDF (fitz)
            try:
                import fitz  # PyMuPDF
                pdf_document = fitz.open(stream=file_data, filetype="pdf")
                first_page = pdf_document[0]
                pix = first_page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))  # Scale down
                img_data = pix.tobytes("png")
                pdf_document.close()
                return base64.b64encode(img_data).decode('utf-8')
            except ImportError:
                return None
        elif file_ext == '.txt':
            # Text thumbnail - first few lines
            try:
                content = file_data.decode('utf-8', errors='ignore')
                lines = content.splitlines()[:8]  # First 8 lines
                preview_text = '\n'.join(lines)
                return preview_text[:300]  # First 300 chars
            except:
                return None
        elif file_ext in ['.docx', '.doc']:
            # Word document thumbnail - extract first paragraph
            try:
                from docx import Document as DocxDocument
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
                    tmp.write(file_data)
                    tmp_path = tmp.name
                docx_doc = DocxDocument(tmp_path)
                paragraphs = [p.text for p in docx_doc.paragraphs if p.text.strip()]
                preview_text = '\n'.join(paragraphs[:3])  # First 3 paragraphs
                os.remove(tmp_path)
                return preview_text[:300]  # First 300 chars
            except:
                return None
    except Exception:
        return None
    return None

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
        if 'login' in request.form:
            # Giriş işlemi
            username = request.form['username']
            password = request.form['password']
            user = db.session.query(User).filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                session['username'] = user.username
                session['role'] = user.role
                flash('Login successful!')
                return redirect(url_for('upload_file'))
            else:
                flash('Invalid credentials')
        elif 'register' in request.form:
            # Kayıt işlemi
            username = request.form['reg_username'].strip()
            email = request.form['reg_email'].strip()
            password = request.form['reg_password']
            # Kullanıcı adı veya e-posta var mı?
            if db.session.query(User).filter((User.username == username) | (User.email == email)).first():
                flash('Username or email already exists')
            else:
                user = User(
                    username=username,
                    email=email,
                    password_hash=generate_password_hash(password),
                    role='user',
                    created_at=datetime.datetime.now()
                )
                db.session.add(user)
                db.session.commit()
                flash('Account created! You can now log in.')
    return render_template('login_register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user = db.session.query(User).filter_by(username=session['username']).first()
    if not user:
        flash('User not found')
        return redirect(url_for('login'))
    
    # Get user statistics
    user_documents = Document.query.filter_by(uploaded_by=user.id).all()
    total_documents = len(user_documents)
    
    # Calculate total storage used (approximate)
    total_size_bytes = sum(len(doc.file_data) if doc.file_data else 0 for doc in user_documents)
    total_size = f"{total_size_bytes / (1024*1024):.1f} MB" if total_size_bytes > 0 else "0 MB"
    
    # Last upload date
    last_upload = "Never"
    if user_documents:
        latest_doc = max(user_documents, key=lambda x: x.upload_date if x.upload_date else datetime.datetime.min)
        if latest_doc.upload_date:
            last_upload = latest_doc.upload_date.strftime('%B %d, %Y')
    
    user_stats = {
        'total_documents': total_documents,
        'total_size': total_size,
        'last_upload': last_upload
    }
    
    # Admin-specific statistics
    admin_stats = None
    all_documents = []
    all_users = []
    if is_admin():
        # Get all system statistics for admin
        all_documents = Document.query.all()
        all_users = User.query.all()
        total_system_docs = len(all_documents)
        total_system_size_bytes = sum(len(doc.file_data) if doc.file_data else 0 for doc in all_documents)
        total_system_size = f"{total_system_size_bytes / (1024*1024):.1f} MB" if total_system_size_bytes > 0 else "0 MB"
        total_users = len(all_users)
        
        admin_stats = {
            'total_system_documents': total_system_docs,
            'total_system_size': total_system_size,
            'total_users': total_users,
            'recent_uploads': sorted(all_documents, key=lambda x: x.upload_date if x.upload_date else datetime.datetime.min, reverse=True)[:5]
        }
        
        # Create user map for admin view
        user_map = {u.id: u.username for u in all_users}
        user_map[None] = 'System User'
        
        # Add user info to documents for admin view
        for doc in all_documents:
            doc.uploader_name = user_map.get(doc.uploaded_by, 'Unknown User')
    
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Verify current password
        if not check_password_hash(user.password_hash, current_password):
            flash('Current password is incorrect')
            return render_template('profile.html', user=user, user_stats=user_stats, admin_stats=admin_stats, all_documents=all_documents, all_users=all_users, is_admin=is_admin())
        
        # Check if new passwords match
        if new_password != confirm_password:
            flash('New passwords do not match')
            return render_template('profile.html', user=user, user_stats=user_stats, admin_stats=admin_stats, all_documents=all_documents, all_users=all_users, is_admin=is_admin())
        
        # Check password length
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long')
            return render_template('profile.html', user=user, user_stats=user_stats, admin_stats=admin_stats, all_documents=all_documents, all_users=all_users, is_admin=is_admin())
        
        # Update password
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash('Password updated successfully!')
        return render_template('profile.html', user=user, user_stats=user_stats, admin_stats=admin_stats, all_documents=all_documents, all_users=all_users, is_admin=is_admin())
    
    return render_template('profile.html', user=user, user_stats=user_stats, admin_stats=admin_stats, all_documents=all_documents, all_users=all_users, is_admin=is_admin())

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
    user_map = {}
    user_ids = set(doc.uploaded_by for doc in documents if doc.uploaded_by)
    if user_ids:
        users = User.query.filter(User.id.in_(user_ids)).all()
        user_map = {u.id: u.username for u in users}
    
    # Add fallback for documents without uploader
    user_map[None] = 'System User'
    
    # Generate thumbnails for documents
    thumbnails = {}
    for doc in documents:
        ext = os.path.splitext(doc.title)[1].lower()
        if doc.file_data:
            thumbnail = generate_thumbnail(doc.file_data, ext)
            thumbnails[doc.id] = thumbnail
        else:
            thumbnails[doc.id] = None
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
    return render_template('index.html', documents=documents, paginated_documents=paginated_documents, sort_by=sort_by, query=query, date_from=date_from, date_to=date_to, is_admin=is_admin(), previews=previews, page=page, per_page=per_page, page_count=page_count, total=total, user_map=user_map, thumbnails=thumbnails)

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

@app.route('/register_only', methods=['GET', 'POST'])
def register_only():
    if request.method == 'POST':
        username = request.form['reg_username'].strip()
        email = request.form['reg_email'].strip()
        password = request.form['reg_password']
        password2 = request.form['reg_password2']
        if password != password2:
            flash('Passwords do not match!')
            return render_template('register_only.html')
        if db.session.query(User).filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists')
            return render_template('register_only.html')
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='user',
            created_at=datetime.datetime.now()
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.')
        return redirect(url_for('login'))
    return render_template('register_only.html')

@app.route('/init_admin')
def init_admin():
    """Initialize default admin user if not exists"""
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@dms.local',
            password_hash=generate_password_hash('adminpass'),
            role='admin',
            created_at=datetime.datetime.now()
        )
        db.session.add(admin_user)
        db.session.commit()
        return "Admin user created successfully! Username: admin, Password: adminpass"
    else:
        return "Admin user already exists"

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

@app.route('/admin/delete_document/<int:doc_id>', methods=['POST'])
def admin_delete_document(doc_id):
    if not is_admin():
        flash('Unauthorized access')
        return redirect(url_for('profile'))
    
    doc = Document.query.get(doc_id)
    if doc:
        db.session.delete(doc)
        db.session.commit()
        flash(f'Document "{doc.title}" deleted successfully')
    else:
        flash('Document not found')
    
    return redirect(url_for('profile'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def admin_delete_user(user_id):
    if not is_admin():
        flash('Unauthorized access')
        return redirect(url_for('profile'))
    
    # Prevent admin from deleting themselves
    current_user = db.session.query(User).filter_by(username=session['username']).first()
    if current_user and current_user.id == user_id:
        flash('Cannot delete your own account')
        return redirect(url_for('profile'))
    
    user = User.query.get(user_id)
    if user:
        # Delete user's documents first
        user_docs = Document.query.filter_by(uploaded_by=user.id).all()
        for doc in user_docs:
            db.session.delete(doc)
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        flash(f'User "{user.username}" and their documents deleted successfully')
    else:
        flash('User not found')
    
    return redirect(url_for('profile'))

@app.route('/admin/promote_user/<int:user_id>', methods=['POST'])
def admin_promote_user(user_id):
    if not is_admin():
        flash('Unauthorized access')
        return redirect(url_for('profile'))
    
    user = User.query.get(user_id)
    if user:
        if user.role == 'user':
            user.role = 'admin'
            db.session.commit()
            flash(f'User "{user.username}" promoted to admin')
        elif user.role == 'admin':
            user.role = 'user'
            db.session.commit()
            flash(f'User "{user.username}" demoted to regular user')
    else:
        flash('User not found')
    
    return redirect(url_for('profile'))

@app.route('/bulk_download', methods=['POST'])
def bulk_download():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    doc_ids = request.form.getlist('doc_ids')
    if not doc_ids:
        flash('No documents selected for download')
        return redirect(url_for('upload_file'))
    
    # If only one document, download directly
    if len(doc_ids) == 1:
        return redirect(url_for('download_file', doc_id=doc_ids[0]))
    
    # For multiple documents, create a ZIP file
    import zipfile
    import tempfile
    
    # Create a temporary ZIP file
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    
    try:
        with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for doc_id in doc_ids:
                doc = Document.query.get(int(doc_id))
                if doc and doc.file_data:
                    # Add file to ZIP with its original name
                    zipf.writestr(doc.title, doc.file_data)
        
        # Send the ZIP file
        return send_file(
            temp_zip.name,
            download_name=f'documents_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.zip',
            as_attachment=True,
            mimetype='application/zip'
        )
    except Exception as e:
        flash(f'Error creating download: {str(e)}')
        return redirect(url_for('upload_file'))
    finally:
        # Clean up temp file after sending
        try:
            os.unlink(temp_zip.name)
        except:
            pass

@app.route('/bulk_delete', methods=['POST'])
def bulk_delete():
    if not is_admin():
        flash('Unauthorized access')
        return redirect(url_for('upload_file'))
    
    doc_ids = request.form.getlist('doc_ids')
    if not doc_ids:
        flash('No documents selected for deletion')
        return redirect(url_for('upload_file'))
    
    try:
        deleted_count = 0
        for doc_id in doc_ids:
            doc = Document.query.get(int(doc_id))
            if doc:
                db.session.delete(doc)
                deleted_count += 1
        
        db.session.commit()
        flash(f'{deleted_count} document(s) deleted successfully')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting documents: {str(e)}')
    
    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(debug=True)
