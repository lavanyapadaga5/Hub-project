import plotly.graph_objects as go
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['data_db']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Save the data to MongoDB
        data = {col: request.form[col] for col in request.form}
        db.form_data.insert_one(data)

        return redirect(url_for('index'))

    return render_template('form.html')

@app.route('/excel', methods=['GET', 'POST'])
def excel_upload():
    if request.method == 'POST':
        # Read the uploaded Excel file and save the data to MongoDB
        file = request.files['file']
        if file.filename.endswith('.xlsx'):
            data_df = pd.read_excel(file)
            data = data_df.to_dict(orient='records')
            db.excel_data.insert_many(data)

            return redirect(url_for('index'))

    return render_template('excel_upload.html')

@app.route('/piechart')
def pie_chart():
    # Fetch data from MongoDB for pie charts
    data = list(db.form_data.find({}, {'_id': 0}))

    # Create a list to store pie chart HTML
    pie_charts = []

    # Create a pie chart for each column
    for column in data[0]:
        column_counts = {item[column] for item in data if item[column]}
        labels = list(column_counts)
        values = [len([item for item in data if item[column] == label]) for label in labels]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        pie_chart_html = fig.to_html(full_html=False)
        pie_charts.append(pie_chart_html)

    return render_template('pie_chart.html', pie_charts=pie_charts)

if __name__ == '__main__':
    app.run(debug=True)
