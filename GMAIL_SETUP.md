# 📧 Gmail App Password Alma Kılavuzu

## 🔐 **Gmail App Password Nedir?**
Gmail App Password, Gmail hesabınızı üçüncü parti uygulamalarla güvenli bir şekilde kullanmanızı sağlayan özel bir şifredir.

## 📋 **Adım Adım Kurulum:**

### 1️⃣ **2-Factor Authentication Aktifleştir:**
- https://myaccount.google.com/security adresine gidin
- "2-Step Verification" seçeneğini bulun ve aktifleştirin
- Telefon numaranızla doğrulama yapın

### 2️⃣ **App Password Oluştur:**
- https://myaccount.google.com/apppasswords adresine gidin
- "Select app" menüsünden "Mail" seçin
- "Select device" menüsünden "Other (Custom name)" seçin
- "DMS Password Reset" yazın
- "Generate" butonuna tıklayın

### 3️⃣ **16-Karakter Şifreyi Kopyala:**
- Ekranda 16 karakterlik bir şifre görünecek (örn: abcd efgh ijkl mnop)
- Bu şifreyi kopyalayın (boşluklar olmadan: abcdefghijklmnop)

### 4️⃣ **App.py'ye Ekle:**
```python
app.config['MAIL_PASSWORD'] = 'abcdefghijklmnop'  # Kopyaladığınız 16-karakter şifre
```

## ⚡ **Hızlı Test:**
1. App password'u ekledikten sonra Flask'ı yeniden başlatın
2. "Şifremi Unuttum" sayfasına gidin: http://127.0.0.1:5000/forgot_password
3. yavuzselimuyaner@gmail.com adresini girin
4. 1-2 dakika içinde e-posta gelecek

## 🛠️ **Sorun Giderme:**

### ❌ "App passwords aren't available" hatası:
- 2-Factor Authentication aktif değil
- Önce 2FA'yı aktifleştirin

### ❌ "Invalid credentials" hatası:
- App password yanlış girilmiş
- Boşlukları kaldırın, sadece 16 karakteri girin

### ❌ "Less secure app access" hatası:
- App password kullanın, normal şifre değil
- 2FA aktif olmalı

## 🔒 **Güvenlik Notları:**
- App password'u kimseyle paylaşmayın
- Sadece güvendiğiniz uygulamalarda kullanın
- İhtiyaç kalmadığında silebilirsiniz

## 📱 **Test Komutları:**
```bash
# Test scripti ile test edin
python test_password_reset.py

# Veya manuel test
# 1. http://127.0.0.1:5000/forgot_password
# 2. yavuzselimuyaner@gmail.com girin  
# 3. E-postanızı kontrol edin
```

**App Password aldıktan sonra sistem tamamen çalışacak! 🎉**
