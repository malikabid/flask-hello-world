
# --- Refactored code below ---
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, features
import os
import datetime

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    reshaper_available = True
except ImportError:
    reshaper_available = False

FONTS_DIR = "fonts"
FONT_SIZE = 80
IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 260
URDU_FONT_PATH = os.path.join(FONTS_DIR, "NotoNaskhArabic-Regular.ttf")
HINDI_FONT_PATH = os.path.join(FONTS_DIR, "TiroDevanagariHindi-Regular.ttf")
ENGLISH_FONT_PATH = os.path.join(FONTS_DIR, "Arial-Medium.ttf")

def load_font(font_path, size, fallback=None):
    try:
        return ImageFont.truetype(font_path, size)
    except IOError:
        print(f"Warning: {font_path} not found or failed to load. Using fallback font.")
        return fallback if fallback else ImageFont.load_default()

def shape_urdu_text(text):
    if reshaper_available and text:
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        except Exception as e:
            print(f"Urdu reshaping failed: {e}")
            return text
    return text

def extract_text_lines(row, language):
    # Returns (line1, line2) for the given language and row
    if language == "english_hindi":
        hindi = str(row[1]).strip().replace("\t", " ") if len(row) > 1 else ""
        english = str(row[0]).replace("\t", " ").strip()
        return hindi, english
    elif language == "english_urdu":
        urdu = str(row[1]).strip().replace("\t", " ") if len(row) > 1 else ""
        english = str(row[0]).replace("\t", " ").strip()
        return urdu, english
    elif language == "english":
        return "", str(row[0]).replace("\t", " ").strip()
    elif language == "hindi":
        return str(row[0]).strip().replace("\t", " "), ""
    elif language == "urdu":
        return str(row[0]).strip().replace("\t", " "), ""
    else:
        return "", ""

def adjust_font(font_path, base_size, text, threshold=20, fallback=None):
    if len(text) > threshold:
        return load_font(font_path, base_size - 10, fallback)
    return load_font(font_path, base_size, fallback)


def get_text_size(font, text):
    if font is None or not text:
        return 0, 0
    # Use .getsize for compatibility, fallback to .font.getsize if needed
    try:
        return font.getsize(text)
    except Exception:
        return font.font.getsize(text)[0]

def calculate_positions(language, text_line_1, text_line_2, font1, font2):
    # Returns (position_1, position_2, text_width_1, text_height_1, text_width_2, text_height_2)
    text_width_1, text_height_1 = get_text_size(font1, text_line_1)
    text_width_2, text_height_2 = get_text_size(font2, text_line_2)

    if language == "english_hindi":
        text_height_1 = text_height_1 if text_height_1 > 90 else 90
        total_height = text_height_1 + text_height_2
        position_1 = ((IMAGE_WIDTH - text_width_1) / 2, (IMAGE_HEIGHT - total_height) / 2)
        position_2 = ((IMAGE_WIDTH - text_width_2) / 2, (IMAGE_HEIGHT + total_height) / 2 - text_height_2)
        return position_1, position_2, text_width_1, text_height_1, text_width_2, text_height_2
    elif language == "english_urdu":
        text_height_1 = text_height_1 if text_height_1 > 90 else 90
        gap = 15
        total_height = text_height_1 + text_height_2 + gap
        position_1 = ((IMAGE_WIDTH - text_width_1) / 2, (IMAGE_HEIGHT - total_height) / 2 - gap)
        position_2 = ((IMAGE_WIDTH - text_width_2) / 2, (IMAGE_HEIGHT - total_height) / 2 + text_height_1 + gap)
        return position_1, position_2, text_width_1, text_height_1, text_width_2, text_height_2
    elif language == "english":
        position_2 = ((IMAGE_WIDTH - text_width_2) / 2, (IMAGE_HEIGHT - text_height_2) / 2)
        return None, position_2, 0, 0, text_width_2, text_height_2
    elif language == "hindi":
        position_1 = ((IMAGE_WIDTH - text_width_1) / 2, (IMAGE_HEIGHT - text_height_1) / 2)
        return position_1, None, text_width_1, text_height_1, 0, 0
    elif language == "urdu":
        position_1 = ((IMAGE_WIDTH - text_width_1) / 2, (IMAGE_HEIGHT - text_height_1) / 2)
        return position_1, None, text_width_1, text_height_1, 0, 0
    else:
        return None, None, 0, 0, 0, 0

def draw_text_on_image(draw, language, text_line_1, text_line_2, font1, font2, position_1, position_2):
    if language == "hindi" and text_line_1.strip():
        draw.text(position_1, text_line_1, fill=(0,0,0), font=font1)
    elif language == "urdu" and text_line_1.strip():
        draw.text(position_1, text_line_1, fill=(0,0,0), font=font1)
    elif language == "english_hindi":
        if text_line_1.strip():
            draw.text(position_1, text_line_1, fill=(0,0,0), font=font1)
        if text_line_2.strip():
            draw.text(position_2, text_line_2, fill=(0,0,0), font=font2)
    elif language == "english_urdu":
        if text_line_1.strip():
            draw.text(position_1, text_line_1, fill=(0,0,0), font=font1)
        if text_line_2.strip():
            draw.text(position_2, text_line_2, fill=(0,0,0), font=font2)
    elif language == "english" and text_line_2.strip():
        draw.text(position_2, text_line_2, fill=(0,0,0), font=font2)

def generate_images_from_csv(csv_file, language="both"):
    print("Reshaper available:", features.check('raqm'))
    print("Reshaper available:", reshaper_available)

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

    num_images_generated = 0
    for index, row in df.iterrows():
        text_line_1, text_line_2 = extract_text_lines(row, language)

        # Shape Urdu text if needed
        if language in ["urdu", "english_urdu"]:
            text_line_1 = shape_urdu_text(text_line_1)
            print("Shaped Urdu text:", text_line_1)

        # Load/adjust fonts
        if language == "english_hindi":
            font1 = adjust_font(HINDI_FONT_PATH, FONT_SIZE, text_line_1)
            font2 = adjust_font(ENGLISH_FONT_PATH, FONT_SIZE, text_line_2)
        elif language == "english_urdu":
            font1 = adjust_font(URDU_FONT_PATH, FONT_SIZE, text_line_1)
            font2 = adjust_font(ENGLISH_FONT_PATH, FONT_SIZE, text_line_2)
        elif language == "hindi":
            font1 = adjust_font(HINDI_FONT_PATH, FONT_SIZE, text_line_1)
            font2 = None
        elif language == "urdu":
            font1 = adjust_font(URDU_FONT_PATH, FONT_SIZE, text_line_1)
            font2 = None
        elif language == "english":
            font1 = None
            font2 = adjust_font(ENGLISH_FONT_PATH, FONT_SIZE, text_line_2)
        else:
            font1 = font2 = None

        # Create a white background image
        image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), color=(255,255,255))
        draw = ImageDraw.Draw(image)

        # Calculate positions
        position_1, position_2, *_ = calculate_positions(language, text_line_1, text_line_2, font1, font2)

        # Draw text
        draw_text_on_image(draw, language, text_line_1, text_line_2, font1, font2, position_1, position_2)

        # Save the image
        image_path = os.path.join(output_dir, f"{index+1}.jpg")
        image.save(image_path)
        num_images_generated += 1

    print("Images have been generated successfully.")
    return output_dir, num_images_generated
