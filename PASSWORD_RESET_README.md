# 🔐 Şifre Sıfırlama Sistemi - Kullanım Kılavuzu

## ✅ **Eklenen Özellikler:**

### 🔑 **Şifremi Unuttum Sistemi:**
- ✅ E-posta ile şifre sıfırlama
- ✅ Güvenli reset token sistemi (1 saat geçerli)
- ✅ HTML e-posta template'i
- ✅ Token süresi kontrolü
- ✅ Giriş sayfasında kolay erişim

### 📧 **E-posta Ayarları:**

#### Gmail Kullanımı için:
```python
# app.py içinde
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_app_password'
```

#### Gmail App Password Alma:
1. Google hesabınızda 2-factor authentication aktif edin
2. https://myaccount.google.com/apppasswords adresine gidin
3. "Uygulama Şifresi" oluşturun
4. 16 karakterlik şifreyi `MAIL_PASSWORD`'e yazın

### 🗃️ **Veritabanı Değişiklikleri:**
```sql
ALTER TABLE users 
ADD COLUMN reset_token VARCHAR(100) NULL,
ADD COLUMN reset_token_expires DATETIME NULL;
```

### 🎯 **Kullanım:**

#### 1. **Şifre Sıfırlama Talebi:**
- Giriş sayfasında "Şifremi Unuttum" linkine tıklayın
- E-posta adresinizi girin
- Gönder butonuna basın

#### 2. **E-posta Kontrolü:**
- E-postanızı kontrol edin
- "Şifremi Sıfırla" butonuna tıklayın
- Veya gönderilen linki kopyalayın

#### 3. **Yeni Şifre Belirleme:**
- Açılan sayfada yeni şifrenizi girin
- Şifre onayını tekrar girin
- "Şifreyi Güncelle" butonuna basın

### 🔒 **Güvenlik Özellikleri:**
- ✅ Rastgele 32-byte güvenli token
- ✅ 1 saat token geçerlilik süresi
- ✅ Kullanıldıktan sonra token otomatik silinir
- ✅ Geçersiz tokenlar için hata mesajı
- ✅ Şifre uzunluk kontrolü (min 6 karakter)

### 🧪 **Test:**
```bash
# Test scripti çalıştır
python test_password_reset.py

# Manuel test
# 1. http://127.0.0.1:5000/forgot_password
# 2. Mevcut kullanıcı e-postası girin
# 3. Konsol çıktısındaki reset linkini kopyala
# 4. Reset linkine git ve yeni şifre belirle
```

### 📁 **Yeni Dosyalar:**
- `templates/forgot_password.html` - Şifremi unuttum sayfası
- `templates/reset_password.html` - Şifre sıfırlama sayfası
- `test_password_reset.py` - Test scripti

### 🚀 **Production İçin:**
1. `.env` dosyası oluşturun (`.env.example`'dan kopyalayın)
2. Gerçek e-posta bilgilerini girin
3. `send_email()` fonksiyonundaki debug kodunu kaldırın
4. Gerçek SMTP kodunu aktifleştirin

**Şifre sıfırlama sistemi başarıyla entegre edildi! 🎉**
