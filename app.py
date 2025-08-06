# app.py

import os
import pandas as pd
import plotly.express as px
from flask import Flask, render_template, request, redirect, url_for

# Initialize Flask app and configure uploads
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/', methods=['GET', 'POST'])
def upload_page():
    """Handles the initial file upload."""
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part. Please go back and select a file."
        file = request.files['file']
        if file.filename == '':
            return "No selected file. Please go back and select a file."

        if file and file.filename.endswith('.csv'):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return redirect(url_for('explorer_page', filename=filename))
        else:
            return "Invalid file type. Please upload a .csv file."

    # For a GET request, just show the upload page
    return '''
    <!doctype html>
    <title>Upload CSV</title>
    <style>
        body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background-color: #f0f2f5; }
        .upload-box { background: #fff; padding: 40px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; }
        h1 { color: #005A9C; }
        input[type=file] { margin-bottom: 20px; }
        input[type=submit] { padding: 10px 20px; background-color: #007BFF; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        input[type=submit]:hover { background-color: #005A9C; }
    </style>
    <div class="upload-box">
        <h1>Interactive Data Explorer</h1>
        <p>Step 1: Upload your CSV file to begin.</p>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file accept=".csv">
          <input type=submit value=Upload>
        </form>
    </div>
    '''

@app.route('/explorer/<filename>', methods=['GET', 'POST'])
def explorer_page(filename):
    """Handles plot generation and displays the data."""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        df = pd.read_csv(filepath)
        columns = df.columns.tolist()
    except Exception as e:
        return f"Error reading CSV file: {e}"

    plot_div = None
    if request.method == 'POST':
        x_axis = request.form.get('x_axis')
        y_axis = request.form.get('y_axis')
        chart_type = request.form.get('chart_type')
        plot_df = df.copy()

        is_date_axis = any(keyword in x_axis.lower() for keyword in ['date', 'time'])
        if is_date_axis:
            plot_df[x_axis] = pd.to_datetime(plot_df[x_axis], errors='coerce')
            plot_df[y_axis] = pd.to_numeric(plot_df[y_axis], errors='coerce')
        elif chart_type in ['scatter', 'line']:
            plot_df[x_axis] = pd.to_numeric(plot_df[x_axis], errors='coerce')
            plot_df[y_axis] = pd.to_numeric(plot_df[y_axis], errors='coerce')

        plot_df.dropna(subset=[x_axis, y_axis], inplace=True)

        if not plot_df.empty:
            if chart_type == 'line' and is_date_axis:
                plot_df = plot_df.sort_values(by=x_axis)
            if chart_type == 'scatter':
                fig = px.scatter(plot_df, x=x_axis, y=y_axis, title=f'{y_axis} vs. {x_axis}')
            elif chart_type == 'bar':
                fig = px.bar(plot_df, x=x_axis, y=y_axis, title=f'{y_axis} by {x_axis}')
            else:
                fig = px.line(plot_df, x=x_axis, y=y_axis, title=f'{y_axis} over {x_axis}')

            plot_div = fig.to_html(full_html=False)

    table_html = df.head(10).to_html(classes='data-table', border=0)

    return render_template('explorer.html', columns=columns, plot_div=plot_div, table_html=table_html, filename=filename)


if __name__ == '__main__':
    app.run(debug=True)
