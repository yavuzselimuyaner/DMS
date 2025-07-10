#!/usr/bin/env python3
"""
Test script for document hierarchy access
"""

from app import app, Document, DocumentType, User, get_accessible_document_types
from flask import session
import sys

def test_user_access(username, role):
    """Test document access for a specific user role"""
    print(f"\n=== {username.upper()} ({role}) TESLERİ ===")
    
    with app.test_request_context():
        # Simulate login
        session['username'] = username
        session['role'] = role
        
        # Get accessible document types
        accessible_types = get_accessible_document_types()
        print(f"Erişebilir doküman tipleri: {[dt.name for dt in accessible_types]}")
        
        # Get accessible type IDs
        accessible_type_ids = [dt.id for dt in accessible_types]
        
        # Query documents with hierarchy filter
        if accessible_type_ids:
            documents = Document.query.filter(
                Document.document_type_id.in_(accessible_type_ids)
            ).all()
        else:
            documents = []
        
        print(f"Görülebilir doküman sayısı: {len(documents)}")
        
        # Show document distribution by type
        type_count = {}
        for doc in documents:
            doc_type = DocumentType.query.get(doc.document_type_id)
            type_name = doc_type.name if doc_type else 'Tip Yok'
            type_count[type_name] = type_count.get(type_name, 0) + 1
        
        for type_name, count in type_count.items():
            print(f"  - {type_name}: {count} doküman")

def main():
    with app.app_context():
        print("🔒 HİYERAŞIK ERİŞİM SİSTEMİ TEST EDİLİYOR...")
        
        # Test all user roles
        test_user_access('admin', 'admin')
        test_user_access('yavuz', 'user')
        test_user_access('kullanici1', 'user')
        test_user_access('calisan1', 'calisan')
        
        print("\n📊 VERİTABANI DURUM ÖZETİ:")
        
        # Show document type distribution
        doc_types = DocumentType.query.all()
        for doc_type in doc_types:
            count = Document.query.filter_by(document_type_id=doc_type.id).count()
            print(f"  - {doc_type.name}: {count} doküman")
        
        # Show users
        print("\n👥 KULLANICILAR:")
        users = User.query.all()
        for user in users:
            print(f"  - {user.username}: {user.role}")

if __name__ == '__main__':
    main()
