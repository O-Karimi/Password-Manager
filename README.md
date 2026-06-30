# 🔒 Secure Vault - Zero-Knowledge Password Manager

Secure Vault is a military-grade, web-based password manager built with Django. It utilizes a true Zero-Knowledge cryptographic architecture, ensuring that your raw master password and unencrypted data never exist on the server's hard drive.

## ✨ Features

* **Zero-Knowledge Architecture:** Master keys are derived client-side/in-memory using PBKDF2 with 600,000 iterations.
* **AES Encryption:** All vault data is symmetrically encrypted using Fernet (AES-128 in CBC mode with SHA256 HMAC).
* **Secure Session Management:** Vault keys only exist in volatile session RAM and are wiped upon logout or expiration.
* **Cryptographic Re-Keying:** Users can update their master password without losing data through an automated unlock-and-re-encrypt pipeline.
* **Local Vault Export:** One-click on-the-fly decryption to export the entire vault as a standard CSV file.
* **Advanced Password Generator:** Built-in API to generate cryptographically strong passwords and passphrases.

## 🧠 Cryptographic Flow (How it works)

1. **Registration:** A random `salt` is generated. The user's plain-text password and salt run through PBKDF2 to derive a `Master Key`. A random `Vault Key` is generated, encrypted by the Master Key, and stored in the database.
2. **Login:** The plain-text password is intercepted to derive the Master Key again. The Master Key unlocks the encrypted Vault Key, which is then stored temporarily in the browser's secure session.
3. **Data Access:** The application uses the temporary session Vault Key to decrypt passwords on-the-fly for the dashboard. 
*At no point does the server database possess the required keys to decrypt the vault.*

## 🛠️ Tech Stack

* **Backend:** Python, Django
* **Cryptography:** `cryptography` (Hazmat Primitives, Fernet, PBKDF2HMAC)
* **Frontend:** HTML5, CSS3, Vanilla JavaScript
* **Database:** MySQL

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/secure-vault.git](https://github.com/yourusername/secure-vault.git)
   cd secure-vault
   ``` 

2. **Create and activate a virtual environment:**
```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
   pip install -r requirements.txt
```

4. **Set up environment variables:**
   Copy `.env.example` to a new file named `.env` and fill in a random Django secret key.
```bash
   cp .env.example .env
```

5. **Run migrations and start the server:**
```bash
   python manage.py migrate
   python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser to access the application.