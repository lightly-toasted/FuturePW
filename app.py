import os, json, base64, urllib.parse, datetime, hashlib
from flask import Flask, render_template, request, redirect, flash, get_flashed_messages
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from hashmoji import hashmoji

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates', static_url_path='/')
app.config['SECRET_KEY'] = os.environ.get('ENCRYPTION_KEY')
encryptionKey = os.environ.get('ENCRYPTION_KEY')

if encryptionKey is None:
    raise ValueError("ENCRYPTION_KEY environment variable is not set")

def getTimestamp():
    dt = datetime.datetime.now(datetime.timezone.utc)
    utc_time = dt.replace(tzinfo=datetime.timezone.utc)
    return utc_time.timestamp()

def generateFernetKey(input):
    hash_object = hashlib.sha256(input.encode('utf-8'))
    key = hash_object.digest()[:32]
    return base64.urlsafe_b64encode(key)

def encrypt(data, key=None):
    if key is None:
        key = encryptionKey
    fernet = Fernet(key)
    encrypted_bytes = fernet.encrypt(json.dumps(data).encode())
    return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')

def decrypt(data, key=None):
    if key is None:
        key = encryptionKey
    fernet = Fernet(key)
    encrypted_bytes = base64.urlsafe_b64decode(data)
    return json.loads(fernet.decrypt(encrypted_bytes).decode())

def hashToEmoji(data):
    return hashmoji(hashlib.md5(data.encode('utf-8')).digest())

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
        timeDelta = datetime.timedelta(**{timeUnit: timeNumber})

        data = {
            "content": content,
            "createdAt": currentTimestamp,
            "duration": timeDelta.total_seconds(),
        }

        if 'pin' in request.form:
            data['content'] = encrypt(content, generateFernetKey(request.form['pin']))
            data['secured'] = True

        encrypted = encrypt(data)

        return redirect(f'/unlock?data={encrypted}', 303)
    return render_template(
        'index.html',
        timedelta=datetime.timedelta,
        today=datetime.datetime.now(datetime.timezone.utc).strftime("%b %d, %Y"),
    )

@app.route('/unlock', methods=['GET', 'POST'])
def decrypt_route():
    encrypted = request.args.get('data')
    try:
        data = decrypt(encrypted)
    except:
        return "Error: invalid data", 400
    if data.get('secured', False):
        if request.method == 'POST' and 'pin' in request.form:
            try:
                data['content'] = decrypt(data['content'], generateFernetKey(request.form['pin']))
                data.pop('secured', None)
            except:
                flash("Invalid PIN")
        if 'secured' in data:
            return render_template('secured.html')
    unlockAt = data['createdAt'] + data['duration']
    currentTimestamp = getTimestamp()
    if currentTimestamp < unlockAt:
        remainingSeconds = round(unlockAt - currentTimestamp)
        hours, remainder = divmod(remainingSeconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        countdownText = f"{hours:02}:{minutes:02}:{seconds:02}"
        unlockAtISO = datetime.datetime.fromtimestamp(unlockAt, datetime.UTC).strftime('%Y%m%dT%H%M%SZ')
        ics_content = f"""BEGIN:VCALENDAR\r
VERSION:2.0\r
PRODID:-//FuturePW//NONSGML v1.0//EN\r
BEGIN:VEVENT\r
SUMMARY:FuturePW\r
DTSTART;VALUE=DATE-TIME:{unlockAtISO}\r
DTEND;VALUE=DATE-TIME:{unlockAtISO}\r
LOCATION:{request.url}\r
DESCRIPTION:FuturePW\r
STATUS:CONFIRMED\r
END:VEVENT\r
END:VCALENDAR\r"""
        return render_template(
            'countdown.html',
            remainingSeconds=remainingSeconds,
            countdownText=countdownText,
            iso=unlockAtISO,
            url=request.url,
            ics_content=urllib.parse.quote_plus(ics_content),
            hash=hashToEmoji(encrypted)
        )
    
    createdDate = datetime.datetime.fromtimestamp(data['createdAt'], datetime.UTC).strftime("%b %d, %Y")
    
    return render_template('decrypt.html', createdAt=createdDate, content=data['content'])

if __name__ == '__main__':
    app.run(debug=True)