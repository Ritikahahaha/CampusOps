from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = "campusops_secret"

# ================= DATABASE =================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campusops.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ================= MAIL =================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'campusops.project@gmail.com'
app.config['MAIL_PASSWORD'] = 'yivs gieg yqff hddk'  # 🔴 replace with App Password
app.config['MAIL_DEFAULT_SENDER'] = 'campusops.project@gmail.com'

db = SQLAlchemy(app)
mail = Mail(app)

# ================= MODEL =================
class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    category = db.Column(db.String(100))
    issue = db.Column(db.String(500))
    status = db.Column(db.String(50), default="Pending")


# ================= HOME =================
@app.route('/')
def home():
    return render_template("index.html")


# ================= COMPLAINT =================
@app.route('/complaint', methods=['GET', 'POST'])
def complaint():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        category = request.form['category']
        issue = request.form['issue']

        new_c = Complaint(
            name=name,
            email=email,
            category=category,
            issue=issue,
            status="Pending"
        )

        db.session.add(new_c)
        db.session.commit()

        # ================= EMAIL ON SUBMIT =================
        try:
            msg = Message(
                "New Complaint Received",
                recipients=[email]
            )

            msg.body = f"""
New Complaint Received

Name: {name}

Category: {category}

Issue:
{issue}

Status: Pending

--
CampusOps System
"""

            mail.send(msg)

        except Exception as e:
            print("Email error:", e)

        return redirect("/dashboard")

    return render_template("complaint.html")


# ================= ADMIN LOGIN =================
@app.route('/admin', methods=['GET', 'POST'])
def admin():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":
            session['admin'] = True
            return redirect("/dashboard")

        return "Invalid credentials ❌"

    return render_template("admin.html")


# ================= DASHBOARD =================
@app.route('/dashboard')
def dashboard():

    if not session.get('admin'):
        return redirect('/admin')

    complaints = Complaint.query.all()

    total = Complaint.query.count()
    pending = Complaint.query.filter_by(status="Pending").count()
    resolved = Complaint.query.filter_by(status="Resolved").count()

    return render_template(
        "dashboard.html",
        complaints=complaints,
        total=total,
        pending=pending,
        resolved=resolved
    )


# ================= RESOLVE =================
@app.route('/resolve/<int:id>')
def resolve(id):

    c = db.session.get(Complaint, id)

    if c:
        c.status = "Resolved"
        db.session.commit()

        # ================= EMAIL ON RESOLVE =================
        try:
            msg = Message(
                "Complaint Resolved",
                recipients=[c.email]
            )

            msg.body = f"""
Hello {c.name},

Your complaint has been RESOLVED successfully.

Category: {c.category}
Issue:
{c.issue}

Status: Resolved

--
CampusOps System
"""

            mail.send(msg)

        except Exception as e:
            print("Email error:", e)

    return redirect("/dashboard")


# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/admin')


# ================= RUN =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5000, debug=True)