from flask import Flask, request, jsonify, render_template, send_file
import pandas as pd
import smtplib
import os

app = Flask(__name__)

# Base directory for relative paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load Excel data
excel_path = os.path.join(BASE_DIR, "descriptions.xlsx")
df = pd.read_excel(excel_path)

# Images folder
image_base_dir = os.path.join(BASE_DIR, "static", "compund images")

def get_image_path(compund_name):
    image_path = os.path.join(image_base_dir, f"{compund_name}.PNG")
    return image_path if os.path.exists(image_path) else None

@app.route('/')
def index():
    return render_template('test.html')

@app.route('/suggestions', methods=['GET'])
def suggestions():
    query = request.args.get('query', "").strip().lower()
    if not query:
        return jsonify({'suggestions': []})
    matches = df[df['Sialic acid analogues'].str.contains(query, case=False, na=False, regex=False)]
    return jsonify({'suggestions': matches['Sialic acid analogues'].tolist()})

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', "").strip().lower()
    if not query:
        return jsonify({'results': [], 'suggestions': []})
    results = df[df['Sialic acid analogues'].str.contains(query, case=False, na=False, regex=False)]
    if results.empty:
        return jsonify({'results': [], 'suggestions': []})
    results_dict = results.to_dict(orient='records')
    for r in results_dict:
        r['Image'] = get_image_path(r['Sialic acid analogues'])
    return jsonify({'results': results_dict, 'suggestions': [r['Sialic acid analogues'] for r in results_dict]})

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(BASE_DIR, "sialic acid analog", filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(file_path, as_attachment=True)

# Gmail SMTP (password from env variable)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'lathamythili2000@gmail.com'
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # set this in environment

@app.route('/submit_question', methods=['POST'])
def ask_question():
    question = request.form['user_question']
    send_email(question)
    return jsonify({'message': 'Question sent successfully!'})

def send_email(question):
    email_message = f'Subject: New Question\n\nYou have received a new question:\n\n{question}'
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, 'lathaladu0912@gmail.com', email_message)

if __name__ == '__main__':
    app.run(debug=True)
