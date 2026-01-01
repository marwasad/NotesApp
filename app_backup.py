from flask import Flask, request, redirect, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = "very-secret-key"  # For production, use a strong random key from environment variable

# Function to get a fresh DB connection per request
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="notesuser",
        password="StrongPassword123",
        database="notesdb"
    )

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if not username or not password:
            return "Username and password are required."

        password_hash = generate_password_hash(password)

        db = get_db()
        cur = db.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, password_hash)
            )
            db.commit()
        except mysql.connector.errors.IntegrityError:
            cur.close()
            db.close()
            return "Username already exists. Choose another."
        cur.close()
        db.close()
        return redirect("/login")

    return """
    <h2>Register</h2>
    <form method="POST">
        Username:<br><input name="username" required><br>
        Password:<br><input type="password" name="password" required><br><br>
        <button>Register</button>
    </form>
    <a href="/login">Already have an account? Login</a>
    """

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        cur.close()
        db.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/")
        return "Invalid credentials. Please try again."

    return """
    <h2>Login</h2>
    <form method="POST">
        Username:<br><input name="username" required><br>
        Password:<br><input type="password" name="password" required><br><br>
        <button>Login</button>
    </form>
    <a href="/register">Don't have an account? Register</a>
    """

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------- DASHBOARD / NOTES ----------
@app.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cur = db.cursor(dictionary=True)

    # Add a new note
    if request.method == "POST":
        note_content = request.form["note"].strip()
        if note_content:
            cur.execute(
                "INSERT INTO notes (user_id, content) VALUES (%s, %s)",
                (session["user_id"], note_content)
            )
            db.commit()

    # Retrieve user-specific notes
    cur.execute(
        "SELECT content, created_at FROM notes WHERE user_id=%s ORDER BY created_at DESC",
        (session["user_id"],)
    )
    notes = cur.fetchall()
    cur.close()
    db.close()

    html = """
    <h2>Welcome, {{ username }}</h2>
    <form method="POST">
        <textarea name="note" required placeholder="Write your note here..." rows="4" cols="50"></textarea><br><br>
        <button>Add Note</button>
    </form>
    <a href="/logout">Logout</a>
    <hr>
    <h3>Your Notes:</h3>
    {% if notes %}
        {% for n in notes %}
            <p><b>{{ n.created_at }}</b><br>{{ n.content }}</p>
            <hr>
        {% endfor %}
    {% else %}
        <p>No notes yet.</p>
    {% endif %}
    """
    return render_template_string(html, notes=notes, username=session["username"])

# ---------- RUN APP ----------
if __name__ == "__main__":
    # Use port 5000 to avoid sudo; change to 80 if you want public access
    app.run(host="0.0.0.0", port=80, debug=True)

