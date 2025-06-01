from flask import Flask, render_template, request, redirect
import firebase_admin
from firebase_admin import credentials, firestore
import socket

app = Flask(__name__)

# Load Firebase credentials
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Admin IP
ADMIN_IP = "37.111.145.91"

@app.route("/")
def home():
    device_id = request.remote_addr
    doc_ref = db.collection("devices").document(device_id)
    doc = doc_ref.get()

    if doc.exists:
        data = doc.to_dict()
        if data.get("approved"):
            return render_template("approved.html")
        else:
            return render_template("approval.html", device_id=device_id)
    else:
        doc_ref.set({"approved": False})
        return render_template("welcome.html", device_id=device_id)

@app.route("/send", methods=["POST"])
def send():
    return redirect("https://www.facebook.com/The.Unbeatble.Stark")

@app.route("/send2", methods=["POST"])
def send2():
    return redirect("https://www.facebook.com/asadmeer.645927")

@app.route("/admin-faizi-panel-1000000100003737")
def admin():
    if request.remote_addr != ADMIN_IP:
        return "Access Denied"
    
    devices = db.collection("devices").get()
    pending = []
    approved = []

    for doc in devices:
        item = {"id": doc.id}
        if doc.to_dict().get("approved"):
            approved.append(item)
        else:
            pending.append(item)

    return render_template("admin.html", pending=pending, approved=approved)

@app.route("/approve/<device_id>")
def approve(device_id):
    if request.remote_addr != ADMIN_IP:
        return "Access Denied"
    
    db.collection("devices").document(device_id).update({"approved": True})
    return redirect("/admin-faizi-panel-1000000100003737")

@app.route("/reject/<device_id>")
def reject(device_id):
    if request.remote_addr != ADMIN_IP:
        return "Access Denied"
    
    db.collection("devices").document(device_id).delete()
    return redirect("/admin-faizi-panel-1000000100003737")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
