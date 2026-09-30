# Student Result Management System

## 1. Project Title
**Student Result Management System – Feature Set C**

## 2. Problem Statement
Develop a Python-based Student Result Management System that allows student records and subject marks to be managed and provides useful result and performance information.

## 3. Assigned Feature Set
- Add/edit/delete student records
- Multiple subject marks
- Total, percentage and grade
- Subject-wise performance
- Class performance summary

## 4. Features Implemented
- Add a student with roll number, name, class and marks.
- Edit student details and marks.
- Delete student records.
- Store marks for multiple subjects.
- Automatically calculate total marks, percentage and grade.
- View an individual student's complete result.
- View subject-wise average, highest, lowest and pass count.
- View class performance summary with class average, pass/fail counts and student ranking by total marks.
- Responsive and simple web interface.
- SQLite database for persistent storage.
- Input validation for required fields and marks from 0 to 100.

## 5. Technologies Used
- Python
- Flask
- SQLite
- HTML5
- CSS3
- Jinja2 templates

## 6. AI Tools Used
- ChatGPT for project planning, code generation assistance, debugging guidance, UI planning and documentation.
- The generated code was reviewed, tested and modified for this project.

## 7. Important AI Prompts / AI Usage
Examples of prompts used:
1. "Create a Python Flask Student Result Management System with SQLite."
2. "Implement add, edit and delete student records."
3. "Add multiple subject marks and calculate total, percentage and grade."
4. "Create subject-wise performance statistics."
5. "Create a class performance summary."
6. "Help debug and improve the Flask project."
7. "Create a README for the Student Result Management System."

## 8. Project Structure
```text
student_result_management_system/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── student_form.html
│   ├── student_result.html
│   ├── performance.html
│   └── summary.html
└── static/
    └── style.css
```

## 9. How to Run the Project

### Step 1: Install Python
Install Python 3.10 or newer.

### Step 2: Open the project folder
Open Command Prompt/Terminal inside this folder.

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Start the application
```bash
python app.py
```

### Step 5: Open in browser
Go to:
```text
http://127.0.0.1:5000
```

The SQLite database (`students.db`) is created automatically when the application starts.

## 10. Screenshots
Before submission, run the project and add screenshots of:
- Dashboard
- Add Student page
- Edit Student page
- Individual Result page
- Subject-wise Performance page
- Class Performance Summary page

Recommended README screenshot section:
```markdown
## Screenshots

### Dashboard
![Dashboard](screenshots/dashboard.png)

### Add Student
![Add Student](screenshots/add-student.png)

### Student Result
![Student Result](screenshots/student-result.png)

### Subject Performance
![Subject Performance](screenshots/subject-performance.png)

### Class Summary
![Class Summary](screenshots/class-summary.png)
```

## 11. Academic Note
This project was developed with AI assistance. The student should review, run, test and understand the implementation before submission.
