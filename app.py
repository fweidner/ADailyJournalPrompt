from flask import Flask, jsonify, render_template, request

import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = 'journal.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/daily-prompt', methods=['GET'])
def daily_prompt():
    conn = get_db_connection()
    cur = conn.cursor()

    # Get the current day index
    day_of_year = datetime.now().strftime("%Y%m%d")
    seed = int(day_of_year) % 10
    # cur.execute("SELECT * FROM journal_prompts WHERE rating LIKE 'pos' ORDER BY id LIMIT 1 OFFSET ?", (seed,))
    cur.execute("SELECT * FROM journal_prompts WHERE rating LIKE 'pos' ORDER BY RANDOM() LIMIT 1")
    prompt = cur.fetchone()
    conn.close()

    if prompt:
        return jsonify({'id': prompt['id'], 
                        'prompt': prompt['prompt'], 
                        'rating': prompt['rating']})
    else:
        return jsonify({'error': 'No prompt available'}), 404


@app.route('/rate-prompt', methods=['POST'])
def rate_prompt():
    conn = get_db_connection()
    cur = conn.cursor()

    data = request.json
    prompt_id = data.get('id')
    rating = data.get('rating')

    if rating not in ['pos', 'neg']:
        return jsonify({'error': 'Invalid rating value'}), 400

    # Update the rating of the given prompt
    cur.execute("UPDATE journal_prompts SET rating = ? WHERE id = ?", (rating, prompt_id))
    conn.commit()

    conn.close()
    return jsonify({'message': 'Rating updated successfully'})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
