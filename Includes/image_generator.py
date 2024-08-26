import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import datetime

def generate_images_from_csv(csv_file):
    
    # Create the output directory with a timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    output_dir = f'generated_{timestamp}'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read the CSV file
    try:
        df = pd.read_csv(csv_file, delimiter='|', header=None)
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
        english_font = ImageFont.truetype("fonts/ARIBLK.TTF", font_size)
        # Load the Nirmala font for Hindi text
        hindi_font = ImageFont.truetype("fonts/nirmalab.ttf", font_size)
    except IOError:
        print("Required font files not found. Please make sure Arial.ttf and Nirmala.ttf are in the same directory as the script.")
        return

    num_images_generated = 0

    for index, row in df.iterrows():
        
        if len(row) > 1:
            text_line_1 = row[1].strip()  # First line (Hindi)
            text_line_1 = text_line_1.replace('\t',' ')  # First line (Hindi)
        else:
            text_line_1 = ""  # Empty field  # First line (Hindi)
        
        text_line_2 = row[0].replace('\t',' ').strip()  # Second line (English)
        
        # Adjust font size if the length of the string is more than 20 characters
        if len(text_line_1) > 20:
            hindi_font = ImageFont.truetype("fonts/nirmalab.ttf", font_size - 10)
        if len(text_line_2) > 20:
            english_font = ImageFont.truetype("fonts/ARIBLK.TTF", font_size - 10)
        
        # Create a white background image
        image = Image.new('L', (image_width, image_height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Calculate text sizes
        text_width_1, text_height_1 = draw.textsize(text_line_1, font=hindi_font)
        text_width_2, text_height_2 = draw.textsize(text_line_2, font=english_font)
        
        # Calculate total height needed for both lines
        total_height = text_height_1 + text_height_2
        
        # Calculate positions for the texts to be centered horizontally and vertically
        position_1 = ((image_width - text_width_1) / 2, (image_height - total_height) / 2)
        position_2 = ((image_width - text_width_2) / 2, (image_height + total_height) / 2 - text_height_2)
        
        # Draw the texts on the image
        draw.text(position_1, text_line_1, fill='black', font=hindi_font)
        draw.text(position_2, text_line_2, fill='black', font=english_font)
        
        # Save the image
        image_path = os.path.join(output_dir, f'{index+1}.jpg')
        image.save(image_path)
        num_images_generated += 1

    print("Images have been generated successfully.")
    return output_dir, num_images_generated
