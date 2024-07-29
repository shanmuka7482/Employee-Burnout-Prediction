from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, PolynomialFeatures, OneHotEncoder

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

    # changing into DataFrame

    personal_test_df = pd.DataFrame(Personal_test)
    
    # devideing into two parts which need dummy values and which does not need dummy values
    data_dummy_values = personal_test_df.drop(['Designation', 'Resource Allocation', 'Mental Fatigue Score'  ], axis=1)
    data_Not_required_dummy_values=personal_test_df.drop(['Gender', 'Company Type', 'WFH Setup Available'], axis=1)

    print(f"data_dummy_values.columns: {data_dummy_values.columns}")
    print(f"data_Not_required_dummy_values.columns: {data_Not_required_dummy_values.columns}")


    # Check if the columns exist before applying get_dummies
    if all(col in data_dummy_values.columns for col in ['Company Type', 'WFH Setup Available', 'Gender']):
        data_dummy_values = pd.get_dummies(data_dummy_values, columns=['Company Type', 'WFH Setup Available', 'Gender'], drop_first=False, dtype=int)
        encoded_columns = data_dummy_values.columns
    else:
        print("Error: One or more of the specified columns are not present in the DataFrame.")
        print(data_dummy_values.columns)

    all_columns = ['Company Type_Product', 'Company Type_Service',
                    'WFH Setup Available_No', 'WFH Setup Available_Yes',
                    'Gender_Female', 'Gender_Male']

    # Add missing columns with default values of 0
    for col in all_columns:
        if col not in data_dummy_values.columns:
            data_dummy_values[col] = 0
        
    # Ensure columns are in the correct order
    data_dummy_values = data_dummy_values[all_columns]


    # combining the columns
    data = pd.concat([data_dummy_values, data_Not_required_dummy_values], axis=1) 




    # Multiply specified columns by 2 and create a new column with the sum values
    columns_to_sum = ['Company Type_Product', 'Company Type_Service',
        'WFH Setup Available_No', 'WFH Setup Available_Yes', 'Gender_Female',
        'Gender_Male', 'Designation', 'Resource Allocation',
        'Mental Fatigue Score']
    data['Sum_Column'] = data[columns_to_sum].apply(lambda x: x * 2).sum(axis=1)




    # Feature Engineering: Interaction and Polynomial Features
    poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
    poly_features = poly.fit_transform(data[columns_to_sum])
    poly_features_df = pd.DataFrame(poly_features, columns=poly.get_feature_names_out(columns_to_sum))
    data = pd.concat([data, poly_features_df], axis=1)


        
    # Drop the duplicate column by index
    data_cleaned = data.loc[:, ~data.columns.duplicated()]

    # Perdict the values with model
    predicted_value=linear_regression_model.predict(data_cleaned)


    return jsonify(predicted_value.tolist())

if __name__ == '__main__':
    app.run(debug=True)

