"""Единый слой данных для Telegram-бота, Mini App, сайта и админ-аналитики."""
import json
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from database.connection import SessionLocal
from database.models import FoodLog, Profile, TrainingSession, User, UserEvent, WeightHistory


def _month_key(value: datetime) -> str:
    return value.strftime('%Y-%m')


def _month_range(months: int = 12) -> List[str]:
    now = datetime.utcnow()
    year, month = now.year, now.month
    result = []
    for _ in range(max(1, months)):
        result.append(f'{year:04d}-{month:02d}')
        month -= 1
        if month == 0:
            month, year = 12, year - 1
    return list(reversed(result))


# ===== USERS =====

def upsert_user(user_id: int, username: str = None, first_name: str = None, phone_number: str = None) -> User:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            user = User(user_id=user_id, username=username, first_name=first_name, phone_number=phone_number)
            db.add(user)
        else:
            if username is not None:
                user.username = username
            if first_name is not None:
                user.first_name = first_name
            if phone_number is not None:
                user.phone_number = phone_number
            user.last_active = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def create_user(user_id: int, username: str = None, first_name: str = None) -> User:
    """Обратная совместимость: теперь создание безопасно идемпотентно."""
    return upsert_user(user_id, username, first_name)


def get_user(user_id: int) -> Optional[User]:
    db = SessionLocal()
    try:
        return db.query(User).filter(User.user_id == user_id).first()
    finally:
        db.close()


def update_user_activity(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            user.last_active = datetime.utcnow()
            db.commit()
    finally:
        db.close()


# ===== PROFILE =====

def create_profile(user_id: int, age: int, gender: str, height: float,
                   current_weight: float, target_weight: float,
                   activity_level: str, goal: str, experience_level: str,
                   training_days_per_week: int = None,
                   sleep_hours: float = None) -> Profile:
    db = SessionLocal()
    try:
        profile = Profile(
            user_id=user_id, age=age, gender=gender, height=height,
            current_weight=current_weight, target_weight=target_weight,
            activity_level=activity_level, goal=goal,
            experience_level=experience_level,
            training_days_per_week=training_days_per_week,
            sleep_hours=sleep_hours,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
    finally:
        db.close()


def get_profile(user_id: int) -> Optional[Profile]:
    db = SessionLocal()
    try:
        return db.query(Profile).filter(Profile.user_id == user_id).first()
    finally:
        db.close()


def update_profile(user_id: int, **kwargs) -> Optional[Profile]:
    db = SessionLocal()
    try:
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if profile:
            for key, value in kwargs.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            profile.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(profile)
            return profile
        return None
    finally:
        db.close()


def has_profile(user_id: int) -> bool:
    return get_profile(user_id) is not None


# ===== EVENTS =====

def create_user_event(user_id: int, event_type: str, payload: Dict = None) -> UserEvent:
    db = SessionLocal()
    try:
        event = UserEvent(
            user_id=user_id,
            event_type=event_type,
            payload=json.dumps(payload or {}, ensure_ascii=False),
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
    finally:
        db.close()


def get_user_events(user_id: int, limit: int = 200) -> List[UserEvent]:
    db = SessionLocal()
    try:
        return db.query(UserEvent).filter(UserEvent.user_id == user_id).order_by(UserEvent.created_at.desc()).limit(limit).all()
    finally:
        db.close()


# ===== WEIGHT HISTORY =====

def create_weight_history(user_id: int, weight: float) -> WeightHistory:
    db = SessionLocal()
    try:
        weight_record = WeightHistory(user_id=user_id, weight=weight)
        db.add(weight_record)
        db.commit()
        db.refresh(weight_record)
    finally:
        db.close()
    create_user_event(user_id, 'weight_logged', {'weight': weight})
    return weight_record


def get_weight_history(user_id: int, limit: int = 30) -> List[WeightHistory]:
    db = SessionLocal()
    try:
        return db.query(WeightHistory).filter(WeightHistory.user_id == user_id).order_by(WeightHistory.recorded_at.desc()).limit(limit).all()
    finally:
        db.close()


# ===== FOOD LOG =====

def create_food_log(user_id: int, photo_path: str, detected_foods: str,
                    total_calories: float, confirmed: bool = False) -> FoodLog:
    db = SessionLocal()
    try:
        food_log = FoodLog(
            user_id=user_id, photo_path=photo_path,
            detected_foods=detected_foods, total_calories=total_calories,
            confirmed=confirmed,
        )
        db.add(food_log)
        db.commit()
        db.refresh(food_log)
    finally:
        db.close()
    if confirmed:
        create_user_event(user_id, 'food_logged', {'calories': total_calories})
    return food_log


def confirm_food_log(log_id: int) -> Optional[FoodLog]:
    db = SessionLocal()
    try:
        food_log = db.query(FoodLog).filter(FoodLog.id == log_id).first()
        if food_log:
            food_log.confirmed = True
            db.commit()
            db.refresh(food_log)
            create_user_event(food_log.user_id, 'food_logged', {'calories': food_log.total_calories})
            return food_log
        return None
    finally:
        db.close()


def get_food_logs_today(user_id: int) -> List[FoodLog]:
    today = date.today()
    db = SessionLocal()
    try:
        return db.query(FoodLog).filter(
            FoodLog.user_id == user_id,
            FoodLog.confirmed == True,
            FoodLog.logged_at >= datetime.combine(today, datetime.min.time()),
            FoodLog.logged_at < datetime.combine(today + timedelta(days=1), datetime.min.time()),
        ).order_by(FoodLog.logged_at.desc()).all()
    finally:
        db.close()


def get_daily_calories(user_id: int) -> float:
    return sum(log.total_calories for log in get_food_logs_today(user_id))


# ===== TRAINING SESSIONS =====

def create_training_session(user_id: int, program_type: str, session_type: str = 'strength',
                            duration_minutes: int = 0, cardio_minutes: int = 0,
                            notes: str = None) -> TrainingSession:
    allowed_programs = {'full_body', 'split', 'upper_lower', 'ppl', 'cardio'}
    if program_type not in allowed_programs:
        raise ValueError('Unknown training program')
    duration_minutes = max(0, min(int(duration_minutes), 600))
    cardio_minutes = max(0, min(int(cardio_minutes), 600))
    db = SessionLocal()
    try:
        session = TrainingSession(
            user_id=user_id, program_type=program_type, session_type=session_type,
            duration_minutes=duration_minutes, cardio_minutes=cardio_minutes,
            notes=(notes or '')[:500],
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    finally:
        db.close()
    create_user_event(user_id, 'training_logged', {
        'program_type': program_type, 'session_type': session_type,
        'duration_minutes': duration_minutes, 'cardio_minutes': cardio_minutes,
    })
    return session


def get_training_sessions(user_id: int, limit: int = 100) -> List[TrainingSession]:
    db = SessionLocal()
    try:
        return db.query(TrainingSession).filter(TrainingSession.user_id == user_id).order_by(
            TrainingSession.completed_at.desc()
        ).limit(limit).all()
    finally:
        db.close()


# ===== ANALYTICS =====

def _get_user_raw_data(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        weights = db.query(WeightHistory).filter(WeightHistory.user_id == user_id).order_by(WeightHistory.recorded_at.asc()).all()
        foods = db.query(FoodLog).filter(FoodLog.user_id == user_id, FoodLog.confirmed == True).order_by(FoodLog.logged_at.asc()).all()
        events = db.query(UserEvent).filter(UserEvent.user_id == user_id).order_by(UserEvent.created_at.asc()).all()
        sessions = db.query(TrainingSession).filter(TrainingSession.user_id == user_id).order_by(TrainingSession.completed_at.asc()).all()
        return user, profile, weights, foods, events, sessions
    finally:
        db.close()


def get_user_monthly_stats(user_id: int, months: int = 12) -> List[Dict]:
    user, profile, weights, foods, events, sessions = _get_user_raw_data(user_id)
    month_keys = _month_range(months)
    result = []
    for key in month_keys:
        month_weights = [x for x in weights if _month_key(x.recorded_at) == key]
        month_foods = [x for x in foods if _month_key(x.logged_at) == key]
        month_events = [x for x in events if _month_key(x.created_at) == key]
        month_sessions = [x for x in sessions if _month_key(x.completed_at) == key]
        active_days = {x.created_at.date().isoformat() for x in month_events}
        active_days.update(x.recorded_at.date().isoformat() for x in month_weights)
        active_days.update(x.logged_at.date().isoformat() for x in month_foods)
        active_days.update(x.completed_at.date().isoformat() for x in month_sessions)
        start_weight = month_weights[0].weight if month_weights else None
        end_weight = month_weights[-1].weight if month_weights else None
        result.append({
            'month': key,
            'label': datetime.strptime(key, '%Y-%m').strftime('%m.%Y'),
            'weight_start': start_weight,
            'weight_end': end_weight,
            'weight_change': round(end_weight - start_weight, 1) if start_weight is not None and end_weight is not None else 0,
            'weight_entries': len(month_weights),
            'food_entries': len(month_foods),
            'training_sessions': len(month_sessions),
            'cardio_minutes': sum(x.cardio_minutes for x in month_sessions),
            'training_minutes': sum(x.duration_minutes for x in month_sessions),
            'calories': round(sum(x.total_calories or 0 for x in month_foods)),
            'active_days': len(active_days),
            'events': len(month_events),
        })
    return result


def get_user_dashboard(user_id: int, months: int = 12) -> Dict:
    user, profile, weights, foods, events, sessions = _get_user_raw_data(user_id)
    monthly = get_user_monthly_stats(user_id, months)
    active_days = set()
    for event in events:
        active_days.add(event.created_at.date())
    for weight in weights:
        active_days.add(weight.recorded_at.date())
    for food in foods:
        active_days.add(food.logged_at.date())
    for session in sessions:
        active_days.add(session.completed_at.date())
    streak = 0
    cursor = date.today()
    while cursor in active_days:
        streak += 1
        cursor -= timedelta(days=1)
    progress = None
    if profile and weights:
        initial = weights[0].weight
        current = weights[-1].weight
        distance = abs(initial - profile.target_weight)
        travelled = abs(initial - current)
        progress = round(min(100, (travelled / distance * 100) if distance else 100), 1)
    achievements = []
    if profile:
        achievements.append({'icon': '🎯', 'title': 'Профиль создан', 'done': True})
    achievements.append({'icon': '🔥', 'title': 'Серия активности 7 дней', 'done': streak >= 7, 'value': streak})
    achievements.append({'icon': '⚖️', 'title': '10 замеров веса', 'done': len(weights) >= 10, 'value': len(weights)})
    achievements.append({'icon': '🍽', 'title': '10 записей питания', 'done': len(foods) >= 10, 'value': len(foods)})
    achievements.append({'icon': '🏋️', 'title': '10 тренировок', 'done': len(sessions) >= 10, 'value': len(sessions)})
    achievements.append({'icon': '🚴', 'title': '300 минут кардио', 'done': sum(x.cardio_minutes for x in sessions) >= 300, 'value': sum(x.cardio_minutes for x in sessions)})
    return {
        'user': {
            'user_id': user.user_id if user else user_id,
            'first_name': user.first_name if user else None,
            'username': user.username if user else None,
            'created_at': user.created_at.isoformat() if user and user.created_at else None,
        },
        'profile': {
            'age': profile.age,
            'gender': profile.gender,
            'height': profile.height,
            'current_weight': profile.current_weight,
            'target_weight': profile.target_weight,
            'activity_level': profile.activity_level,
            'goal': profile.goal,
            'experience_level': profile.experience_level,
            'training_days_per_week': profile.training_days_per_week,
            'sleep_hours': profile.sleep_hours,
        } if profile else None,
        'summary': {
            'streak_days': streak,
            'weight_entries': len(weights),
            'food_entries': len(foods),
            'training_sessions': len(sessions),
            'training_minutes': sum(x.duration_minutes for x in sessions),
            'cardio_minutes': sum(x.cardio_minutes for x in sessions),
            'active_days': len(active_days),
            'goal_progress': progress,
        },
        'achievements': achievements,
        'monthly': monthly,
    }


def get_admin_users(search: str = '', goal: str = '') -> List[Dict]:
    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.last_active.desc()).all()
        rows = []
        search = (search or '').strip().lower()
        for user in users:
            profile = db.query(Profile).filter(Profile.user_id == user.user_id).first()
            if search and search not in str(user.user_id).lower() and search not in (user.username or '').lower() and search not in (user.first_name or '').lower():
                continue
            if goal and (not profile or profile.goal != goal):
                continue
            weights = db.query(WeightHistory).filter(WeightHistory.user_id == user.user_id).order_by(WeightHistory.recorded_at.asc()).all()
            foods = db.query(FoodLog).filter(FoodLog.user_id == user.user_id, FoodLog.confirmed == True).all()
            events = db.query(UserEvent).filter(UserEvent.user_id == user.user_id).all()
            training_sessions = db.query(TrainingSession).filter(TrainingSession.user_id == user.user_id).all()
            initial_weight = weights[0].weight if weights else None
            current_weight = weights[-1].weight if weights else (profile.current_weight if profile else None)
            goal_progress = None
            if profile and initial_weight is not None:
                total = abs(initial_weight - profile.target_weight)
                goal_progress = round(min(100, abs(initial_weight - current_weight) / total * 100), 1) if total else 100
            rows.append({
                'user_id': user.user_id,
                'first_name': user.first_name or 'Без имени',
                'username': user.username,
                'phone_number': user.phone_number,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_active': user.last_active.isoformat() if user.last_active else None,
                'profile_completed': profile is not None,
                'goal': profile.goal if profile else None,
                'current_weight': current_weight,
                'target_weight': profile.target_weight if profile else None,
                'goal_progress': goal_progress,
                'weight_entries': len(weights),
                'food_entries': len(foods),
                'training_sessions': len(training_sessions),
                'cardio_minutes': sum(x.cardio_minutes for x in training_sessions),
                'events': len(events),
            })
        return rows
    finally:
        db.close()


def get_admin_overview(months: int = 12) -> Dict:
    users = get_admin_users()
    db = SessionLocal()
    try:
        events = db.query(UserEvent).all()
        foods = db.query(FoodLog).filter(FoodLog.confirmed == True).all()
        weights = db.query(WeightHistory).all()
        sessions = db.query(TrainingSession).all()
    finally:
        db.close()
    today = date.today()
    active_today = len({event.user_id for event in events if event.created_at.date() == today})
    completed_profiles = sum(1 for user in users if user['profile_completed'])
    progress_values = [x['goal_progress'] for x in users if x['goal_progress'] is not None]
    monthly = []
    for key in _month_range(months):
        month_events = [event for event in events if _month_key(event.created_at) == key]
        month_foods = [food for food in foods if _month_key(food.logged_at) == key]
        month_weights = [weight for weight in weights if _month_key(weight.recorded_at) == key]
        month_sessions = [session for session in sessions if _month_key(session.completed_at) == key]
        monthly.append({
            'month': key,
            'label': datetime.strptime(key, '%Y-%m').strftime('%m.%Y'),
            'new_users': len({event.user_id for event in month_events if event.event_type == 'bot_start'}),
            'active_users': len({event.user_id for event in month_events}),
            'food_entries': len(month_foods),
            'training_sessions': len(month_sessions),
            'cardio_minutes': sum(session.cardio_minutes for session in month_sessions),
            'training_minutes': sum(session.duration_minutes for session in month_sessions),
            'weight_entries': len(month_weights),
            'calories': round(sum(food.total_calories or 0 for food in month_foods)),
        })
    return {
        'totals': {
            'users': len(users),
            'profiles': completed_profiles,
            'active_today': active_today,
            'food_entries': len(foods),
            'weight_entries': len(weights),
            'training_sessions': len(sessions),
            'cardio_minutes': sum(session.cardio_minutes for session in sessions),
            'average_goal_progress': round(sum(progress_values) / len(progress_values), 1) if progress_values else 0,
        },
        'top_users': sorted(users, key=lambda x: (x['goal_progress'] or 0), reverse=True)[:5],
        'monthly': monthly,
    }
