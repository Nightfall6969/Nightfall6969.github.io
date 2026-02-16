-- SQLite
CREATE TABLE quiz_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT NOT NULL,
    quiz_number INTEGER NOT NULL,
    score INTEGER NOT NULL,
    total_possible INTEGER NOT NULL,
    date_taken DATE DEFAULT CURRENT_DATE
); 
INSERT INTO quiz_scores (student_name, quiz_number, score, total_possible) 
VALUES ('John Smith', 1, 18, 20);

INSERT INTO quiz_scores (student_name, quiz_number, score, total_possible) 
VALUES ('Mary Johnson', 1, 19, 20);

INSERT INTO quiz_scores (student_name, quiz_number, score, total_possible) 
VALUES ('John Smith', 2, 15, 20);

SELECT * FROM quiz_scores;

SELECT * FROM quiz_scores WHERE student_name = 'John Smith';

SELECT 
    student_name,
    quiz_number,
    score,
    total_possible,
    (score * 100.0 / total_possible) AS percentage
FROM quiz_scores;

SELECT 
    quiz_number,
    AVG(score * 100.0 / total_possible) AS average_percentage
FROM quiz_scores
GROUP BY quiz_number;

-- See all scores for a student
SELECT * FROM quiz_scores WHERE student_name = 'Student Name';

-- See if they've done all 20
SELECT student_name, COUNT(*) as quizzes_done
FROM quiz_scores 
GROUP BY student_name
HAVING quizzes_done = 20;