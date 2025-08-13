
from flask import Blueprint, render_template_string

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    reshaper_available = True
except ImportError:
    reshaper_available = False

status_bp = Blueprint('status', __name__)

def get_reshaped_sample():
    sample = "أكبر لون"
    if reshaper_available:
        try:
            reshaped = arabic_reshaper.reshape(sample)
            reshaped = get_display(reshaped)
            return sample, reshaped
        except Exception as e:
            return sample, f"Reshaping error: {e}"
    return sample, "reshaper not available"

STATUS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>System Status</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f4; color: #333; padding: 40px; }
        .status-box { background: #fff; border-radius: 8px; box-shadow: 0 0 10px #ccc; padding: 30px; max-width: 500px; margin: 40px auto; text-align: center; }
        .ok { color: #4CAF50; font-weight: bold; }
        .fail { color: #f44336; font-weight: bold; }
        .sample { font-size: 1.3em; margin: 10px 0; direction: rtl; }
        .label { font-size: 1em; color: #888; }
    </style>
</head>
<body>
    <div class="status-box">
        <h2>System Status</h2>
        <p>arabic_reshaper: {% if reshaper %}<span class="ok">Available</span>{% else %}<span class="fail">Not Available</span>{% endif %}</p>
        <div>
            <div class="label">Original Urdu:</div>
            <div class="sample">{{ original }}</div>
            <div class="label">After Reshaping:</div>
            <div class="sample">{{ reshaped }}</div>
        </div>
    </div>
</body>
</html>
'''

@status_bp.route("/status")
def system_status():
    original, reshaped = get_reshaped_sample()
    return render_template_string(STATUS_TEMPLATE, reshaper=reshaper_available, original=original, reshaped=reshaped)
