from flask import Flask, request, jsonify, send_from_directory # type: ignore
from flask_cors import CORS # type: ignore
import sqlite3
import os

app = Flask(__name__)
CORS(app)  # Allow your HTML files to talk to this server

# Database setup
def init_db():
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            quiz_number INTEGER NOT NULL,
            score INTEGER NOT NULL,
            total_possible INTEGER NOT NULL,
            date_taken DATE DEFAULT CURRENT_DATE
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return "Quiz Server is Running!"

@app.route('/save_score', methods=['POST'])
def save_score():
    data = request.json
    student = data['student']
    quiz = data['quiz']
    score = data['score']
    total = data['total']
    
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO quiz_scores (student_name, quiz_number, score, total_possible)
        VALUES (?, ?, ?, ?)
    ''', (student, quiz, score, total))
    conn.commit()
    
    # Check if student completed all 20
    cursor.execute('''
        SELECT COUNT(DISTINCT quiz_number) 
        FROM quiz_scores 
        WHERE student_name = ?
    ''', (student,))
    completed = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'success': True,
        'completed': completed,
        'message': f'Quiz {quiz} saved! Completed {completed}/20 quizzes'
    })

@app.route('/progress/<student>')
def get_progress(student):
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    # Get all scores for student
    cursor.execute('''
        SELECT quiz_number, score, total_possible, date_taken
        FROM quiz_scores 
        WHERE student_name = ?
        ORDER BY quiz_number
    ''', (student,))
    
    scores = cursor.fetchall()
    
    # Calculate totals
    cursor.execute('''
        SELECT 
            SUM(score) as total,
            SUM(total_possible) as possible,
            COUNT(DISTINCT quiz_number) as completed
        FROM quiz_scores 
        WHERE student_name = ?
    ''', (student,))
    
    total, possible, completed = cursor.fetchone()
    
    conn.close()
    
    return jsonify({
        'student': student,
        'completed': completed,
        'total_score': total,
        'total_possible': possible,
        'percentage': (total/possible)*100 if possible else 0,
        'scores': [{'quiz': q, 'score': s, 'total': t, 'date': d} for q, s, t, d in scores]
    })

@app.route('/leaderboard')
def leaderboard():
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            student_name,
            COUNT(DISTINCT quiz_number) as quizzes_done,
            SUM(score) as total_score,
            SUM(total_possible) as total_possible,
            ROUND(AVG(score * 100.0 / total_possible), 1) as avg_percentage
        FROM quiz_scores 
        GROUP BY student_name
        ORDER BY avg_percentage DESC
    ''')
    
    students = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'name': s[0],
        'quizzes_done': s[1],
        'total_score': s[2],
        'total_possible': s[3],
        'average': s[4]
    } for s in students])

if __name__ == '__main__':
    init_db()
    print("🚀 Quiz Server Starting...")
    print("📊 Database: quiz.db")
    print("🌐 Open your quiz HTML files to start!")
    app.run(debug=True, port=5000)  

    
#Automatic Completion
# Add this to your server to auto-detect completion
@app.route('/check_completion/<student>')
def check_completion(student):
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(DISTINCT quiz_number) 
        FROM quiz_scores 
        WHERE student_name = ?
    ''', (student,))
    
    completed = cursor.fetchone()[0]
    
    if completed >= 20:
        # Student finished all quizzes!
        cursor.execute('''
            SELECT 
                SUM(score),
                SUM(total_possible)
            FROM quiz_scores 
            WHERE student_name = ?
        ''', (student,))
        
        total, possible = cursor.fetchone()
        percentage = (total/possible) * 100
        
        return jsonify({
            'status': 'completed',
            'message': f'🎉 Congratulations! You completed all 20 quizzes!',
            'final_score': f'{total}/{possible} ({percentage:.1f}%)'
        })
    
    return jsonify({
        'status': 'in_progress',
        'completed': completed,
        'remaining': 20 - completed
    })