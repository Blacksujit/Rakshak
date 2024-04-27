# from flask import Flask, render_template, request
# from flask_sqlalchemy import SQLAlchemy
# import pandas as pd
# import pymysql
import numpy as np
import os
from flask import Flask , request , render_template , jsonify
import pickle  
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

# create a flask app


app = Flask(__name__)

ps = PorterStemmer()
# os.chdir('data')

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
 


@app.route("/", methods=["GET", 'POST'])
def home():
    return render_template("home.html")


@app.route("/result", methods=['POST'])
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

