from flask import Flask, render_template, request, redirect, url_for, session
from collections import Counter
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

    contact_names, last_seen_times = extract_contact_info(extracted_texts)
    return render_template('results.html', contact_names=contact_names, last_seen_times=last_seen_times)

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

import re

import re

import re

def extract_contact_info(extracted_texts):
    contact_names = []
    last_seen_times = []

    for text in extracted_texts:
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Exclude lines with specific unwanted words or patterns
            if "¢" in line or "yesterday" in line.lower() or any(word.lower() in line.lower() for word in ["today", "aGe", "-POSOC", "2e6", "@00@", "BGOZEGOOSCSBOOO", "5 e", "BSar2a eg", "@9g DdDOevec", "i> Bo", "SOS Aer Sh BOOM", "0G: =~ HG"]):
                continue
            
            # Use regex to identify and exclude lines that are only times
            match_time = re.match(r'^\d{1,2}:\d{2}\s*(?:AM|PM)?$', line)
            if match_time:
                last_seen_times.append(line)
                continue
            
            # Use regex to identify valid contact names
            match_name = re.match(r'^[A-Za-z][A-Za-z\s.@+-\u0C00-\u0C7F]{2,}$', line)
            if match_name:
                contact_names.append(line)
    
    # Count occurrences of each contact name
    contact_name_counts = Counter(contact_names)

    # Add contact names with zero count if not repeated
    for name in contact_names:
        if name not in contact_name_counts:
            contact_name_counts[name] = 0
    
    return contact_name_counts, last_seen_times


if __name__ == '__main__':
    app.run(debug=True)
