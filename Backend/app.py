from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, PolynomialFeatures

app = Flask(__name__)
CORS(app,resources={r"/*":{"origins":"http://127.0.0.1:3000"}})  # This will allow all origins by default

# Load the model and scaler once when the application starts
linear_regression_model = joblib.load('Burnout_prediction_model.pkl')

@app.route('/submit', methods=['POST'])
def submit():
    # Get form data
    Gender = request.form['Gender']
    Company = request.form['Company']
    WFH = request.form['WFH']
    Designation = float(request.form['Designation'])
    Resource_Allocation = float(request.form['Resource_Allocation'])
    Mental_Fatigue_Score = float(request.form['Mental_Fatigue_Score'])

    # Create a DataFrame from the form data
    Personal_test = {
        'Gender': [Gender],
        'Company Type': [Company],
        "WFH Setup Available": [WFH],
        'Designation': [Designation],
        'Resource Allocation': [Resource_Allocation],
        'Mental Fatigue Score': [Mental_Fatigue_Score],
    }
    personal_test_df = pd.DataFrame(Personal_test)
        # Check if the columns exist before applying get_dummies
    if all(col in personal_test_df.columns for col in ['Company Type', 'WFH Setup Available', 'Gender']):
        personal_test_df = pd.get_dummies(personal_test_df, columns=['Company Type', 'WFH Setup Available', 'Gender'], dtype=int)
    else:
        print("Error: One or more of the specified columns are not present in the DataFrame.")
        print(personal_test_df.columns)

    # Multiply specified columns by 2 and create a new column with the sum values
    columns_to_sum = ['Designation', 'Resource Allocation', 'Mental Fatigue Score',
                    'Company Type_Service', 'WFH Setup Available_Yes', 'Gender_Male']
    personal_test_df['Sum_Column'] = personal_test_df[columns_to_sum].apply(lambda x: x * 2).sum(axis=1)

    # Feature Engineering: Interaction and Polynomial Features
    poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
    poly_features = poly.fit_transform(personal_test_df[columns_to_sum])
    poly_features_df = pd.DataFrame(poly_features, columns=poly.get_feature_names_out(columns_to_sum))
    personal_test_df = pd.concat([personal_test_df, poly_features_df], axis=1)
    
    # Drop the duplicate column by index
    personal_test_df = personal_test_df.loc[:, ~personal_test_df.columns.duplicated()]

    # Remove columns which has less correlation
    personal_test_df = personal_test_df.drop([ 
        'WFH Setup Available_Yes','Designation Mental Fatigue Score','Designation Gender_Male',
                                  'Resource Allocation Mental Fatigue Score','Resource Allocation Gender_Male',
                                  'Mental Fatigue Score Company Type_Service','Mental Fatigue Score Gender_Male','Company Type_Service Gender_Male',
                                  'WFH Setup Available_Yes Gender_Male'
       ], axis=1)

    # Perdict the values with model
    predicted_value=linear_regression_model.predict(personal_test_df)
    return jsonify(predicted_value.tolist())

if __name__ == '__main__':
    app.run(debug=True)