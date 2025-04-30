# 🔐 Post-Quantum Secure Messaging App

A Flask web application demonstrating quantum-resistant encryption using Kyber768 and AES-GCM.

## ✨ Features
- Quantum-safe key generation (Kyber768)
- End-to-end encrypted messaging
- Simple browser interface
- Debug-friendly encryption logs

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Git

### Installation
```bash
# Clone repository
git clone https://github.com/Jannat-Butt/infosecurity_projects.git
cd infosecurity_projects

# Create virtual environment
python -m venv venv

# Activate environment (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```
### Running Locally
  - python app.py
  - Access at: http://localhost:5000

### Public Deployment
  - Access at: https://imjannatbutt.pythonanywhere.com/

### Private Deployment
  - Run .\deploy.ps1
  - Access at: https://entity-asia-gratis-patterns.trycloudflare.com/


### 📂 Files
  - **`app.py`**: Core Flask application with encryption logic
  - **`requirements.txt`**: Lists all Python packages needed (`flask`, `cryptography`, etc.)
  - **`static/style.css`**: Custom styling for the web interface
  - **`templates/index.html`**: Frontend HTML with message forms
  - **`deploy.ps1`**: Windows script to launch Flask + Cloudflare tunnel


### ⚠️ Troubleshooting
  - Module errors: pip install -r requirements.txt --force-reinstall
  - Port conflicts: Change port=5001 in app.py
  - Key errors: Ensure .env exists with SECRET_KEY
