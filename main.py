from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
import os

app = Flask(__name__)

# Firebase Admin SDK initialization
cred = credentials.Certificate("firebase_key.json")  # Make sure this file exists!
firebase_admin.initialize_app(cred)
db = firestore.client()

# Home page where users see their key and status
@app.route("/")
def home():
    user_ip = request.remote_addr
    key_ref = db.collection("user_keys").document(user_ip)
    key_doc = key_ref.get()

    if key_doc.exists:
        key_data = key_doc.to_dict()
        if key_data.get("status") == "approved":
            return f"<h2>✅ Approved! You may access the app.</h2><p>Key: {key_data.get('key')}</p>"
        else:
            return f"<h3>⏳ Pending Approval...</h3><p>Your key: {key_data.get('key')}</p>"
    else:
        # Generate new key for first-time user
        import uuid
        new_key = str(uuid.uuid4())[:8]
        key_ref.set({"key": new_key, "status": "pending"})
        return f"<h3>🔐 Your key has been generated!</h3><p>Key: {new_key}</p><p>Waiting for admin approval...</p>"

# Admin panel (requires password)
@app.route("/admin", methods=["GET", "POST"])
def admin():
    password = "FAIZI H3R3"  # Change as needed

    if request.method == "POST":
        if request.form.get("password") != password:
            return "<h3>❌ Wrong password</h3>"

        approve_key = request.form.get("approve_key")
        if approve_key:
            # Approve the key
            docs = db.collection("user_keys").stream()
            for doc in docs:
                if doc.to_dict().get("key") == approve_key:
                    db.collection("user_keys").document(doc.id).update({"status": "approved"})
                    return f"<h3>✅ Key '{approve_key}' approved!</h3><a href='/admin'>Back</a>"
            return f"<h3>❌ Key '{approve_key}' not found.</h3><a href='/admin'>Back</a>"

    # Show keys
    pending = []
    approved = []
    docs = db.collection("user_keys").stream()
    for doc in docs:
        d = doc.to_dict()
        if d.get("status") == "approved":
            approved.append(d)
        else:
            pending.append(d)

    return f"""
    <h2>🔐 Admin Panel</h2>
    <form method='POST'>
        <input type='password' name='password' placeholder='Enter admin password' required><br><br>
        <input type='text' name='approve_key' placeholder='Key to approve'>
        <button type='submit'>Approve Key</button>
    </form>
    <br>
    <h3>⏳ Pending Keys:</h3>
    {"<br>".join([k["key"] for k in pending]) or "None"}
    <h3>✅ Approved Keys:</h3>
    {"<br>".join([k["key"] for k in approved]) or "None"}
    """

# Flask app port setup for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
