from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures

app = Flask(__name__)
CORS(app, origins=["https://employee-burnout-prediction.onrender.com"])  # Allow requests from your frontend

# Load the model once when the application starts
linear_regression_model = joblib.load('Burnout_prediction_model.pkl')

@app.route('/submit', methods=['POST'])
def submit():
    # Get JSON data
    data = request.get_json()
    
    # Extract fields from JSON data
    Gender = data.get('Gender')
    Company = data.get('Company')
    WFH = data.get('WFH')
    Designation = float(data.get('Designation', 0))
    Resource_Allocation = float(data.get('Resource_Allocation', 0))
    Mental_Fatigue_Score = float(data.get('Mental_Fatigue_Score', 0))

    # Create DataFrame from the received data
    Personal_test = {
        'Gender': [Gender],
        'Company Type': [Company],
        "WFH Setup Available": [WFH],
        'Designation': [Designation],
        'Resource Allocation': [Resource_Allocation],
        'Mental Fatigue Score': [Mental_Fatigue_Score],
    }
    personal_test_df = pd.DataFrame(Personal_test)

    # Check if required columns exist before applying get_dummies
    if all(col in personal_test_df.columns for col in ['Company Type', 'WFH Setup Available', 'Gender']):
        personal_test_df = pd.get_dummies(personal_test_df, columns=['Company Type', 'WFH Setup Available', 'Gender'], dtype=int)
    else:
        return jsonify({"error": "One or more specified columns are missing in the DataFrame"}), 400

    # Multiply specified columns by 2 and create a new column with the sum values
    columns_to_sum = ['Designation', 'Resource Allocation', 'Mental Fatigue Score',
                      'Company Type_Service', 'WFH Setup Available_Yes', 'Gender_Male']
    if all(col in personal_test_df.columns for col in columns_to_sum):
        personal_test_df['Sum_Column'] = personal_test_df[columns_to_sum].apply(lambda x: x * 2).sum(axis=1)
    else:
        return jsonify({"error": "One or more specified columns for summation are missing"}), 400

    # Feature Engineering: Interaction and Polynomial Features
    poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
    poly_features = poly.fit_transform(personal_test_df[columns_to_sum])
    poly_features_df = pd.DataFrame(poly_features, columns=poly.get_feature_names_out(columns_to_sum))
    personal_test_df = pd.concat([personal_test_df, poly_features_df], axis=1)
    
    # Drop duplicate columns
    personal_test_df = personal_test_df.loc[:, ~personal_test_df.columns.duplicated()]

    # Remove columns with less correlation (ensure these columns exist)
    columns_to_drop = ['WFH Setup Available_Yes', 'Designation Mental Fatigue Score', 'Designation Gender_Male',
                       'Resource Allocation Mental Fatigue Score', 'Resource Allocation Gender_Male',
                       'Mental Fatigue Score Company Type_Service', 'Mental Fatigue Score Gender_Male',
                       'Company Type_Service Gender_Male', 'WFH Setup Available_Yes Gender_Male']
    columns_to_drop = [col for col in columns_to_drop if col in personal_test_df.columns]
    personal_test_df = personal_test_df.drop(columns=columns_to_drop, errors='ignore')

    # Predict the values with the model
    predicted_value = linear_regression_model.predict(personal_test_df)
    return jsonify(predicted_value.tolist())

if __name__ == '__main__':
    app.run(debug=True)
