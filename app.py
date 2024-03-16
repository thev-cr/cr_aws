import os
import certifi
import pymongo
from flask import Flask, request, jsonify
import pandas as pd
from joblib import load
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

universities = []
courses = []


def connect():
    # MongoDB connection parameters
    mongo_uri = os.environ.get('MONGO_URI')

    # Connect to MongoDB
    client = pymongo.MongoClient('mongo_uri', tlsCAFile=certifi.where())
    db = client.imaginary
    client.admin.command('ping')
    print('Connected to db')

    collection_name = "universities"
    collection = db[collection_name]

    collection_name_c = "courses"
    collection_c = db[collection_name_c]

    cursor = collection.find({})
    documents = list(cursor)

    cursor_c = collection_c.find({})
    documents_c = list(cursor_c)

    return documents, documents_c


universities, courses = connect()


@app.route('/')
def index():
    return "You have reached the Homepage of AI Predictions for CampusRoot EduTech Pvt. Ltd."


# Function to predict university rating
def predict_uni_rating(ug_gpa, gre):
    # Load the model
    pipeline = load('knn_regressor_model.joblib')
    input_data = pd.DataFrame({'ug_gpa': [ug_gpa], 'gre': [gre], 'status': 'Accepted'})  # status is dummy here
    predicted_rating = pipeline.predict(input_data)[0]
    return predicted_rating


# Endpoint for processing requests
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    ug_gpa = data.get('ug_gpa')
    gre = data.get('gre')
    chosen_sub_disciplines = data.get('sub_discipline', [])

    if not isinstance(chosen_sub_disciplines, list):
        chosen_sub_disciplines = [chosen_sub_disciplines.strip()]
    else:
        chosen_sub_disciplines = [sub.strip() for sub in chosen_sub_disciplines]

    # Predict the university rating
    predicted_rating = predict_uni_rating(ug_gpa, gre)

    # Function to categorize university
    def categorize_university(uni_rating, predicted_rating):
        if predicted_rating - 1 <= uni_rating < predicted_rating - 0.35:
            return 'Safe'
        elif predicted_rating - 0.35 <= uni_rating <= predicted_rating + 0.25:
            return 'Moderate'
        elif predicted_rating + 0.25 < uni_rating <= predicted_rating + 1:
            return 'Ambitious'
        return 'Outside Range'

    matching_universities = {}
    for uni in universities:
        uni_rating = uni.get('uni_rating')
        if uni_rating is None:
            uni_rating = 6
        if uni_rating is not None:
            category = categorize_university(uni_rating, predicted_rating)
            if category != 'Outside Range':
                matching_universities[str(uni['_id'])] = {'name': uni['name'], 'category': category}

    matching_courses_by_sub_discipline = {sub: [] for sub in chosen_sub_disciplines}

    for course in courses:
        try:
            # Directly compare subDiscipline with chosen sub-disciplines
            if str(course['university']) in matching_universities and course['subDiscipline'].strip() in chosen_sub_disciplines:
                # Add the course to the list of matching courses for each sub-discipline it matches
                for sub_discipline in chosen_sub_disciplines:
                    if course['subDiscipline'].strip() == sub_discipline:
                        matching_courses_by_sub_discipline[sub_discipline].append({
                            "Course": course['name'],
                            "University": matching_universities[str(course['university'])]['name'],
                            "Category": matching_universities[str(course['university'])]['category'],
                            "CID": str(course['_id'])
                        })
        except KeyError:
            # If a KeyError occurs, skip this course and continue with the next
            print(f"Skipping course with ID {str(course['_id'])} due to missing university data.")
            continue

    # Convert output data to JSON
    output_json = jsonify(matching_courses_by_sub_discipline)
    return output_json


if __name__ == '__main__':
    app.run(debug=False)
