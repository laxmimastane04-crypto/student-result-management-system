from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "student-result-management-secret"
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "students.db"

DEFAULT_SUBJECTS = ["Python", "Java", "DBMS", "Computer Networks", "English"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            class_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            marks REAL NOT NULL CHECK(marks >= 0 AND marks <= 100),
            UNIQUE(student_id, subject_id),
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
        )
    """)
    for subject in DEFAULT_SUBJECTS:
        conn.execute("INSERT OR IGNORE INTO subjects(name) VALUES (?)", (subject,))
    conn.commit()
    conn.close()


def calculate_result(marks):
    values = [float(m["marks"]) for m in marks]
    total = sum(values)
    percentage = total / len(values) if values else 0

    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B+"
    elif percentage >= 60:
        grade = "B"
    elif percentage >= 50:
        grade = "C"
    elif percentage >= 40:
        grade = "D"
    else:
        grade = "F"

    return total, percentage, grade


@app.route("/")
def index():
    conn = get_db()
    students = conn.execute("""
        SELECT s.*, COUNT(m.id) AS subject_count,
               COALESCE(SUM(m.marks), 0) AS total_marks
        FROM students s
        LEFT JOIN marks m ON s.id = m.student_id
        GROUP BY s.id
        ORDER BY s.id DESC
    """).fetchall()
    conn.close()

    rows = []
    for student in students:
        subject_count = student["subject_count"]
        total = student["total_marks"]
        percentage = total / subject_count if subject_count else 0
        rows.append({**dict(student), "percentage": percentage})

    return render_template("index.html", students=rows)


@app.route("/student/add", methods=["GET", "POST"])
def add_student():
    conn = get_db()
    subjects = conn.execute("SELECT * FROM subjects ORDER BY id").fetchall()

    if request.method == "POST":
        roll_no = request.form.get("roll_no", "").strip()
        name = request.form.get("name", "").strip()
        class_name = request.form.get("class_name", "").strip()

        if not roll_no or not name or not class_name:
            flash("Please fill all student details.", "danger")
            conn.close()
            return render_template("student_form.html", student=None, subjects=subjects)

        try:
            cursor = conn.execute(
                "INSERT INTO students(roll_no, name, class_name) VALUES (?, ?, ?)",
                (roll_no, name, class_name)
            )
            student_id = cursor.lastrowid

            for subject in subjects:
                raw = request.form.get(f"marks_{subject['id']}", "").strip()
                if raw:
                    marks = float(raw)
                    if marks < 0 or marks > 100:
                        raise ValueError
                    conn.execute(
                        "INSERT INTO marks(student_id, subject_id, marks) VALUES (?, ?, ?)",
                        (student_id, subject["id"], marks)
                    )

            conn.commit()
            conn.close()
            flash("Student added successfully.", "success")
            return redirect(url_for("index"))
        except sqlite3.IntegrityError:
            conn.rollback()
            flash("Roll number already exists.", "danger")
        except (ValueError, TypeError):
            conn.rollback()
            flash("Marks must be valid numbers between 0 and 100.", "danger")

    conn.close()
    return render_template("student_form.html", student=None, subjects=subjects)


@app.route("/student/<int:student_id>/edit", methods=["GET", "POST"])
def edit_student(student_id):
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    subjects = conn.execute("SELECT * FROM subjects ORDER BY id").fetchall()

    if student is None:
        conn.close()
        flash("Student not found.", "danger")
        return redirect(url_for("index"))

    existing_marks = {
        row["subject_id"]: row["marks"]
        for row in conn.execute(
            "SELECT subject_id, marks FROM marks WHERE student_id = ?", (student_id,)
        ).fetchall()
    }

    if request.method == "POST":
        roll_no = request.form.get("roll_no", "").strip()
        name = request.form.get("name", "").strip()
        class_name = request.form.get("class_name", "").strip()

        if not roll_no or not name or not class_name:
            flash("Please fill all student details.", "danger")
        else:
            try:
                conn.execute("""
                    UPDATE students
                    SET roll_no = ?, name = ?, class_name = ?
                    WHERE id = ?
                """, (roll_no, name, class_name, student_id))

                conn.execute("DELETE FROM marks WHERE student_id = ?", (student_id,))
                for subject in subjects:
                    raw = request.form.get(f"marks_{subject['id']}", "").strip()
                    if raw:
                        marks = float(raw)
                        if marks < 0 or marks > 100:
                            raise ValueError
                        conn.execute(
                            "INSERT INTO marks(student_id, subject_id, marks) VALUES (?, ?, ?)",
                            (student_id, subject["id"], marks)
                        )

                conn.commit()
                conn.close()
                flash("Student updated successfully.", "success")
                return redirect(url_for("view_student", student_id=student_id))
            except sqlite3.IntegrityError:
                conn.rollback()
                flash("Roll number already exists.", "danger")
            except (ValueError, TypeError):
                conn.rollback()
                flash("Marks must be valid numbers between 0 and 100.", "danger")

    student_data = dict(student)
    conn.close()
    return render_template(
        "student_form.html",
        student=student_data,
        subjects=subjects,
        existing_marks=existing_marks
    )


@app.post("/student/<int:student_id>/delete")
def delete_student(student_id):
    conn = get_db()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()
    flash("Student deleted successfully.", "success")
    return redirect(url_for("index"))


@app.route("/student/<int:student_id>")
def view_student(student_id):
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    marks = conn.execute("""
        SELECT subjects.name, marks.marks
        FROM marks
        JOIN subjects ON subjects.id = marks.subject_id
        WHERE marks.student_id = ?
        ORDER BY subjects.id
    """, (student_id,)).fetchall()
    conn.close()

    if student is None:
        flash("Student not found.", "danger")
        return redirect(url_for("index"))

    total, percentage, grade = calculate_result(marks)
    return render_template(
        "student_result.html",
        student=student,
        marks=marks,
        total=total,
        percentage=percentage,
        grade=grade
    )


@app.route("/performance")
def performance():
    conn = get_db()
    subjects = conn.execute("SELECT * FROM subjects ORDER BY id").fetchall()

    subject_stats = []
    for subject in subjects:
        stats = conn.execute("""
            SELECT COUNT(marks.id) AS count,
                   COALESCE(AVG(marks.marks), 0) AS average,
                   COALESCE(MAX(marks.marks), 0) AS highest,
                   COALESCE(MIN(marks.marks), 0) AS lowest
            FROM marks
            WHERE subject_id = ?
        """, (subject["id"],)).fetchone()

        pass_count = conn.execute("""
            SELECT COUNT(*) FROM marks
            WHERE subject_id = ? AND marks >= 40
        """, (subject["id"],)).fetchone()[0]

        subject_stats.append({
            "name": subject["name"],
            "count": stats["count"],
            "average": stats["average"],
            "highest": stats["highest"],
            "lowest": stats["lowest"],
            "pass_count": pass_count
        })

    conn.close()
    return render_template("performance.html", subject_stats=subject_stats)


@app.route("/summary")
def summary():
    conn = get_db()
    students = conn.execute("""
        SELECT s.id, s.name, s.roll_no, s.class_name,
               COUNT(m.id) AS subject_count,
               COALESCE(SUM(m.marks), 0) AS total_marks
        FROM students s
        LEFT JOIN marks m ON s.id = m.student_id
        GROUP BY s.id
        ORDER BY total_marks DESC, s.name
    """).fetchall()

    student_rows = []
    for s in students:
        count = s["subject_count"]
        total = s["total_marks"]
        percentage = total / count if count else 0
        student_rows.append({
            **dict(s),
            "percentage": percentage,
            "grade": calculate_result(
                [{"marks": 0}] * 0
            )[2] if count == 0 else (
                "A+" if percentage >= 90 else
                "A" if percentage >= 80 else
                "B+" if percentage >= 70 else
                "B" if percentage >= 60 else
                "C" if percentage >= 50 else
                "D" if percentage >= 40 else "F"
            )
        })

    class_average = (
        sum(row["percentage"] for row in student_rows) / len(student_rows)
        if student_rows else 0
    )
    pass_count = sum(1 for row in student_rows if row["percentage"] >= 40)
    fail_count = len(student_rows) - pass_count

    conn.close()
    return render_template(
        "summary.html",
        students=student_rows,
        class_average=class_average,
        pass_count=pass_count,
        fail_count=fail_count,
        total_students=len(student_rows)
    )


@app.context_processor
def inject_year():
    from datetime import datetime
    return {"current_year": datetime.now().year}


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
