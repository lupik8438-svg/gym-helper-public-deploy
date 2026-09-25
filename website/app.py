from io import BytesIO, StringIO
import csv
import hmac
import os
import sys

from flask import Flask, jsonify, render_template, request, Response

# Shared project imports regardless of launch directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.config import ADMIN_KEY
from core.calculators.bmi import calculate_bmi
from core.calculators.calories import calculate_full_nutrition
from core.calculators.supplements import calculate_supplement_recommendations
from core.workout_programs import WORKOUT_PROGRAMS
from database.connection import init_db
from database.crud import get_admin_overview, get_admin_users, get_user_dashboard

app = Flask(__name__)
init_db()


@app.route('/healthz')
def healthz():
    return jsonify({'ok': True, 'service': 'gym-helper-site'})


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/calculator')
def calculator():
    return render_template('calculator.html')


@app.route('/food-scanner')
def food_scanner():
    return render_template('food_scanner.html')


@app.route('/user-progress')
def user_progress():
    return render_template('user_progress.html')


@app.route('/programs')
def programs_page():
    return render_template('programs.html')


@app.route('/api/workout-programs')
def workout_programs_api():
    return jsonify({'programs': WORKOUT_PROGRAMS})


@app.route('/api/calculate/bmi', methods=['POST'])
def api_calculate_bmi():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(calculate_bmi(float(data.get('weight')), float(data.get('height'))))
    except (TypeError, ValueError):
        return jsonify({'error': 'Укажи корректные вес и рост'}), 400


@app.route('/api/calculate/calories', methods=['POST'])
def api_calculate_calories():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(calculate_full_nutrition(
            weight=float(data.get('weight')), height=float(data.get('height')),
            age=int(data.get('age')), gender=data.get('gender'),
            activity_level=data.get('activity_level'), goal=data.get('goal'),
        ))
    except (TypeError, ValueError):
        return jsonify({'error': 'Заполни все поля корректно'}), 400


@app.route('/api/calculate/supplements', methods=['POST'])
def api_calculate_supplements():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(calculate_supplement_recommendations(
            weight=float(data.get('weight')), goal=data.get('goal'),
            activity_level=data.get('activity_level'),
        ))
    except (TypeError, ValueError):
        return jsonify({'error': 'Заполни параметры корректно'}), 400


@app.route('/api/user-dashboard/<int:user_id>')
def api_user_dashboard(user_id: int):
    """Private owner-only analytics; never expose user data by numeric ID."""
    if os.getenv('PUBLIC_DEMO_MODE', 'False').lower() == 'true':
        return jsonify({'error': 'Публичная демо-версия не показывает пользовательские данные'}), 404
    denied = _admin_guard()
    if denied:
        return denied
    return jsonify(get_user_dashboard(user_id, months=12))


def _admin_guard():
    supplied = request.headers.get('X-Admin-Key', '')
    if not ADMIN_KEY or not hmac.compare_digest(supplied, ADMIN_KEY):
        return jsonify({'error': 'Нужен корректный ключ владельца'}), 401
    return None


@app.route('/admin')
def admin():
    if os.getenv('PUBLIC_DEMO_MODE', 'False').lower() == 'true':
        return 'Admin dashboard is disabled in public demo', 404
    return render_template('admin.html')


@app.route('/admin/api/overview')
def admin_overview():
    if os.getenv('PUBLIC_DEMO_MODE', 'False').lower() == 'true':
        return jsonify({'error': 'Disabled on public demo'}), 404
    denied = _admin_guard()
    if denied:
        return denied
    return jsonify(get_admin_overview(months=12))


@app.route('/admin/api/users')
def admin_users():
    if os.getenv('PUBLIC_DEMO_MODE', 'False').lower() == 'true':
        return jsonify({'error': 'Disabled on public demo'}), 404
    denied = _admin_guard()
    if denied:
        return denied
    return jsonify({'users': get_admin_users(request.args.get('search', ''), request.args.get('goal', ''))})


@app.route('/admin/api/export.csv')
def admin_export():
    if os.getenv('PUBLIC_DEMO_MODE', 'False').lower() == 'true':
        return jsonify({'error': 'Disabled on public demo'}), 404
    denied = _admin_guard()
    if denied:
        return denied
    output = StringIO()
    output.write('\ufeff')
    writer = csv.DictWriter(output, fieldnames=[
        'user_id', 'first_name', 'username', 'created_at', 'last_active',
        'profile_completed', 'goal', 'current_weight', 'target_weight',
        'goal_progress', 'weight_entries', 'food_entries', 'events',
    ])
    writer.writeheader()
    writer.writerows(get_admin_users())
    return Response(
        output.getvalue(), mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename=gym-helper-users.csv'},
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
