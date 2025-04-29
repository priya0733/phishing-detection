#importing required libraries
from flask import Flask, request, render_template, session, redirect, url_for, flash
import numpy as np
import pandas as pd
from sklearn import metrics 
import warnings
import pickle
import os
warnings.filterwarnings('ignore')
from feature import FeatureExtraction

# Load the pre-trained model
model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
file = open(model_path, "rb")
gbc = pickle.load(file)
file.close()

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
@app.route('/first')
def first():
    return render_template('first.html')

@app.route('/performance')
def performance():
    # Only allow access if logged in
    if not session.get('logged_in'):
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    return render_template('performance.html')

@app.route('/chart')
def chart():
    # Only allow access if logged in
    if not session.get('logged_in'):
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    return render_template('chart.html')    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('pwd')
        
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out!', 'info')
    return redirect(url_for('first'))

@app.route('/index')
def index():
    # Only allow access if logged in
    if not session.get('logged_in'):
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route("/predict", methods=["POST"])
def predict():
    url = request.form["url"]
    obj = FeatureExtraction(url)
    x = np.array(obj.getFeaturesList()).reshape(1, 30) 

    y_pred = gbc.predict(x)[0]
    # Get probabilities
    y_pro_phishing = gbc.predict_proba(x)[0, 0]
    y_pro_non_phishing = gbc.predict_proba(x)[0, 1]
    
    # Pass prediction results to template
    return render_template('result.html', xx=round(y_pro_non_phishing, 2), url=url)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
