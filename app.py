from flask import Flask, request, jsonify, render_template, send_file
from Includes import image_generator
import os
import csv
import datetime
import shutil

app = Flask(__name__)

# Ensure the upload folder exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def hello_world():
    # return 'Hello, World! I am coming...'
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    file = request.files.get("file")
    language_option = request.form.get("languageOption", "both")

    # Save the uploaded file
    if file and file.filename.endswith(".csv"):
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        fileName = f"input_{timestamp}.csv"
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], fileName)
        file.save(file_path)

        # Generate images from the CSV file
        # output_dir = f'{UPLOAD_FOLDER}/{timestamp}' # for debugging purpose
        output_dir, num_images_generated = image_generator.generate_images_from_csv(
            file_path, language=language_option
        )

        # Create a download link for the generated images
        download_link = f"{output_dir}"
        # download_link = f'{fileName}'
        return jsonify(
            {
                "status": "success",
                "message": "File uploaded successfully",
                "file": file.filename,
                "download_link": download_link,
                "num_images_generated": num_images_generated,
            }
        )

    else:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Invalid file type. Only CSV files are allowed.",
                }
            ),
            400,
        )


@app.route("/submit_textarea", methods=["POST"])
def submit_textarea():
    csv_data = request.form.get("csvTextarea")
    language_option = request.form.get("languageOption", "both")

    if not csv_data:
        return jsonify({"status": "error", "message": "No CSV data provided."}), 400

    try:
        # Create a timestamped filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"input_{timestamp}.csv"
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        # Save the CSV data to a file
        with open(file_path, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            reader = csv.reader(csv_data.splitlines())
            for row in reader:
                writer.writerow(row)

        # Process the CSV data as needed

        # Generate images from the CSV file
        # output_dir = f'{UPLOAD_FOLDER}/{timestamp}' # for debugging purpose
        output_dir, num_images_generated = image_generator.generate_images_from_csv(
            file_path, language=language_option
        )

        # Create a download link for the generated images
        download_link = f"{output_dir}"
        # download_link = f'{fileName}'
        return jsonify(
            {
                "status": "success",
                "message": "File uploaded successfully",
                "file": filename,
                "download_link": download_link,
                "num_images_generated": num_images_generated,
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/download/<folder>")
def download(folder):
    # Create a zip file of the folder
    shutil.make_archive(folder, "zip", folder)

    # Get the path to the zip file
    zip_file_path = f"{folder}.zip"

    # Send the zip file for download
    return send_file(zip_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5500)