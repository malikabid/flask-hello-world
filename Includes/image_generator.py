from encodings.punycode import T


try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    reshaper_available = True
except ImportError:
    reshaper_available = False
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, features
import os
import datetime

print("Reshaper available:",features.check('raqm')) 
print("Reshaper available:", reshaper_available)

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
        # Load the Jameel Noori Nastaleeq font for Urdu text with fallback
        try:
            urdu_font = ImageFont.truetype("fonts/NotoNaskhArabic-Regular.ttf", font_size)
        except IOError:
            print("Warning: Jameel-Noori-Nastaleeq-Regular.ttf not found or failed to load. Using default font for Urdu.")
            urdu_font = ImageFont.load_default()
    except IOError:
        print(
            "Required font files not found. Please make sure Arial.ttf, Nirmala.ttf, and Jameel-Noori-Nastaleeq-Regular.ttf are in the fonts directory."
        )
        return

    num_images_generated = 0
    for index, row in df.iterrows():
        if language == "english_hindi":
            if len(row) > 1:
                text_line_1 = row[1].strip()  # First line (Hindi)
                text_line_1 = text_line_1.replace("\t", " ")
            else:
                text_line_1 = ""  # Empty field
            text_line_2 = row[0].replace("\t", " ").strip()  # Second line (English)
        elif language == "english_urdu":
            # Always use the last column for Urdu, first column for English
            text_line_1 = row[1].strip()   # Urdu (last column)
            text_line_2 = row[0].replace("\t", " ").strip()  # Second line (English)
            print("Urdu text:", text_line_1)
            print("Urdu text:", text_line_1)
            print("Extracted Urdu text before reshape:", text_line_1)
            if text_line_1:
                if reshaper_available:
                    try:
                        reshaped_text = arabic_reshaper.reshape(text_line_1)
                        text_line_1 = get_display(reshaped_text)
                        print("Urdu text reshaped:", text_line_1)
                    except Exception as e:
                        print(f"Urdu reshaping failed: {e}")
                else:
                    print("Warning: arabic_reshaper and python-bidi not available. Urdu text may not be connected.")
        elif language == "english":
            text_line_1 = ""
            text_line_2 = row[0].replace("\t", " ").strip()  # Only English text
        elif language == "hindi":
            text_line_1 = row[0].strip().replace("\t", " ")
            text_line_2 = ""
        elif language == "urdu":
            text_line_1 = row[0].strip().replace("\t", " ")
            if reshaper_available:
                try:
                    reshaped_text = arabic_reshaper.reshape(text_line_1)
                    text_line_1 = get_display(reshaped_text)
                    print("Urdu text reshaped:", text_line_1)
                except Exception as e:
                    print(f"Urdu reshaping failed: {e}")
            else:
                print("Warning: arabic_reshaper and python-bidi not available. Urdu text may not be connected.")
            text_line_2 = ""
        else:
            text_line_1 = ""
            text_line_2 = ""

        # Adjust font size if the length of the string is more than 20 characters
        if language == "hindi" and len(text_line_1) > 20:
            hindi_font = ImageFont.truetype("fonts/Nirmala.ttf", font_size - 10)
        if language == "urdu" and len(text_line_1) > 20:
            try:
                urdu_font = ImageFont.truetype("fonts/NotoNaskhArabic-Regular.ttf", font_size - 10)
            except IOError:
                print("Warning: Jameel-Noori-Nastaleeq-Regular.ttf not found or failed to load. Using default font for Urdu.")
                urdu_font = ImageFont.load_default()
        if len(text_line_2) > 20:
            english_font = ImageFont.truetype("fonts/Arial.ttf", font_size - 10)

        # Create a white background image
        image = Image.new("RGB", (image_width, image_height), color=(255,255,255))
        draw = ImageDraw.Draw(image)

        # Calculate text sizes and positions
        if language == "english_hindi":
            [text_width_1, text_height_1] = hindi_font.font.getsize(text_line_1)[0]
            [text_width_2, text_height_2] = english_font.font.getsize(text_line_2)[0]
            text_height_1 = text_height_1 if text_height_1 > 90 else 90
            total_height = text_height_1 + text_height_2
            position_1 = (
                (image_width - text_width_1) / 2,
                (image_height - total_height) / 2,
            )
            position_2 = (
                (image_width - text_width_2) / 2,
                (image_height + total_height) / 2 - text_height_2,
            )
        elif language == "english_urdu":
            [text_width_1, text_height_1] = urdu_font.font.getsize(text_line_1)[0]
            [text_width_2, text_height_2] = english_font.font.getsize(text_line_2)[0]
            text_height_1 = text_height_1 if text_height_1 > 90 else 90
            gap = 15  # vertical gap in pixels between Urdu and English lines
            total_height = text_height_1 + text_height_2 + gap
            position_1 = (
                (image_width - text_width_1) / 2,
                (image_height - total_height) / 2 - gap,  # Adjusted for better centering
            )
            position_2 = (
                (image_width - text_width_2) / 2,
                (image_height - total_height) / 2 + text_height_1 + gap,
            )
        elif language == "english":
            [text_width_2, text_height_2] = english_font.font.getsize(text_line_2)[0]
            position_2 = (
                (image_width - text_width_2) / 2,
                (image_height - text_height_2) / 2,
            )
        elif language == "hindi":
            [text_width_1, text_height_1] = hindi_font.font.getsize(text_line_1)[0]
            position_1 = (
                (image_width - text_width_1) / 2,
                (image_height - text_height_1) / 2,
            )
        elif language == "urdu":
            print("Urdu text:", text_line_1)
            [text_width_1, text_height_1] = urdu_font.font.getsize(text_line_1)[0]
            print("Urdu text font:", urdu_font.font.getsize(text_line_1))
            print("Urdu text width:", text_width_1, "height:", text_height_1)
            position_1 = (
                (image_width - text_width_1) / 2,
                (image_height - text_height_1) / 2,
            )

        # Draw the texts on the image
        if language == "hindi" and text_line_1.strip():
            draw.text(position_1, text_line_1, fill=(0,0,0), font=hindi_font)
        elif language == "urdu" and text_line_1.strip():
            # Draw Urdu text without direction argument (libraqm not available)
            draw.text(position_1, text_line_1, fill=(0,0,0), font=urdu_font)
        elif language == "english_hindi":
            if text_line_1.strip():
                draw.text(position_1, text_line_1, fill=(0,0,0), font=hindi_font)
            if text_line_2.strip():
                draw.text(position_2, text_line_2, fill=(0,0,0), font=english_font)
        elif language == "english_urdu":
            if text_line_1.strip():
                draw.text(position_1, text_line_1, fill=(0,0,0), font=urdu_font)
            if text_line_2.strip():
                draw.text(position_2, text_line_2, fill=(0,0,0), font=english_font)
        elif language == "english" and text_line_2.strip():
            draw.text(position_2, text_line_2, fill=(0,0,0), font=english_font)

        # Save the image
        image_path = os.path.join(output_dir, f"{index+1}.jpg")
        image.save(image_path)
        num_images_generated += 1

    print("Images have been generated successfully.")
    return output_dir, num_images_generated
