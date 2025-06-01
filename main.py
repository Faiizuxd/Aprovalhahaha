from flask import Flask, request, render_template_string, redirect
import firebase_admin
from firebase_admin import credentials, firestore
import socket

# Replace with your IP
ADMIN_IP = "139.135.45.48"

# Initialize Firebase
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)

@app.route("/")
def index():
    user_ip = request.remote_addr
    key = request.args.get("key")
    if not key:
        return "🔑 No key provided."

    doc_ref = db.collection("users").document(key)
    doc = doc_ref.get()

    if not doc.exists:
        doc_ref.set({"status": "pending", "ip": user_ip})
        return "⏳ Your key is pending approval."

    data = doc.to_dict()
    if data.get("status") == "approved":
        return "✅ Approved! You may continue."
    return "⏳ Still pending approval."

@app.route("/admin")
def admin():
    user_ip = request.remote_addr
    if user_ip != ADMIN_IP:
        return "⛔ Access Denied. You're not the admin."

    users = db.collection("users").stream()
    html = "<h2>Admin Panel</h2><ul>"
    for u in users:
        d = u.to_dict()
        html += f"<li>{u.id} - {d.get('status')} - <a href='/approve/{u.id}'>Approve</a></li>"
    html += "</ul>"
    return html

@app.route("/approve/<key>")
def approve_key(key):
    user_ip = request.remote_addr
    if user_ip != ADMIN_IP:
        return "⛔ Not allowed."
    db.collection("users").document(key).update({"status": "approved"})
    return redirect("/admin")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
