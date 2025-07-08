from flask import Flask, request, jsonify, send_file
from models import db, Document
from io import BytesIO
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/dms_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Dosya yükle
@app.route('/api/documents', methods=['POST'])
def upload_document():
    file = request.files.get('file')
    explanation = request.form.get('explanation', '')
    uploaded_by = request.form.get('uploaded_by', 'unknown')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    filename = file.filename
    if Document.query.filter_by(filename=filename).first():
        return jsonify({'error': 'File already exists'}), 409
    doc = Document(
        filename=filename,
        data=file.read(),
        mimetype=file.mimetype,
        uploaded_by=uploaded_by,
        explanation=explanation
    )
    db.session.add(doc)
    db.session.commit()
    return jsonify({'message': 'File uploaded'}), 201

# Dosya listele/ara
@app.route('/api/documents', methods=['GET'])
def list_documents():
    query = request.args.get('q', '')
    docs = Document.query
    if query:
        docs = docs.filter(Document.filename.ilike(f'%{query}%'))
    docs = docs.all()
    return jsonify([{
        'filename': d.filename,
        'uploaded_by': d.uploaded_by,
        'explanation': d.explanation,
        'upload_time': d.upload_time
    } for d in docs])

# Dosya indir/önizle
@app.route('/api/documents/<filename>', methods=['GET'])
def get_document(filename):
    doc = Document.query.filter_by(filename=filename).first()
    if not doc:
        return jsonify({'error': 'File not found'}), 404
    return send_file(BytesIO(doc.data), download_name=doc.filename, mimetype=doc.mimetype)

# Dosya sil
@app.route('/api/documents/<filename>', methods=['DELETE'])
def delete_document(filename):
    doc = Document.query.filter_by(filename=filename).first()
    if not doc:
        return jsonify({'error': 'File not found'}), 404
    db.session.delete(doc)
    db.session.commit()
    return jsonify({'message': 'File deleted'})

if __name__ == '__main__':
    app.run(debug=True)
