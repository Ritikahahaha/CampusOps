from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/complaint')
def complaint():
    return render_template('complaint.html')

if __name__ == '__main__':
    app.run(debug=True)