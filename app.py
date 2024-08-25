from flask import Flask, request, jsonify, render_template, send_file
from Includes import image_generator
import os
import datetime
import shutil

app = Flask(__name__)

@app.route('/')
def hello_world():
    # return 'Hello, World! I am coming...'
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    file = request.files.get('file')

    # Save the uploaded file
    if file and file.filename.endswith('.csv'):
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        fileName = f"input_{timestamp}.csv"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], fileName)
        file.save(file_path)
        
        # Generate images from the CSV file
        output_dir, num_images_generated = image_generator.generate_images_from_csv(file_path)
        
        # Create a download link for the generated images
        download_link = f'{output_dir}'
        # download_link = f'{fileName}'
        return jsonify({"status": "success", "message": "File uploaded successfully", "file": file.filename, "download_link": download_link, "num_images_generated": num_images_generated})
    
    else:
        return jsonify({"status": "error", "message": "Invalid file type. Only CSV files are allowed."}), 400

@app.route('/download/<folder>')
def download(folder):
    # Create a zip file of the folder
    shutil.make_archive(folder, 'zip', folder)
    
    # Get the path to the zip file
    zip_file_path = f'{folder}.zip'
    
    # Send the zip file for download
    return send_file(zip_file_path, as_attachment=True)