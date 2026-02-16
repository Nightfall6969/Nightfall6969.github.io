import sqlite3
import datetime

def record_score():
    # Connect to database
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    # Get input
    student = input("Enter student name: ")
    quiz = int(input("Enter quiz number (1-20): "))
    score = int(input("Enter score (0-20): "))
    total = 20
    
    # Insert data
    cursor.execute("""
        INSERT INTO quiz_scores (student_name, quiz_number, score, total_possible)
        VALUES (?, ?, ?, ?)
    """, (student, quiz, score, total))
    
    conn.commit()
    
    # Show student's progress
    cursor.execute("""
        SELECT COUNT(DISTINCT quiz_number) 
        FROM quiz_scores 
        WHERE student_name = ?
    """, (student,))
    
    completed = cursor.fetchone()[0]
    print(f"\n✅ Score recorded for Quiz {quiz}")
    print(f"📊 {student} has completed {completed}/20 quizzes")
    
    if completed == 20:
        print("🎉 Student has completed all quizzes!")
        
        # Calculate final grade
        cursor.execute("""
            SELECT 
                SUM(score) as total,
                SUM(total_possible) as possible
            FROM quiz_scores 
            WHERE student_name = ?
        """, (student,))
        
        total, possible = cursor.fetchone()
        percentage = (total / possible) * 100
        print(f"📈 Final Score: {total}/{possible} = {percentage:.1f}%")
    
    conn.close()

if __name__ == "__main__":
    record_score()