from flask import Blueprint, render_template_string
from PIL import features

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    reshaper_available = True
except ImportError:
    reshaper_available = False

status_bp = Blueprint('status', __name__)

STATUS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>System Status</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f4; color: #333; padding: 40px; }
        .status-box { background: #fff; border-radius: 8px; box-shadow: 0 0 10px #ccc; padding: 30px; max-width: 400px; margin: 40px auto; text-align: center; }
        .ok { color: #4CAF50; font-weight: bold; }
        .fail { color: #f44336; font-weight: bold; }
    </style>
</head>
<body>
    <div class="status-box">
        <h2>System Status</h2>
        <p>arabic_reshaper: {% if reshaper %}<span class="ok">Available</span>{% else %}<span class="fail">Not Available</span>{% endif %}</p>
    </div>
</body>
</html>
'''

@status_bp.route("/status")
def system_status():
    return render_template_string(STATUS_TEMPLATE, reshaper=reshaper_available)
