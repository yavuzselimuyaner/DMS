# DMS (Document Management System)

A modern Flask-based document management system with user authentication, file upload, search, preview, and database storage. Features a responsive Bootstrap UI with document thumbnails and user profile management.

## Features

### Authentication & User Management
- User registration with password hashing (bcrypt)
- Secure login/logout with session management
- User profile page with account statistics
- Password change functionality
- Admin and regular user roles

### Document Management
- Upload multiple files at once (PDF, DOCX, TXT, DOC)
- Document explanations/descriptions
- File storage as BLOBs in MySQL database
- Document thumbnails (PDF first page, TXT preview, DOCX content)
- Full-text search and date filtering
- Pagination for large document collections

### Preview & Download
- In-browser PDF preview
- Text file content preview
- DOCX document preview
- Secure file download with access control

### Modern UI
- Responsive Bootstrap-based interface
- Card/grid layout for documents
- Mobile-friendly design
- Clean, centered login/register forms
- Top navigation with profile access

### Security & Permissions
- Admin-only file deletion with audit trail
- User session management
- Secure file access controls
- Password confirmation on registration

## Prerequisites

Before setting up the DMS, ensure you have the following installed:

1. **Python 3.7+**
2. **MySQL Server** (8.0+ recommended)
3. **pip** (Python package manager)

## Step-by-Step Setup Guide

### 1. Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd DMSprototype

# Or download and extract the ZIP file to DMSprototype folder
```

### 2. Create Python Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install flask
pip install flask-sqlalchemy
pip install mysql-connector-python
pip install werkzeug
pip install python-docx
pip install bcrypt
pip install PyMuPDF
```

Or create a `requirements.txt` file with these contents:
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
mysql-connector-python==8.1.0
Werkzeug==2.3.7
python-docx==0.8.11
bcrypt==4.0.1
PyMuPDF==1.23.5
```

Then install with:
```bash
pip install -r requirements.txt
```

### 4. Set Up MySQL Database

#### 4.1 Create Database
```sql
-- Connect to MySQL as root or admin user
CREATE DATABASE dms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create a dedicated user (optional but recommended)
CREATE USER 'dms_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON dms_db.* TO 'dms_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 4.2 Run Database Schema
```bash
# Navigate to the database folder
cd database

# Import the schema (update connection details as needed)
mysql -u dms_user -p dms_db < schema.sql
```

### 5. Configure Database Connection

Edit the database connection settings in `app.py` (around line 10-15):

```python
# Update these values according to your MySQL setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://dms_user:your_secure_password@localhost/dms_db'
```

### 6. Initialize the Application

```bash
# Make sure you're in the project root directory
cd c:\Users\yavuz\DMSprototype

# Run the Flask application
python app.py
```

### 7. Access the Application

1. Open your web browser
2. Navigate to: `http://localhost:5000`
3. You should see the login page

## Default Login Credentials

The application comes with pre-configured users:

### Admin User
- **Username:** `admin`
- **Password:** `adminpass`
- **Permissions:** Full access (upload, download, delete, user management)

### Regular User
- **Username:** `user` 
- **Password:** `userpass`
- **Permissions:** Upload, download, view documents

## Getting Started

### For New Users:
1. Click "Register" on the login page
2. Fill in your details with password confirmation
3. Login with your new credentials
4. Start uploading and managing documents

### For Admins:
1. Login with admin credentials
2. Access all documents uploaded by any user
3. Delete documents when necessary
4. Monitor user activity through document metadata

## File Upload Guidelines

### Supported File Types:
- **PDF** - Adobe Portable Document Format
- **DOCX** - Microsoft Word Document (newer format)
- **DOC** - Microsoft Word Document (legacy format)  
- **TXT** - Plain Text Files

### Upload Process:
1. Click "Choose Files" button
2. Select one or multiple files
3. Add optional explanations for each file
4. Click "Upload" to save to database

### File Storage:
- Files are stored as BLOBs directly in the MySQL database
- No local file system storage required
- Automatic thumbnail generation for supported formats

## Troubleshooting

### Common Issues:

#### Database Connection Error
```
Error: Can't connect to MySQL server
```
**Solution:** 
- Verify MySQL is running
- Check database credentials in app.py
- Ensure database and user exist

#### Import Error for Dependencies
```
ModuleNotFoundError: No module named 'flask'
```
**Solution:**
- Activate virtual environment
- Install missing packages with pip

#### Port Already in Use
```
OSError: [Errno 48] Address already in use
```
**Solution:**
- Change port in app.py: `app.run(debug=True, port=5001)`
- Or kill the process using port 5000

#### File Upload Issues
```
File size too large or unsupported format
```
**Solution:**
- Check file size limits in app.py
- Verify file format is supported
- Ensure sufficient database storage

### Database Reset:
If you need to reset the database:
```sql
DROP DATABASE dms_db;
CREATE DATABASE dms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- Then re-run schema.sql
```

## Project Structure

```
DMSprototype/
├── app.py                          # Main Flask application
├── README.md                       # This file
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
├── database/
│   └── schema.sql                  # MySQL database schema
├── static/
│   └── style.css                   # CSS styles and responsive design
└── templates/
    ├── index.html                  # Main DMS interface
    ├── login_register.html         # Login page
    ├── register_only.html          # Registration page
    ├── profile.html                # User profile page
    ├── preview_pdf.html            # PDF preview template
    ├── preview_txt.html            # Text preview template
    └── preview_docx.html           # DOCX preview template
```

## Development Notes

### Database Models:
- **User**: User accounts and authentication
- **DocumentType**: File type definitions
- **Document**: File metadata and BLOB storage
- **Permission**: User access controls

### Security Features:
- Password hashing with bcrypt
- Session-based authentication
- CSRF protection considerations
- File type validation
- Access control for file operations

### Performance Considerations:
- Database indexing on search fields
- Pagination for large document sets
- Thumbnail caching
- BLOB storage optimization

## Contributing

When making changes:
1. Test thoroughly with different file types
2. Verify responsive design on mobile devices
3. Check database performance with large files
4. Ensure security measures remain intact

## License

This project is for educational and internal organizational use.

---

**Ready to manage your documents efficiently!**

For technical support or feature requests, please refer to the development team.
