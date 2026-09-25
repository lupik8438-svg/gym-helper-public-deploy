from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from bot.config import DEBUG, REQUIRE_WEBAPP_AUTH, WEB_PORT
from core.calculators.bmi import calculate_bmi
from core.calculators.calories import calculate_full_nutrition
from core.calculators.supplements import calculate_supplement_recommendations
from database.connection import init_db
from database.crud import (
    create_user_event, get_food_logs_today, get_profile, get_user, get_user_dashboard,
    get_weight_history, upsert_user, create_training_session, get_training_sessions,
)
from utils.telegram_auth import validate_init_data
from core.workout_programs import WORKOUT_PROGRAMS

app = FastAPI(title="Gym Helper Mini App")
app.mount("/static", StaticFiles(directory="webapp/static"), name="static")
templates = Jinja2Templates(directory="webapp/templates")


@app.on_event('startup')
def startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


def _profile_payload(profile):
    if not profile:
        return None
    return {
        "age": profile.age, "gender": profile.gender, "height": profile.height,
        "current_weight": profile.current_weight, "target_weight": profile.target_weight,
        "activity_level": profile.activity_level, "goal": profile.goal,
        "experience_level": profile.experience_level,
        "training_days_per_week": profile.training_days_per_week,
        "sleep_hours": profile.sleep_hours,
    }


def _resolve_user(request: Request) -> int:
    """Get an authenticated Telegram user, with an explicit local-dev escape hatch."""
    init_data = request.headers.get('X-Telegram-Init-Data', '')
    validated = validate_init_data(init_data)
    if validated:
        telegram_user = validated['user']
        user_id = int(telegram_user['id'])
        upsert_user(user_id, telegram_user.get('username'), telegram_user.get('first_name'))
        return user_id
    if DEBUG:
        dev_id = request.headers.get('X-Gym-User-ID')
        if dev_id and dev_id.isdigit():
            upsert_user(int(dev_id))
            return int(dev_id)
    if not REQUIRE_WEBAPP_AUTH:
        dev_id = request.headers.get('X-Gym-User-ID')
        if dev_id and dev_id.isdigit():
            upsert_user(int(dev_id))
            return int(dev_id)
    raise HTTPException(status_code=401, detail='Открой Mini App из Telegram для авторизации')


def _user_profile_response(user_id: int):
    user = get_user(user_id)
    profile = get_profile(user_id)
    return {
        'user': {
            'user_id': user_id,
            'first_name': user.first_name if user else None,
            'username': user.username if user else None,
        },
        'profile': _profile_payload(profile),
    }


@app.get('/api/me/profile')
async def me_profile(request: Request):
    return _user_profile_response(_resolve_user(request))


@app.get('/api/me/dashboard')
async def me_dashboard(request: Request):
    return get_user_dashboard(_resolve_user(request), months=12)


@app.post('/api/me/events')
async def me_event(request: Request):
    user_id = _resolve_user(request)
    payload = await request.json()
    event_type = payload.get('event_type', 'mini_app_open')
    create_user_event(user_id, event_type, payload.get('payload', {}))
    return {'ok': True}


@app.get('/api/me/calculators/bmi')
async def me_bmi(request: Request):
    profile = get_profile(_resolve_user(request))
    if not profile:
        return {'error': 'Profile not found'}
    return calculate_bmi(profile.current_weight, profile.height)


@app.get('/api/me/calculators/calories')
async def me_calories(request: Request):
    profile = get_profile(_resolve_user(request))
    if not profile:
        return {'error': 'Profile not found'}
    return calculate_full_nutrition(
        weight=profile.current_weight, height=profile.height, age=profile.age,
        gender=profile.gender, activity_level=profile.activity_level, goal=profile.goal,
    )


@app.get('/api/me/calculators/supplements')
async def me_supplements(request: Request):
    profile = get_profile(_resolve_user(request))
    if not profile:
        return {'error': 'Profile not found'}
    return calculate_supplement_recommendations(
        weight=profile.current_weight, goal=profile.goal, activity_level=profile.activity_level,
    )


@app.get('/api/workout-programs')
async def workout_programs():
    return {'programs': WORKOUT_PROGRAMS}


@app.get('/api/me/training')
async def me_training(request: Request):
    rows = get_training_sessions(_resolve_user(request), limit=100)
    return {'sessions': [
        {'id': row.id, 'program_type': row.program_type, 'session_type': row.session_type,
         'duration_minutes': row.duration_minutes, 'cardio_minutes': row.cardio_minutes,
         'notes': row.notes, 'date': row.completed_at.isoformat()}
        for row in rows
    ]}


@app.post('/api/me/training')
async def log_training(request: Request):
    user_id = _resolve_user(request)
    payload = await request.json()
    try:
        session = create_training_session(
            user_id=user_id,
            program_type=payload.get('program_type', 'full_body'),
            session_type=payload.get('session_type', 'strength'),
            duration_minutes=int(payload.get('duration_minutes', 0)),
            cardio_minutes=int(payload.get('cardio_minutes', 0)),
            notes=payload.get('notes', ''),
        )
    except (ValueError, TypeError) as error:
        raise HTTPException(status_code=400, detail=str(error))
    return {'ok': True, 'id': session.id}


@app.get('/api/me/weight-history')
async def me_weight_history(request: Request):
    history = get_weight_history(_resolve_user(request), limit=365)
    return {'history': [{'weight': item.weight, 'date': item.recorded_at.strftime('%Y-%m-%d')} for item in history]}


@app.get('/api/me/food-stats')
async def me_food_stats(request: Request):
    logs = get_food_logs_today(_resolve_user(request))
    return {
        'meals_count': len(logs),
        'total_calories': sum(log.total_calories or 0 for log in logs),
        'logs': [{'calories': log.total_calories, 'time': log.logged_at.strftime('%H:%M')} for log in logs],
    }


# Compatibility endpoints for local tooling. New frontend code uses /api/me/*.
@app.get('/api/profile/{user_id}')
async def get_user_profile(user_id: int):
    return _user_profile_response(user_id)


@app.get('/api/calculators/bmi/{user_id}')
async def calculate_user_bmi(user_id: int):
    profile = get_profile(user_id)
    if not profile:
        return {'error': 'Profile not found'}
    return calculate_bmi(profile.current_weight, profile.height)


@app.get('/api/calculators/calories/{user_id}')
async def calculate_user_calories(user_id: int):
    profile = get_profile(user_id)
    if not profile:
        return {'error': 'Profile not found'}
    return calculate_full_nutrition(
        weight=profile.current_weight, height=profile.height, age=profile.age,
        gender=profile.gender, activity_level=profile.activity_level, goal=profile.goal,
    )


@app.get('/api/calculators/supplements/{user_id}')
async def calculate_user_supplements(user_id: int):
    profile = get_profile(user_id)
    if not profile:
        return {'error': 'Profile not found'}
    return calculate_supplement_recommendations(
        weight=profile.current_weight, goal=profile.goal, activity_level=profile.activity_level,
    )


@app.get('/api/weight-history/{user_id}')
async def get_user_weight_history(user_id: int):
    history = get_weight_history(user_id, limit=365)
    return {'history': [{'weight': item.weight, 'date': item.recorded_at.strftime('%Y-%m-%d')} for item in history]}


@app.get('/api/food-stats/{user_id}')
async def get_food_stats(user_id: int):
    logs = get_food_logs_today(user_id)
    return {
        'meals_count': len(logs),
        'total_calories': sum(log.total_calories or 0 for log in logs),
        'logs': [{'calories': log.total_calories, 'time': log.logged_at.strftime('%H:%M')} for log in logs],
    }


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=WEB_PORT)
