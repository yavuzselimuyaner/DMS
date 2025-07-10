#!/usr/bin/env python3
"""
Gmail SMTP Test Script
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_gmail_smtp():
    """Test Gmail SMTP connection"""
    print("📧 Gmail SMTP Bağlantısı Test Ediliyor...")
    
    # Gmail ayarları
    smtp_server = "smtp.gmail.com"
    port = 587
    sender_email = "yavuzselimuyaner@gmail.com"
    
    # App password gerekli - kullanıcıdan al
    print(f"\n🔑 Gmail App Password gerekli!")
    print(f"1. https://myaccount.google.com/apppasswords adresine gidin")
    print(f"2. 2-Factor Authentication aktif olmalı")
    print(f"3. Yeni app password oluşturun")
    print(f"4. 16-karakter şifreyi aşağıya girin")
    
    app_password = input("\nGmail App Password girin (16 karakter): ").strip().replace(" ", "")
    
    if len(app_password) != 16:
        print("❌ App password 16 karakter olmalı!")
        return False
    
    receiver_email = input("Test e-postası kime gönderilsin? (varsayılan: yavuzselimuyaner@gmail.com): ").strip()
    if not receiver_email:
        receiver_email = "yavuzselimuyaner@gmail.com"
    
    # E-posta içeriği
    message = MIMEMultipart("alternative")
    message["Subject"] = "DMS Test - Şifre Sıfırlama Sistemi"
    message["From"] = sender_email
    message["To"] = receiver_email
    
    html = """
    <html>
      <body>
        <h2>🎉 DMS E-posta Sistemi Test Başarılı!</h2>
        <p>Bu e-posta, DMS şifre sıfırlama sisteminin çalıştığını doğrular.</p>
        <p><strong>Test bilgileri:</strong></p>
        <ul>
            <li>Gönderen: {sender}</li>
            <li>Alıcı: {receiver}</li>
            <li>SMTP Server: {server}:{port}</li>
        </ul>
        <p>Şifre sıfırlama sistemi artık kullanıma hazır! 🚀</p>
        <hr>
        <p><small>DMS - Döküman Yönetim Sistemi</small></p>
      </body>
    </html>
    """.format(sender=sender_email, receiver=receiver_email, server=smtp_server, port=port)
    
    part = MIMEText(html, "html")
    message.attach(part)
    
    try:
        print(f"\n📤 E-posta gönderiliyor...")
        print(f"   Gönderen: {sender_email}")
        print(f"   Alıcı: {receiver_email}")
        print(f"   SMTP: {smtp_server}:{port}")
        
        # SMTP bağlantısı
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()  # TLS aktifleştir
        server.login(sender_email, app_password)
        
        # E-posta gönder
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        
        print("✅ E-posta başarıyla gönderildi!")
        print(f"✅ {receiver_email} adresini kontrol edin!")
        
        # App password'u app.py'ye kaydet
        print(f"\n📝 App.py güncellemesi:")
        print(f"app.config['MAIL_PASSWORD'] = '{app_password}'")
        
        return True
        
    except Exception as e:
        print(f"❌ E-posta gönderme hatası: {e}")
        print(f"\n🔧 Olası çözümler:")
        print(f"1. 2-Factor Authentication aktif mi?")
        print(f"2. App password doğru mu? (16 karakter)")
        print(f"3. İnternet bağlantısı var mı?")
        return False

if __name__ == "__main__":
    test_gmail_smtp()
