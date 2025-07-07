from flask import Flask, request, redirect, url_for, render_template, flash, send_from_directory, session
import os
from werkzeug.utils import secure_filename
import json

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
METADATA_FILE = 'uploads/metadata.json'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'

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
    metadata = load_metadata()
    query = request.args.get('q', '').lower()
    sort_by = request.args.get('sort', 'name')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    all_files = os.listdir(app.config['UPLOAD_FOLDER'])
    # Filter by keyword
    if query:
        files = [f for f in all_files if query in f.lower()]
    else:
        files = all_files
    # Filter by date interval
    from_dt = None
    to_dt = None
    import datetime
    if date_from:
        from_dt = datetime.datetime.strptime(date_from, '%Y-%m-%d')
    if date_to:
        to_dt = datetime.datetime.strptime(date_to, '%Y-%m-%d')
        to_dt = to_dt.replace(hour=23, minute=59, second=59)
    if from_dt or to_dt:
        filtered = []
        for f in files:
            fpath = os.path.join(app.config['UPLOAD_FOLDER'], f)
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(fpath))
            if from_dt and mtime < from_dt:
                continue
            if to_dt and mtime > to_dt:
                continue
            filtered.append(f)
        files = filtered
    # Sort files
    if sort_by == 'date':
        files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], f)), reverse=True)
    else:
        files = sorted(files, key=lambda f: f.lower())
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        explanation = request.form.get('explanation', '').strip()
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Save uploader info and explanation
            metadata[filename] = {'uploaded_by': session['username']}
            if explanation:
                metadata[filename]['explanation'] = explanation
            save_metadata(metadata)
            flash('File successfully uploaded')
            return redirect(url_for('upload_file'))
        else:
            flash('File type not allowed')
            return redirect(request.url)
    return render_template('index.html', files=files, sort_by=sort_by, query=query, date_from=date_from, date_to=date_to, is_admin=is_admin(), metadata=metadata)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    if not is_admin():
        flash('Unauthorized')
        return redirect(url_for('upload_file'))
    fpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    metadata = load_metadata()
    if os.path.exists(fpath):
        os.remove(fpath)
        # Save deleter info
        if filename in metadata:
            metadata[filename]['deleted_by'] = session['username']
        else:
            metadata[filename] = {'deleted_by': session['username']}
        save_metadata(metadata)
        flash('File deleted')
    else:
        flash('File not found')
    return redirect(url_for('upload_file'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/preview/<filename>')
def preview_file(filename):
    if not is_logged_in():
        return redirect(url_for('login'))
    ext = os.path.splitext(filename)[1].lower()
    fpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(fpath):
        flash('File not found')
        return redirect(url_for('upload_file'))
    if ext == '.pdf':
        return render_template('preview_pdf.html', filename=filename)
    elif ext == '.txt':
        with open(fpath, encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return render_template('preview_txt.html', filename=filename, content=content)
    elif ext == '.docx':
        try:
            from docx import Document
            doc = Document(fpath)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            content = '\n'.join(paragraphs)
        except Exception as e:
            content = f'Error reading DOCX: {e}'
        return render_template('preview_docx.html', filename=filename, content=content)
    else:
        flash('Preview not supported for this file type.')
        return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(debug=True)
