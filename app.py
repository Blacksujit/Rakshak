# from flask import Flask, render_template, request
# from flask_sqlalchemy import SQLAlchemy
# import pandas as pd
# import pymysql
import numpy as np
import os
from flask import  Flask , request , redirect , url_for , render_template , jsonify
import pickle  
import json
import random
# from  ML_Model import model
import nltk , string
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import pandas as pd
from nltk.tokenize import word_tokenize
from string import punctuation
# importin for spam call functionality
import requests
# from flask import Flask, render_template, request, jsonify
# import requests

# create a flask app


app = Flask(__name__)

ps = PorterStemmer()

# Define your API key
# RAPIDAPI_KEY = "2408f98dfemshf58df2f19cfc556p1a26c5jsnac7fa5db12ad"


#  load the  pickel model

tfidf = pickle.load(open('ML_Model/vectorizer.pkl' , 'rb'))
model = pickle.load(open("ML_Model/model.pkl" , "rb"))



def transform_text(text):
    text=text.lower()
    text=nltk.word_tokenize(text)
    y=[]
    for i in text:
        if i.isalnum():
            y.append(i)
    text=y[:]      
    y.clear()
    for i in text:
        if i not in stopwords.words('english') and i not in string.punctuation:
           y.append(i) 

    text=y[:]
    y.clear()

    for i in text:
        y.append(ps.stem(i))
    return " ".join(y)
 
with open("spam_numbers.json", "r") as f:
    spam_dataset = json.load(f)
    print(spam_dataset)
    
# Initialize a set to store blocked phone numbers
blacklist = set()

def generate_phone_number():
    """
    Generates a random phone number with the country code +91 (India).
    """
    return "+91" + "".join(random.choice("0123456789") for _ in range(10))

def generate_spam_dataset(num_entries):
    """
    Generates a dataset of spam phone numbers in JSON format.
    """
    dataset = []
    for _ in range(num_entries):
        phone_number = generate_phone_number()
        entry = {
            "phone_number": phone_number,
            "spam_status": "Spam",
            "spam_score": random.uniform(0.5, 1.0)
            # Random spam score between 0.5 and 1.0
        }
        dataset.append(entry)
    return dataset

def detect_spam(phone_number):
    for entry in spam_dataset:
        if entry["phone_number"] == phone_number:
            return True, entry["spam_score"]  # Phone number is classified as spam if found in dataset
    return False, 0.0  # Phone number is not classified as spam if not found in dataset
# Function to detect spam calls using TrueCNAM Caller ID API from RapidAPI
# TWILIO_ACCOUNT_SID = "AC86dbc860626d670a54b2aea483c1ea43"
# TWILIO_AUTH_TOKEN = "7faa581aa5b866c5c449a60812b9de4e"

# def detect_spam_twilio(phone_number):
#     try:
#         # Build the Twilio Lookup API URL
#         url = f"https://lookups.twilio.com/v2/PhoneNumbers/{phone_number}"

#         # Set authentication headers
#         auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

#         # Make a POST request to Twilio Lookup API
#         response = requests.get(url, auth=auth)
#         data = response.json()

#         # Check the response status code
#         if response.status_code == 200:
#             # Check if the 'spam_risk' property is present
#             if 'spam_risk' in data:
#                 if data['spam_risk'] == 'high':
#                     return "Spam Call Detected!"
#                 else:
#                     return "Not a Spam Call"
#             else:
#                 return "Error: Spam risk information not available"
#         else:
#             return f"Error: Failed to fetch spam detection result. Status code: {response.status_code}"

#     except Exception as e:
#         return f"Error: {str(e)}"


@app.route("/", methods=["GET", 'POST'])
def home():
    return render_template("home.html")


@app.route('/check_spam' , methods=['POST'])
def check_spam():
    phone_number = request.form['phone_number'] 
    formatted_phone_number = phone_number[3:]
    
   # Check if the entered phone number is in the spam dataset
    is_spam, spam_score = detect_spam(phone_number)
    if is_spam:
        return redirect(url_for('result', phone=phone_number, result="Spam Call Detected!", spam_per=spam_score))
    else:
        return redirect(url_for('result', phone=phone_number, result="Not a Spam Call", spam_per=0.0))

# Function to block phone numbers
def block_phone_number(phone_number):
    # Check if the phone number is already in the blacklist
    if phone_number in blacklist:
        return f"Phone number {phone_number} is already blocked."
    # Add the phone number to the blacklist
    blacklist.add(phone_number)
    return f"Phone number {phone_number} has been blocked."        
         
    # If the phone number is not found in the dataset, consider it not spam
    
    # return redirect(url_for('result', phone=phone_number, result="Not a Spam Call" , spam_per=0.0))
    # return jsonify({"phone_number": phone_number, "spam_score": 0.0, "is_spam": False , "spam_status": "Not Spam"}) 

    # return redirect(url_for('result', phone=phone_number, result=result , spam_per=entry)  )

@app.route('/result', methods=['GET'])
def result():
    phone_number = request.args.get('phone')
    result = request.args.get('result')
    spam_per = request.args.get('spam_per')
    # spam_status = request.args.get('spam_status')
      # Check if a query parameter indicates that the phone number should be blocked
    block_phone_param = request.args.get('block_phone')
    if block_phone_param == 'true' and phone_number:
        # Add the phone number to the blacklist
        blacklist.add(phone_number)
    
    # Example of blocked phone numbers (replace with your logic)
    blocked_numbers = list(blacklist)
    return render_template('spam_result.html', phone_number=phone_number, result=result , spam_per=spam_per  , blocked_numbers=blocked_numbers)
    # return redirect(url_for('result', phone=phone_number, result=result))
   


@app.route('/result', methods=['POST'])
def homer():
    user_input = request.form.get("user_input")
    preprocessed_input = transform_text(user_input)
    vector_input = tfidf.transform([preprocessed_input])
    prediction = model.predict(vector_input)[0]  # Get the first prediction value

    # Check if the prediction is spam or ham
    if prediction == 1:
        spam_count = 1
        ham_count = 0
    else:
        spam_count = 0
        ham_count = 1

    spam_per = 100 if spam_count > ham_count else 0
    ham_per = 100 - spam_per

    return render_template("result.html", spam_count=spam_count, ham_count=ham_count, spam_per=spam_per, ham_per=ham_per)

@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template("about.html")
 
 
       
app.run(debug=True, host="0.0.0.0")





