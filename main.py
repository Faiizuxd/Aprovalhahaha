from flask import Flask, request, render_template, redirect
import firebase_admin
from firebase_admin import credentials, firestore
import socket

app = Flask(__name__)

# Load Firebase credentials
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Only this IP can access admin panel
ADMIN_IP = "37.111.145.91"
ADMIN_PASSWORD = "FAIZI H3R3"

@app.route("/")
def home():
    user_ip = request.remote_addr
    device_id = request.headers.get('X-Device-ID') or request.args.get('device_id')
    if not device_id:
        return render_template("approval.html")
    doc_ref = db.collection("approvals").document(device_id)
    doc = doc_ref.get()
    if doc.exists and doc.to_dict().get("status") == "approved":
        return render_template("approved.html")
    return render_template("approval.html", device_id=device_id)

@app.route("/send", methods=["POST"])
def send():
    device_id = request.form.get("device_id")
    if device_id:
        db.collection("approvals").document(device_id).set({"status": "pending"})
    return "<script>alert('Device ID Sent for Approval');window.location.href='/'</script>"

@app.route("/admin-faizi-panel-1000000100003737", methods=["GET", "POST"])
def admin():
    if request.remote_addr != ADMIN_IP:
        return "Access Denied"
    if request.method == "POST":
        if request.form.get("password") != ADMIN_PASSWORD:
            return "Wrong Password"
    users = db.collection("approvals").stream()
    pending = []
    approved = []
    for user in users:
        data = user.to_dict()
        if data.get("status") == "approved":
            approved.append(user.id)
        else:
            pending.append(user.id)
    return render_template("admin.html", pending=pending, approved=approved)

@app.route("/approve/<device_id>")
def approve(device_id):
    if request.remote_addr != ADMIN_IP:
        return "Access Denied"
    db.collection("approvals").document(device_id).set({"status": "approved"})
    return redirect("/admin-faizi-panel-1000000100003737")

@app.route("/reject/<device_id>")
def reject(device_id):
    if request.remote_addr != ADMIN_IP:
        return "Access Denied"
    db.collection("approvals").document(device_id).delete()
    return redirect("/admin-faizi-panel-1000000100003737")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
