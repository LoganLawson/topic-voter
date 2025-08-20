
from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

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
    return render_template('leaderboard.html', questions=questions_sorted)
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


if __name__ == '__main__':
    app.run(debug=True)
