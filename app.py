import os, json
from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import base64

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates', static_url_path='/')
key = os.environ['ENCRYPTION_KEY']

if key is None:
    raise ValueError("ENCRYPTION_KEY environment variable is not set")

fernet = Fernet(key)

def encrypt(data):
    encrypted_bytes = fernet.encrypt(json.dumps(data).encode())
    return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')

def decrypt(data):
    encrypted_bytes = base64.urlsafe_b64decode(data)
    return json.loads(fernet.decrypt(encrypted_bytes).decode())

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['text']
        salt = request.form['datetime']
        encrypted = encrypt({"text": text, "timestamp": salt})
        return redirect(f'/unlock?data={encrypted}')
    return render_template('index.html', now=datetime.now(), timedelta=timedelta)

@app.route('/unlock')
def decrypt_route():
    encrypted = request.args.get('data')
    data = decrypt(encrypted)
    if datetime.now() < datetime.fromisoformat(data['timestamp']):
        delta = datetime.fromisoformat(data['timestamp']) - datetime.now()
        return f"Error: it's not time yet ({delta.total_seconds():.0f} seconds remaining)", 403
    return f"{data['text']}, {data['timestamp']}"

if __name__ == '__main__':
    app.run(debug=True)