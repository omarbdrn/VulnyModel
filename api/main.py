from flask import Flask, request, make_response, jsonify
from flask import Response as OrigResponse 
import json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import csv


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/vulnmodel"
db = SQLAlchemy(app)


''' Database Models '''

class Models(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(255), unique=True)
    model_size = db.Column(db.String(2555), unique=True)
    model_accuracy = db.Column(db.String(2555))

    def __init__(self, model_name, model_size, model_accuracy):
        self.model_name = model_name
        self.model_size = model_size
        self.model_accuracy = model_accuracy

class ModelPredictions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(2555), unique=True)
    label = db.Column(db.String(255))
    probabilities = db.Column(db.String(2555))
    is_confirmed = db.Column(db.Boolean)
    file_content = db.Column(db.Text)
    
    def __init__(self, filename, label, probabilities, is_confirmed, file_content):
        self.filename = filename
        self.label = label
        self.probabilities = probabilities
        self.is_confirmed = is_confirmed
        self.file_content = file_content

class Improvements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    register_date = db.Column(db.DateTime)
    accuracy = db.Column(db.String(255))
    eval_count = db.Column(db.Integer)

    def __init__(self, reigster_date, accuracy, eval_count):
        self.register_date = register_date
        self.accuracy = accuracy
        self.eval_count = eval_count

class ValidatedSnippets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True)
    reward = db.Column(db.Integer)

    def __init__(self, filename, reward):
        self.filename = filename
        self.reward = reward

''' API Endpoints '''

def Response(obj, mimetype):
    response = OrigResponse(obj, mimetype=mimetype)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route("/api/model/data", methods=["GET"])
def api_model_data():
    model = Models.query.first()
    modelObj = {"model_name": "", "model_size": "", "model_accuracy": ""}
    if model != None:
        modelObj['model_name'] = model.model_name
        modelObj['model_size'] = model.model_size
        modelObj['model_accuracy'] = model.model_accuracy

    return Response(json.dumps(modelObj), mimetype="application/json")

@app.route('/api/model/snippet', methods=['GET'])
def api_model_snippet():
    snippet = ModelPredictions.query.order_by(ModelPredictions.id).filter_by(is_confirmed=False).first()
    snippetObj = {}
    if snippet != None:
        snippetObj = {"filename":snippet.filename, "file_code":snippet.file_content, "prediction_label":snippet.label, "prediction_probabilities":snippet.probabilities}

    return Response(json.dumps(snippetObj), mimetype="application/json")

@app.route('/api/model/add_snippet', methods=["POST"])
def api_model_add_snippet():
    data = request.get_json()
    filename = data['filename']
    file_content = data['content']
    label = data['label']
    probabilities = data['probabilities']

    snippetObj = ModelPredictions(filename=filename, file_content=file_content, is_confirmed=False, label=label, probabilities=json.dumps(probabilities))
    db.session.add(snippetObj)
    db.session.commit()

    return Response(json.dumps({"success":True}), mimetype="application/json")

@app.route('/api/model/insert-csv', methods=["POST", "OPTIONS"])
def api_model_insert_csv():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    else:
        data = request.get_json()
        filename = data['filename']
        reward = data['reward']

        snippet = ModelPredictions.query.filter_by(filename=filename).first()
        if snippet != None:
            snippet.is_confirmed = True
            valObj = ValidatedSnippets(filename=filename, reward=reward)
            db.session.add(valObj)
            db.session.commit()
    
    return Response(json.dumps({"success":True}), mimetype="application/json")

@app.route('/api/model/save-csv', methods=["GET"])
def api_model_save_csv():
    if request.method == "GET":
        validated_snippets = ValidatedSnippets.query.all()
        with open('training_data.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['functionSource', 'CWE-other', 'combine'])
            for vsnippet in validated_snippets:
                snippet = ModelPredictions.query.filter_by(filename=vsnippet.filename).first()
                functionSource = snippet.file_content
                combine = True
                if vsnippet.reward == 1:
                    combine = False
                writer.writerow([functionSource, combine, combine])

    return Response(json.dumps({"success":True}), mimetype="application/json")

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = "POST,GET"
    return response

app.run(host="127.0.0.1", port=6969, debug=True)