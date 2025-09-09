from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_NAME = 'vehicle_reports.db'

# Initialize database if it doesn't exist
def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicle_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                sr_no INTEGER,
                vrn TEXT,
                model TEXT,
                entry_date TEXT,
                in_time TEXT,
                out_date TEXT,
                out_time TEXT,
                remarks TEXT
            )
        ''')
        conn.commit()
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_reports', methods=['POST'])
def save_reports():
    data = request.json
    print("Received data:", data)  # Debug log
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for entry in data:
        cursor.execute('''
            INSERT INTO vehicle_reports 
            (city, sr_no, vrn, model, entry_date, in_time, out_date, out_time, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry['city'],
            int(entry['sr_no']) if entry['sr_no'] else None,
            entry['vrn'],
            entry['model'],
            entry['entry_date'],
            entry['in_time'],
            entry['out_date'],
            entry['out_time'],
            entry['remarks']
        ))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/view_logs')
def view_logs():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM vehicle_reports ORDER BY entry_date DESC, city, sr_no')
    rows = cursor.fetchall()
    conn.close()
    return render_template('logs.html', entries=rows, filter_date=None)

@app.route('/view_by_date/<entry_date>')
def view_by_date(entry_date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM vehicle_reports
        WHERE entry_date = ?
        ORDER BY city, sr_no
    ''', (entry_date,))
    rows = cursor.fetchall()
    conn.close()
    return render_template('logs.html', entries=rows, filter_date=entry_date)

@app.route('/save_reports_row', methods=['POST'])
def save_reports_row():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'No data received'}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO vehicle_reports (city, sr_no, vrn, model, entry_date, in_time, out_date, out_time, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['city'],
        data['sr_no'],
        data['vrn'],
        data['model'],
        data['entry_date'],
        data['in_time'],
        data['out_date'],
        data['out_time'],
        data['remarks']
    ))
    conn.commit()
    conn.close()
    return jsonify({'status': 'Row saved'})


if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))  # Render sets this dynamically
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
