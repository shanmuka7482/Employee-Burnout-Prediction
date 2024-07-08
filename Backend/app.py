from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd

app = Flask(__name__)
CORS(app)  # This will allow all origins by default

# Load the model once when the application starts
linear_regression_model = joblib.load('Burnout_prediction_model.pkl')

@app.route('/submit', methods=['POST'])
def submit():
    # Get form data
    Gender = request.form['Gender']
    Company = request.form['Company']
    WFH = request.form['WFH']
    Designation = request.form['Designation']
    Resource_Allocation = request.form['Resource_Allocation']
    Mental_Fatigue_Score = request.form['Mental_Fatigue_Score']

    Personal_test = {
        'Gender': [Gender],
        'Company Type': [Company],
        "WFH Setup Available": [WFH],
        'Designation': [Designation],
        'Resource Allocation': [Resource_Allocation],
        'Mental Fatigue Score': [Mental_Fatigue_Score],
    }

    Personal_data = pd.DataFrame(data=Personal_test)

    # Check if the columns exist before applying get_dummies
    if all(col in Personal_data.columns for col in ['Company Type', 'WFH Setup Available', 'Gender']):
        Personal_data = pd.get_dummies(Personal_data, columns=['Company Type', 'WFH Setup Available', 'Gender'])
        encoded_columns = Personal_data.columns
    else:
        return jsonify({'error': 'One or more columns are missing in the DataFrame'}), 400

    # Ensure all required columns are present
    required_columns = linear_regression_model.feature_names_in_
    for col in required_columns:
        if col not in Personal_data.columns:
            Personal_data[col] = 0

    Personal_data = Personal_data[required_columns]

    # Make predictions
    y_personal_data = linear_regression_model.predict(Personal_data)

    return jsonify(y_personal_data[0].tolist())

if __name__ == '__main__':
    app.run(debug=True)
