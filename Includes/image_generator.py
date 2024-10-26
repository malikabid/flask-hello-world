import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import datetime

def generate_images_from_csv(csv_file, language="both"):

    # Create the output directory with a timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    output_dir = f"generated_{timestamp}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read the CSV file
    try:
        if language == "english":
            df = pd.read_csv(csv_file, header=None, encoding="utf-8")
        else:
            df = pd.read_csv(csv_file, delimiter="|", header=None, encoding="utf-8")
    except FileNotFoundError:
        print("CSV file not found.")
        return
    except pd.errors.ParserError:
        print("Error while reading the CSV file.")
        return

    # Set the font size and image size
    font_size = 80
    image_width, image_height = 1080, 260

    try:
        # Load the Arial font for English text
        english_font = ImageFont.truetype("fonts/Arial-Medium.ttf", font_size)
        # Load the Nirmala font for Hindi text
        hindi_font = ImageFont.truetype("fonts/Nirmala.ttf", font_size)
    except IOError:
        print(
            "Required font files not found. Please make sure Arial.ttf and Nirmala.ttf are in the same directory as the script."
        )
        return

    num_images_generated = 0

    for index, row in df.iterrows():
        
        if language == "both":
            if len(row) > 1:
                text_line_1 = row[1].strip()  # First line (Hindi)
                text_line_1 = text_line_1.replace('\t',' ')
            else:
                text_line_1 = ""  # Empty field
            
            text_line_2 = row[0].replace('\t',' ').strip()  # Second line (English)
        elif language == "english":
            text_line_1 = ""
            text_line_2 = row[0].replace('\t',' ').strip()  # Only English text
        else:  # Hindi only
            text_line_1 = row[0].strip().replace('\t',' ')
            text_line_2 = ""

        # Adjust font size if the length of the string is more than 20 characters
        if language != "english" and len(text_line_1) > 20:
            hindi_font = ImageFont.truetype("fonts/Nirmala.ttf", font_size - 10)
        if len(text_line_2) > 20:
            english_font = ImageFont.truetype("fonts/Arial.ttf", font_size - 10)

        # Create a white background image
        image = Image.new("L", (image_width, image_height), color="white")
        draw = ImageDraw.Draw(image)

        # Calculate text sizes and positions
        if language == "both":
            [text_width_1, text_height_1] = hindi_font.font.getsize(text_line_1)[0]
            [text_width_2, text_height_2] = english_font.font.getsize(text_line_2)[0]
            text_height_1 = text_height_1 if text_height_1 > 90 else 90
            total_height = text_height_1 + text_height_2
            position_1 = ((image_width - text_width_1) / 2, (image_height - total_height) / 2)
            position_2 = ((image_width - text_width_2) / 2, (image_height + total_height) / 2 - text_height_2)
        elif language == "english":
            [text_width_2, text_height_2] = english_font.font.getsize(text_line_2)[0]
            position_2 = ((image_width - text_width_2) / 2, (image_height - text_height_2) / 2)
        else:  # Hindi only
            [text_width_1, text_height_1] = hindi_font.font.getsize(text_line_1)[0]
            position_1 = ((image_width - text_width_1) / 2, (image_height - text_height_1) / 2)


         # Draw the texts on the image
        if language != "english":
            draw.text(position_1, text_line_1, fill="black", font=hindi_font)
        if language != "hindi":
            draw.text(position_2, text_line_2, fill="black", font=english_font)


        # Save the image
        image_path = os.path.join(output_dir, f"{index+1}.jpg")
        image.save(image_path)
        num_images_generated += 1

    print("Images have been generated successfully.")
    return output_dir, num_images_generated
