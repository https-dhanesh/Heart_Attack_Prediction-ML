from flask import Flask, render_template, request 
import firebase_admin
from firebase_admin import db, credentials
from flask_mail import Mail, Message
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

app = Flask(__name__)

# Firebase setup
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://hap-project-7fa9f-default-rtdb.asia-southeast1.firebasedatabase.app/"})
ref = db.reference("/")

# Flask-Mail setup
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'gpk2324heartattackprediction@gmail.com'
app.config['MAIL_PASSWORD'] = 'olgh nljx qrjm dsbi'
app.config['MAIL_DEFAULT_SENDER'] = 'gpk2324heartattackprediction@gmail.com'

mail = Mail(app)
df = pd.read_csv('dataset.csv')
labels = df.pop("Output")
x_train, x_test, y_train, y_test = train_test_split(df, labels, test_size=0.25)
rf = RandomForestClassifier()
rf.fit(x_train, y_train)
accuracy = accuracy_score(y_test, rf.predict(x_test))

df1 = pd.read_csv('result_file.csv')
labels1 = df1.pop("Output")
x_train1, x_test1, y_train1, y_test1 = train_test_split(df1, labels1, test_size=0.25)
rf1 = RandomForestClassifier()
rf1.fit(x_train1, y_train1)
accuracy1 = accuracy_score(y_test1, rf1.predict(x_test1))

@app.route("/")
def show_form():
    return render_template('index.html')
@app.route('/submit_form', methods=['POST'])
def submit_form():
    age = int(request.form['age'])
    gender = int(request.form['gender'])
    cp=request.form['chest-pain']
    if cp!="3":
        chestpain=int(request.form['chest-pain-option'])
        print(chestpain)
    else:
        chestpain=cp
    shortness=int(request.form['shortness-of-breath'])
    lightheadness_vomiting = int(request.form['lightheadness-vomiting'])
    heart_rate=request.form['heart-rate']
    cardiac_axis=request.form['cardiac-axis']
    st_segment=request.form['st-segment']
    
    last_record = ref.child("Patients").order_by_key().limit_to_last(1).get()
    if last_record :
        b=list(last_record.keys())
        last_key =int( b[0])
    else:
        last_key = 0
    data = {"age": age, "gender": gender,"chestpain":chestpain,"shortness":shortness,"lightheadness_vomiting":lightheadness_vomiting,
            "heart_rate":heart_rate,"cardiac_axis":cardiac_axis,"st_segment":st_segment}
    
    
   
    if heart_rate=='':
        print("Accuracy:", accuracy1)
    else:
        print("Accuracy:", accuracy)

    if heart_rate=='':
        row=np.array([data['chestpain'],data['shortness'],data['lightheadness_vomiting']]).reshape(1,-1)
        predicted_output = rf1.predict(row)
        print("Predicted output : ",predicted_output)
        probability_estimates = rf1.predict_proba(row)[:, 1]
    else:
        row=np.array([data['chestpain'],data['shortness'],data['lightheadness_vomiting'],data['heart_rate'],data['cardiac_axis'],data['st_segment']]).reshape(1,-1)
        predicted_output = rf.predict(row)
        print("Predicted output : ",predicted_output)
        probability_estimates = rf.predict_proba(row)[:, 1]

   

# Calculate the agreement percentage
    agreement_percentage =(probability_estimates.sum() / len(probability_estimates)) * 85
    print("chance: ",agreement_percentage)
    data = {"age": age, "gender": gender,"chestpain":chestpain,"shortness":shortness,"lightheadness_vomiting":lightheadness_vomiting,
            "heart_rate":heart_rate,"cardiac_axis":cardiac_axis,"st_segment":st_segment,"Output":agreement_percentage}
    print(data)

    nlast_key=last_key +  1
    ref.child("Patients").child(str(nlast_key)).set(data)

    return render_template('index.html', paragraph_text="You have "+(str(agreement_percentage))[:2]+"%"+" chance of Heart Attack")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inner-page')
def inner_page():
    return render_template('inner-page.html')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    name = request.form['name']
    email = request.form['email']
    subject = request.form['subject']
    message=request.form['message']

    # Send email
    subject = 'Feedback from {}'.format(name)
    body = 'Name: {}\nEmail: {}\nFeedback: {}\nMessage: {}'.format(name, email, subject, message)
    print(name,email,subject,message)
    msg = Message(subject, recipients=['gpk2324heartattackprediction@gmail.com'], body=body)
    mail.send(msg)

    return render_template('inner-page.html')

if __name__ == '__main__':
    app.run(debug=True)
