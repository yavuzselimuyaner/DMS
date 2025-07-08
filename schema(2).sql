
-- Kullanıcılar tablosu
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) CHECK (role IN ('admin', 'user')) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL UNIQUE,
    data BYTEA NOT NULL,
    mimetype VARCHAR(128) NOT NULL,
    uploaded_by VARCHAR(64) NOT NULL,
    explanation TEXT,
    deleted_by VARCHAR(64),
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Belge türleri tablosu
CREATE TABLE document_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);



-- Belge erişim izinleri tablosu (en son oluşturulmalı)
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    document_id INT REFERENCES documents(id) ON DELETE CASCADE,
    can_view BOOLEAN DEFAULT TRUE,
    can_edit BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id, document_id)
);