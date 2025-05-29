from flask import Flask, render_template, request, redirect
import firebase_admin
from firebase_admin import credentials, db
import os

app = Flask(__name__)

# Firebase setup
cred = credentials.Certificate("firebase_key.json")  # JSON file from Firebase console
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://aproval-973fa-default-rtdb.firebaseio.com'
})

@app.route('/')
def index():
    key = request.args.get('key')
    if not key:
        return render_template('index.html', key=None, approved=False)
    ref = db.reference(f'users/{key}')
    data = ref.get()
    if data and data.get("approved"):
        return render_template('index.html', key=key, approved=True)
    else:
        return render_template('index.html', key=key, approved=False)

@app.route('/generate', methods=['POST'])
def generate():
    import random
    key = "FAI-" + ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890", k=8))
    ref = db.reference(f'users/{key}')
    ref.set({ "approved": False })
    return redirect(f"/?key={key}")

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == "FAIZI H3R3":
            users = db.reference('users').get() or {}
            return render_template('admin.html', users=users)
        return "Wrong password!"
    return render_template('admin.html', users=None)

@app.route('/approve/<key>')
def approve(key):
    ref = db.reference(f'users/{key}')
    ref.update({ "approved": True })
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)
