import os, json
from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from datetime import datetime, timedelta, timezone
import base64

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates', static_url_path='/')
key = os.environ.get('ENCRYPTION_KEY')

if key is None:
    raise ValueError("ENCRYPTION_KEY environment variable is not set")

fernet = Fernet(key)

def getTimestamp():
    dt = datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    return utc_time.timestamp()

def encrypt(data):
    encrypted_bytes = fernet.encrypt(json.dumps(data).encode())
    return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')

def decrypt(data):
    encrypted_bytes = base64.urlsafe_b64decode(data)
    return json.loads(fernet.decrypt(encrypted_bytes).decode())

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        currentTimestamp = getTimestamp()
        content = request.form['content']
        timeNumber = float(request.form.get('timeNumber', 1))
        timeUnit = request.form.get('timeUnit', 'weeks')
        if timeUnit == 'years':
            timeNumber = 365.25 * timeNumber
            timeUnit = 'days'
        timeDelta = timedelta(**{timeUnit: timeNumber})


        encrypted = encrypt({
            "content": content,
            "createdAt": currentTimestamp,
            "duration": timeDelta.total_seconds(),
        })

        return redirect(f'/unlock?data={encrypted}', 303)
    return render_template('index.html', timedelta=timedelta, today=datetime.now().strftime("%b %d, %Y"))

@app.route('/unlock')
def decrypt_route():
    encrypted = request.args.get('data')
    try:
        data = decrypt(encrypted)
    except:
        return "Error: invalid data", 400
    unlockAt = data['createdAt'] + data['duration']
    currentTimestamp = getTimestamp()
    if currentTimestamp < unlockAt:
        return render_template('countdown.html', remainingSeconds=f"{(unlockAt - currentTimestamp):.0f}")
    
    createdDate = datetime.utcfromtimestamp(data['createdAt']).strftime("%b %d, %Y")
    
    return render_template('decrypt.html', createdAt=createdDate, content=data['content'])

if __name__ == '__main__':
    app.run(debug=True)