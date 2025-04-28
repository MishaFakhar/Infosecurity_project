from flask import Flask, render_template, request
from flask_talisman import Talisman
from pqc.kem import kyber768 as kemalg
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from dotenv import load_dotenv
import os
import base64
import secrets

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
Talisman(app)

kyber = kemalg

# AES helper functions
def aes_encrypt(key, plaintext):
    iv = secrets.token_bytes(12)  # 96-bit IV for AES-GCM
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()

    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return base64.b64encode(iv + encryptor.tag + ciphertext).decode('utf-8')

def aes_decrypt(key, token):
    raw = base64.b64decode(token)
    iv = raw[:12]
    tag = raw[12:28]
    ciphertext = raw[28:]

    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()

    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return plaintext.decode()

@app.route("/", methods=["GET", "POST"])
def index():
    context = {}

    if request.method == "POST":
        action = request.form.get("action")

        if action == "generate_keys":
            public_key, private_key = kyber.keypair()
            context['public_key'] = base64.b64encode(public_key).decode('utf-8')
            context['private_key'] = base64.b64encode(private_key).decode('utf-8')

        elif action == "encrypt":
            public_key = base64.b64decode(request.form.get("public_key"))
            message = request.form.get("message")

            ciphertext_kem, shared_secret = kyber.encap(public_key)
            aes_key = shared_secret[:32]  # AES-256 expects 32 bytes

            encrypted_message = aes_encrypt(aes_key, message)

            context['public_key'] = request.form.get("public_key")
            context['private_key'] = request.form.get("private_key")
            context['ciphertext_kem'] = base64.b64encode(ciphertext_kem).decode('utf-8')
            context['encrypted_message'] = encrypted_message

        elif action == "decrypt":
            private_key = base64.b64decode(request.form.get("private_key"))
            ciphertext_kem = base64.b64decode(request.form.get("ciphertext_kem"))
            encrypted_message = request.form.get("encrypted_message")

            shared_secret = kyber.decap(ciphertext_kem, private_key)
            aes_key = shared_secret[:32]

            decrypted_message = aes_decrypt(aes_key, encrypted_message)

            context['public_key'] = request.form.get("public_key")
            context['private_key'] = request.form.get("private_key")
            context['ciphertext_kem'] = request.form.get("ciphertext_kem")
            context['decrypted_message'] = decrypted_message

    return render_template("index.html", **context)

if __name__ == '__main__':
    app.run(debug=True)
