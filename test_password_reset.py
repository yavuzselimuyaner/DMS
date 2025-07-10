#!/usr/bin/env python3
"""
Test script for password reset functionality
"""

from app import app, User, db, send_email
import datetime

def test_password_reset():
    """Test password reset functionality"""
    with app.app_context():
        print("🔐 ŞİFRE SIFIRLAMA SİSTEMİ TEST EDİLİYOR...")
        
        # Test user
        user = User.query.filter_by(email='admin@dms.local').first()
        if not user:
            print("❌ Test kullanıcısı bulunamadı")
            return
            
        print(f"✅ Test kullanıcısı: {user.username} ({user.email})")
        
        # Generate reset token
        from app import generate_reset_token
        reset_token = generate_reset_token()
        user.reset_token = reset_token
        user.reset_token_expires = datetime.datetime.now() + datetime.timedelta(hours=1)
        
        print(f"✅ Reset token oluşturuldu: {reset_token[:20]}...")
        print(f"✅ Token geçerlilik süresi: {user.reset_token_expires}")
        
        # Test email sending
        reset_url = f"http://127.0.0.1:5000/reset_password/{reset_token}"
        email_body = f"""
        <h2>DMS - Şifre Sıfırlama</h2>
        <p>Test e-postası</p>
        <p>Reset URL: {reset_url}</p>
        """
        
        print("📧 E-posta gönderimi test ediliyor...")
        if send_email(user.email, "Test - Şifre Sıfırlama", email_body):
            print("✅ E-posta başarıyla gönderildi (debug mode)")
        else:
            print("❌ E-posta gönderiminde hata")
        
        # Save to database
        try:
            db.session.commit()
            print("✅ Veritabanı güncellemesi başarılı")
        except Exception as e:
            print(f"❌ Veritabanı hatası: {e}")
            db.session.rollback()
        
        print(f"\n🔗 Test için reset linki:")
        print(f"   {reset_url}")
        
        print(f"\n📋 Test Adımları:")
        print(f"   1. {reset_url} adresine git")
        print(f"   2. Yeni şifre belirle")
        print(f"   3. Giriş sayfasında test et")

if __name__ == '__main__':
    test_password_reset()
