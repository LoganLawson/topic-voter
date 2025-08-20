
from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
import qrcode
import io
import base64

app = Flask(__name__)
# API endpoint for live leaderboard data
@app.route('/leaderboard-data')
def leaderboard_data():
    questions = load_questions()
    questions_sorted = sorted(questions, key=lambda q: q['score'], reverse=True)
    return jsonify({'questions': questions_sorted})

# Leaderboard page
@app.route('/leaderboard')
def leaderboard():
    questions = load_questions()
    questions_sorted = sorted(questions, key=lambda q: q['score'], reverse=True)
    
    # Generate QR code for questions page
    # Use environment variable for production URL, fallback to request.url_root for local dev
    base_url = os.getenv('PRODUCTION_URL', request.url_root.rstrip('/'))
    questions_url = f"{base_url}/questions"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(questions_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return render_template('leaderboard.html', questions=questions_sorted, qr_code=qr_code_base64)
def load_questions():
    with open(os.path.join(os.path.dirname(__file__), 'questions.json')) as f:
        return json.load(f)

def save_questions(questions):
    with open(os.path.join(os.path.dirname(__file__), 'questions.json'), 'w') as f:
        json.dump(questions, f, indent=4)

@app.route('/questions')
def questions():
    questions = load_questions()
    # Sort by score descending, then by id for stable order
    questions_sorted = sorted(questions, key=lambda q: (-q['score'], q['id']))
    return render_template('questions.html', questions=questions_sorted)

# Voting endpoint
@app.route('/vote', methods=['POST'])
def vote():
    data = request.get_json()
    qid = data.get('id')
    questions = load_questions()
    for q in questions:
        if q['id'] == qid:
            q['score'] += 1
            break
    save_questions(questions)
    return jsonify({'success': True, 'score': next(q['score'] for q in questions if q['id'] == qid)})

# Reset endpoint - resets all scores to 0
@app.route('/reset', methods=['POST'])
def reset():
    questions = load_questions()
    for q in questions:
        q['score'] = 0
    save_questions(questions)
    return jsonify({'success': True, 'message': 'All scores reset to 0'})


if __name__ == '__main__':
    app.run(debug=True)
