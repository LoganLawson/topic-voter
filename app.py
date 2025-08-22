
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import json
import os
import qrcode
import io
import base64
import glob

app = Flask(__name__)

# Get slideshow media files
def get_slideshow_files():
    media_folder = os.path.join(os.path.dirname(__file__), 'static', 'slideshow')
    if not os.path.exists(media_folder):
        return []
    
    # Supported image and video formats
    image_exts = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']
    video_exts = ['*.mp4', '*.webm', '*.mov', '*.avi']
    
    files = []
    for ext in image_exts + video_exts:
        files.extend(glob.glob(os.path.join(media_folder, ext)))
        files.extend(glob.glob(os.path.join(media_folder, ext.upper())))
    
    # Return relative paths for web serving
    return [os.path.basename(f) for f in sorted(files)]

# Serve slideshow media files
@app.route('/static/slideshow/<filename>')
def slideshow_media(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'static', 'slideshow'), filename)

# API endpoint for slideshow files
@app.route('/slideshow-files')
def slideshow_files():
    files = get_slideshow_files()
    return jsonify({'files': files})

# API endpoint for live leaderboard data
@app.route('/leaderboard-data')
def leaderboard_data():
    questions = load_questions()
    # Filter out hidden questions
    visible_questions = [q for q in questions if not q.get('hidden', False)]
    questions_sorted = sorted(visible_questions, key=lambda q: q['score'], reverse=True)
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
    # Filter out hidden questions and sort by score descending, then by id for stable order
    visible_questions = [q for q in questions if not q.get('hidden', False)]
    questions_sorted = sorted(visible_questions, key=lambda q: (-q['score'], q['id']))
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

# Hide question endpoint
@app.route('/hide-question', methods=['POST'])
def hide_question():
    data = request.get_json()
    print(f"Received hide request: {data}")  # Debug log
    qid = data.get('id')
    questions = load_questions()
    
    # Convert qid to int if it's a string
    try:
        qid = int(qid)
    except (ValueError, TypeError):
        print(f"Invalid question ID: {qid}")  # Debug log
        return jsonify({'success': False, 'error': 'Invalid question ID'})
    
    for q in questions:
        if q['id'] == qid:
            q['hidden'] = True
            save_questions(questions)
            print(f"Successfully hid question {qid}")  # Debug log
            return jsonify({'success': True, 'message': 'Question hidden'})
    
    print(f"Question {qid} not found")  # Debug log
    return jsonify({'success': False, 'error': 'Question not found'})

# Reset endpoint - resets all scores to 0 and shows all hidden questions
@app.route('/reset', methods=['POST'])
def reset():
    questions = load_questions()
    for q in questions:
        q['score'] = 0
        q['hidden'] = False  # Show all hidden questions
    save_questions(questions)
    return jsonify({'success': True, 'message': 'All scores reset to 0 and hidden questions restored'})


if __name__ == '__main__':
    app.run(debug=True)
