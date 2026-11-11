
from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3
import os

app = Flask(__name__)
DB = "ats.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            department TEXT,
            skills TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applicants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            skills TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            applicant_id INTEGER,
            job_id INTEGER,
            status TEXT DEFAULT 'Applied'
        )
    """)
    conn.commit()
    conn.close()

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Smart ATS | Applicant Tracking System</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{box-sizing:border-box}
body{margin:0;font-family:Arial;background:#f3f5fa;color:#202b43}
header{background:#172554;color:white;padding:22px 35px}
header h1{margin:0;font-size:25px}
header p{margin:7px 0 0;color:#cbd5e1}
nav{background:#1e3a8a;padding:14px 30px;display:flex;gap:22px;flex-wrap:wrap}
nav a{color:white;text-decoration:none;font-weight:bold}
main{max-width:1100px;margin:30px auto;padding:0 18px}
h2{color:#172554}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:18px}
.card,.panel{background:white;padding:22px;border-radius:12px;box-shadow:0 3px 14px #0000000c;margin-bottom:20px}
.card h3{margin:0;color:#64748b;font-size:15px}
.number{font-size:32px;font-weight:bold;color:#1d4ed8;margin-top:12px}
input,select{padding:11px;border:1px solid #cbd5e1;border-radius:7px;margin:5px 5px 5px 0;max-width:100%}
button{background:#2563eb;color:white;border:0;padding:11px 17px;border-radius:7px;cursor:pointer}
button:hover{background:#1d4ed8}
table{width:100%;border-collapse:collapse;background:white}
th,td{text-align:left;padding:13px;border-bottom:1px solid #e2e8f0}
th{background:#eff6ff}
.table-wrap{overflow-x:auto}
.tag{background:#dbeafe;color:#1e40af;padding:5px 9px;border-radius:15px}
footer{text-align:center;padding:25px;color:#64748b}
</style>
</head>
<body>
<header>
<h1>Smart ATS</h1>
<p>Applicant Tracking System | Recruitment Management Portal</p>
</header>
<nav>
<a href="/">Dashboard</a>
<a href="/jobs">Jobs</a>
<a href="/applicants">Applicants</a>
<a href="/applications">Applications</a>
<a href="/matching">Skill Matching</a>
</nav>
<main>
{{ content|safe }}
</main>
<footer>Smart ATS | College Project | Built with Python, Flask and SQLite</footer>
</body>
</html>
"""

def page(content):
    return render_template_string(HTML, content=content)

@app.route("/")
def dashboard():
    conn = get_db()
    jobs = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    applicants = conn.execute("SELECT COUNT(*) FROM applicants").fetchone()[0]
    applications = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    selected = conn.execute(
        "SELECT COUNT(*) FROM applications WHERE status='Selected'"
    ).fetchone()[0]
    conn.close()

    content = f"""
    <h2>Dashboard</h2>
    <p>Welcome to your recruitment management system.</p>
    <div class="cards">
      <div class="card"><h3>Total Jobs</h3><div class="number">{jobs}</div></div>
      <div class="card"><h3>Total Applicants</h3><div class="number">{applicants}</div></div>
      <div class="card"><h3>Total Applications</h3><div class="number">{applications}</div></div>
      <div class="card"><h3>Selected Candidates</h3><div class="number">{selected}</div></div>
    </div>
    <div class="panel">
    <h3>About Smart ATS</h3>
    <p>This system helps recruiters manage job openings, applicant details,
    applications and candidate skill matching in one place.</p>
    </div>
    """
    return page(content)

@app.route("/jobs", methods=["GET", "POST"])
def jobs():
    conn = get_db()
    if request.method == "POST":
        conn.execute(
            "INSERT INTO jobs(title,department,skills) VALUES(?,?,?)",
            (request.form["title"], request.form["department"],
             request.form["skills"])
        )
        conn.commit()
        conn.close()
        return redirect(url_for("jobs"))

    rows = conn.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()
    conn.close()
    content = """
    <h2>Manage Jobs</h2>
    <div class="panel">
    <h3>Add New Job</h3>
    <form method="POST">
    <input name="title" placeholder="Job Title" required>
    <input name="department" placeholder="Department">
    <input name="skills" placeholder="Required Skills (Python, SQL)" required>
    <button type="submit">Add Job</button>
    </form></div>
    <div class="panel"><h3>Available Jobs</h3><div class="table-wrap">
    <table><tr><th>ID</th><th>Title</th><th>Department</th><th>Skills</th></tr>
    """
    for r in rows:
        content += f"<tr><td>{r['id']}</td><td>{r['title']}</td><td>{r['department']}</td><td>{r['skills']}</td></tr>"
    content += "</table></div></div>"
    return page(content)

@app.route("/applicants", methods=["GET", "POST"])
def applicants():
    conn = get_db()
    if request.method == "POST":
        conn.execute(
            "INSERT INTO applicants(name,email,skills) VALUES(?,?,?)",
            (request.form["name"], request.form["email"],
             request.form["skills"])
        )
        conn.commit()
        conn.close()
        return redirect(url_for("applicants"))

    rows = conn.execute("SELECT * FROM applicants ORDER BY id DESC").fetchall()
    conn.close()
    content = """
    <h2>Manage Applicants</h2>
    <div class="panel"><h3>Add Applicant</h3>
    <form method="POST">
    <input name="name" placeholder="Full Name" required>
    <input name="email" type="email" placeholder="Email Address" required>
    <input name="skills" placeholder="Skills (Python, SQL)" required>
    <button type="submit">Add Applicant</button>
    </form></div>
    <div class="panel"><h3>Applicant List</h3><div class="table-wrap">
    <table><tr><th>ID</th><th>Name</th><th>Email</th><th>Skills</th></tr>
    """
    for r in rows:
        content += f"<tr><td>{r['id']}</td><td>{r['name']}</td><td>{r['email']}</td><td>{r['skills']}</td></tr>"
    content += "</table></div></div>"
    return page(content)

@app.route("/applications", methods=["GET", "POST"])
def applications():
    conn = get_db()
    if request.method == "POST":
        conn.execute(
            "INSERT INTO applications(applicant_id,job_id,status) VALUES(?,?,?)",
            (request.form["applicant_id"], request.form["job_id"], "Applied")
        )
        conn.commit()
        conn.close()
        return redirect(url_for("applications"))

    people = conn.execute("SELECT * FROM applicants").fetchall()
    jobs_list = conn.execute("SELECT * FROM jobs").fetchall()
    rows = conn.execute("""
        SELECT applications.id, applicants.name, jobs.title, applications.status
        FROM applications
        JOIN applicants ON applicants.id=applications.applicant_id
        JOIN jobs ON jobs.id=applications.job_id
        ORDER BY applications.id DESC
    """).fetchall()
    conn.close()

    content = """
    <h2>Manage Applications</h2>
    <div class="panel"><h3>Create Application</h3>
    <form method="POST"><select name="applicant_id" required>
    <option value="">Select Applicant</option>
    """
    for p in people:
        content += f"<option value='{p['id']}'>{p['name']}</option>"
    content += "</select><select name='job_id' required><option value=''>Select Job</option>"
    for j in jobs_list:
        content += f"<option value='{j['id']}'>{j['title']}</option>"
    content += "</select><button type='submit'>Submit Application</button></form></div>"
    content += """<div class="panel"><h3>Application Records</h3>
    <div class="table-wrap"><table><tr><th>ID</th><th>Applicant</th>
    <th>Job</th><th>Status</th><th>Update Status</th></tr>"""
    for r in rows:
        content += f"""
        <tr><td>{r['id']}</td><td>{r['name']}</td><td>{r['title']}</td>
        <td><span class="tag">{r['status']}</span></td>
        <td><form method="POST" action="/update/{r['id']}">
        <select name="status">
        <option>Applied</option><option>Shortlisted</option>
        <option>Selected</option><option>Rejected</option>
        </select><button>Update</button></form></td></tr>
        """
    content += "</table></div></div>"
    return page(content)

@app.route("/update/<int:application_id>", methods=["POST"])
def update(application_id):
    conn = get_db()
    conn.execute(
        "UPDATE applications SET status=? WHERE id=?",
        (request.form["status"], application_id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("applications"))

@app.route("/matching")
def matching():
    conn = get_db()
    people = conn.execute("SELECT * FROM applicants").fetchall()
    jobs_list = conn.execute("SELECT * FROM jobs").fetchall()
    conn.close()

    content = "<h2>Candidate Skill Matching</h2><p>Matches applicants with jobs based on common skills.</p>"
    if not people or not jobs_list:
        content += "<div class='panel'>Add applicants and jobs first to see skill matches.</div>"
    for p in people:
        for j in jobs_list:
            candidate_skills = {s.strip().lower() for s in p["skills"].split(",")}
            required_skills = {s.strip().lower() for s in j["skills"].split(",")}
            common = candidate_skills & required_skills
            score = round(len(common) / len(required_skills) * 100) if required_skills else 0
            content += f"""
            <div class="panel">
            <h3>{p['name']} → {j['title']}</h3>
            <p>Matching Score: <strong>{score}%</strong></p>
            <p>Matched Skills: {', '.join(common) if common else 'No matching skills yet'}</p>
            </div>
            """
    return page(content)

@app.errorhandler(404)
def not_found(error):
    return page("<h2>Page not found</h2><a href='/'>Go to Dashboard</a>"), 404

init_db()

if __name__ == "__main__":
    app.run(debug=True)
