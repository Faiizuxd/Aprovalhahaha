from flask import Flask, request, render_template_string
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Flask app
app = Flask(__name__)

# Load Firebase Admin credentials
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ✅ Only this IP can access admin panel
ADMIN_IP = "139.135.45.48"  # 🔁 Replace this with YOUR real IP

# Admin Panel HTML Template
admin_html = '''
<h1>Admin Approval Panel</h1>
<h3>Only visible from Admin IP</h3>
<ul>
{% for doc in docs %}
  <li>
    <strong>{{ doc.id }}</strong> — Status: {{ doc.to_dict().get('status') }}
    {% if doc.to_dict().get('status') == "pending" %}
      <form method="POST" action="/approve/{{ doc.id }}">
        <button>Approve</button>
      </form>
    {% endif %}
  </li>
{% endfor %}
</ul>
'''

# 🔒 Admin Panel Route
@app.route("/admin")
def admin():
    ip = request.remote_addr
    if ip != ADMIN_IP:
        return "Aukat main rahe bsdk owner Tera papa Faizu Hai 🩷.", 403

    docs = db.collection("approvals").stream()
    return render_template_string(admin_html, docs=docs)

# ✅ Approve Key Route
@app.route("/approve/<key>", methods=["POST"])
def approve(key):
    ip = request.remote_addr
    if ip != ADMIN_IP:
        return "❌ Unauthorized Request", 403

    db.collection("approvals").document(key).update({"status": "approved"})
    return f"✅ Approved: {key}"

# 🔑 User asks for key
@app.route("/request_key/<key>")
def request_key(key):
    db.collection("approvals").document(key).set({"status": "pending"})
    return "🔐 Key submitted for approval. Wait for Admin."

# 🔎 Check if key approved
@app.route("/get_key/<key>")
def get_key(key):
    doc = db.collection("approvals").document(key).get()
    if doc.exists and doc.to_dict().get("status") == "approved":
        return "✅ Approved Key - Access Granted"
    else:
        return "⏳ Waiting for Admin Approval"

# Run server on Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
