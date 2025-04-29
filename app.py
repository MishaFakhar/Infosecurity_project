from flask import Flask, render_template, request
from flask_talisman import Talisman
from pqc.kem import kyber768 as kemalg
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import secrets
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')  # Fallback if .env missing
Talisman(app)

# Load Kyber KEM
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
    
    # Debug prints
    print(f"Encryption - Key (hex): {key.hex()}")
    print(f"Encryption - IV (hex): {iv.hex()}")
    print(f"Encryption - Tag (hex): {encryptor.tag.hex()}")
    print(f"Encryption - Ciphertext (hex): {ciphertext.hex()}")
    print(f"Encryption - Plaintext: {plaintext}")
    
    return base64.b64encode(iv + encryptor.tag + ciphertext).decode('utf-8')

def aes_decrypt(key, token):
    try:
        # Base64 decode the token to retrieve the IV, tag, and ciphertext
        raw = base64.b64decode(token)
        
        # Extract components (AES-GCM needs 12-byte IV, 16-byte tag)
        iv = raw[:12]  # First 12 bytes are IV
        tag = raw[12:28]  # Next 16 bytes are the tag
        ciphertext = raw[28:]  # Remaining bytes are the ciphertext

        print(f"Decryption - IV (hex): {iv.hex()}")
        print(f"Decryption - Tag (hex): {tag.hex()}")
        print(f"Decryption - Ciphertext (hex): {ciphertext.hex()}")
        print(f"Decryption - raw data length: {len(raw)}")

        # Decrypt using the AES key, IV, tag, and ciphertext
        decryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=default_backend()
        ).decryptor()

        # Decrypt and return the plaintext
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext.decode()
    except Exception as e:
        print(f"Error during AES decryption: {str(e)}")
        print(f"Key (hex): {key.hex()}")
        print(f"IV (hex): {iv.hex() if 'iv' in locals() else 'N/A'}")
        print(f"Tag (hex): {tag.hex() if 'tag' in locals() else 'N/A'}")
        print(f"Ciphertext (hex): {ciphertext.hex() if 'ciphertext' in locals() else 'N/A'}")
        print(f"Token length: {len(token)}")
        print(f"Raw data length: {len(raw) if 'raw' in locals() else 'N/A'}")
        raise


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
            try:
                public_key_b64 = request.form.get("public_key")
                public_key = base64.b64decode(public_key_b64)
                message = request.form.get("message")

                ciphertext_kem, shared_secret = kyber.encap(public_key)
                aes_key = shared_secret[:32]
                
                # Store the shared secret in the form for decryption
                shared_secret_b64 = base64.b64encode(shared_secret).decode('utf-8')
                
                print(f"Encryption - Shared Secret (hex): {shared_secret.hex()}")
                print(f"Encryption - AES Key (hex): {aes_key.hex()}")

                encrypted_message = aes_encrypt(aes_key, message)
                
                context.update({
                    'public_key': public_key_b64,
                    'private_key': request.form.get("private_key"),
                    'ciphertext_kem': base64.b64encode(ciphertext_kem).decode('utf-8'),
                    'encrypted_message': encrypted_message,
                    'shared_secret': shared_secret_b64  # Pass this to the form
                })
            except Exception as e:
                print(f"Error during encryption: {str(e)}")
                context['error'] = f"Encryption error: {str(e)}"

        elif action == "decrypt":
            try:
                # Instead of deriving the shared secret again, use the one from encryption
                shared_secret_b64 = request.form.get("shared_secret")
                shared_secret = base64.b64decode(shared_secret_b64)
                aes_key = shared_secret[:32]
                
                encrypted_message = request.form.get("encrypted_message")
                
                print(f"Decryption - Using saved Shared Secret (hex): {shared_secret.hex()}")
                print(f"Decryption - AES Key (hex): {aes_key.hex()}")

                decrypted_message = aes_decrypt(aes_key, encrypted_message)

                context.update({
                    'public_key': request.form.get("public_key"),
                    'private_key': request.form.get("private_key"),
                    'ciphertext_kem': request.form.get("ciphertext_kem"),
                    'shared_secret': shared_secret_b64,
                    'decrypted_message': decrypted_message
                })
            except Exception as e:
                print(f"Error during decryption: {str(e)}")
                context['error'] = f"Decryption error: {str(e)}"

    return render_template("index.html", **context)


if __name__ == "__main__":
    app.run(debug=True) 
