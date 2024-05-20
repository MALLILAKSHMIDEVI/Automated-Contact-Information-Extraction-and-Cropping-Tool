from flask import Flask, render_template, request, redirect, url_for, session
import pytesseract
from PIL import Image
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# Dummy user data for demonstration
users = {
    'user@example.com': 'password123'
}

@app.route('/')
def index():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users and users[email] == password:
            session['email'] = email
            return redirect(url_for('index'))
        else:
            return 'Invalid email or password'
    return render_template('login.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'email' not in session:
        return redirect(url_for('login'))

    if 'files[]' not in request.files:
        return 'No file part'
    
    files = request.files.getlist('files[]')

    extracted_texts = []
    for file in files:
        if file.filename == '':
            return 'No selected file'

        if file:
            image = Image.open(file)
            extracted_text = pytesseract.image_to_string(image)
            extracted_texts.append(extracted_text)

    parsed_texts = parse_texts(extracted_texts)
    return render_template('results.html', parsed_texts=parsed_texts)

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

def parse_texts(extracted_texts):
    parsed_texts = []

    for text in extracted_texts:
        lines = text.split('\n')
        contact_name = None
        last_seen = None
        for line in lines:
            if "My status" in line:
                if contact_name and last_seen:
                    parsed_texts.append((contact_name, last_seen))
                contact_name = None
                last_seen = None
            elif line.strip():
                if contact_name:
                    parsed_texts.append((contact_name, line.strip()))
                    contact_name = None
                else:
                    contact_name = line.strip()
            else:
                continue

    return parsed_texts

if __name__ == '__main__':
    app.run(debug=True)
