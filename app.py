from flask import Flask, jsonify, render_template, request

import sqlite3
from logging.config import dictConfig
from datetime import datetime

# Configure logging

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "./log/flask.log",
                "formatter": "default",
            },
        },
        "root": {"level": "DEBUG", "handlers": ["console", "file"]},
    }
)

app = Flask(__name__, static_url_path='/ADailyJournalPrompt/static')
app.config['APPLICATION_ROOT'] = '/ADailyJournalPrompt'
DATABASE = 'journal.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    #check_conn(conn)
    conn.row_factory = sqlite3.Row
    return conn

def check_conn(conn):
     try:
        conn.cursor()
        app.logger.debug('DB connection successful!?')
        return True
     except Exception as ex:
        app.logger.debug('DB connection failed!?')
        return False

@app.route('/ADailyJournalPrompt/daily-prompt', methods=['GET'])
def daily_prompt():
    app.logger.debug('daily prompt')    
    conn = get_db_connection()
    cur = conn.cursor()

    # Get the current day index
    day_of_year = datetime.now().strftime("%Y%m%d")
    seed = int(day_of_year) % 10
    # cur.execute("SELECT * FROM journal_prompts WHERE rating LIKE 'pos' ORDER BY id LIMIT 1 OFFSET ?", (seed,))
    # cur.execute("SELECT * FROM journal_prompts WHERE rating LIKE 'pos' ORDER BY RANDOM() LIMIT 1")
    cur.execute("SELECT * FROM journal_prompts ORDER BY RANDOM() LIMIT 1")
    prompt = cur.fetchone()
    conn.close()

    #app.logger.debug(str(prompt))

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

@app.route('/ADailyJournalPrompt')
def index():
    #app.logger.debug('debug')
    #app.logger.info('info')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False)
