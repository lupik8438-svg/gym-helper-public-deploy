from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer,
    BigInteger, String, Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(255))
    first_name = Column(String(255))
    phone_number = Column(String(32), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile = relationship("Profile", back_populates="user", uselist=False)
    weight_history = relationship("WeightHistory", back_populates="user")
    completed_workouts = relationship("CompletedWorkout", back_populates="user")
    events = relationship("UserEvent", back_populates="user")
    training_sessions = relationship("TrainingSession", back_populates="user")


class Profile(Base):
    __tablename__ = 'profiles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), unique=True)
    age = Column(Integer)
    gender = Column(String(10))
    height = Column(Float)
    current_weight = Column(Float)
    target_weight = Column(Float)
    activity_level = Column(String(20))
    goal = Column(String(20))
    experience_level = Column(String(20))
    training_days_per_week = Column(Integer, nullable=True)
    sleep_hours = Column(Float, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class WeightHistory(Base):
    __tablename__ = 'weight_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    weight = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="weight_history")


class UserEvent(Base):
    """Единый журнал активности бота, Mini App и сайта."""
    __tablename__ = 'user_events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), index=True)
    event_type = Column(String(64), index=True)
    payload = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="events")


class TrainingSession(Base):
    """Recorded strength/cardio session for monthly user progress."""
    __tablename__ = 'training_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), index=True)
    program_type = Column(String(32), nullable=False)
    session_type = Column(String(16), nullable=False, default='strength')
    duration_minutes = Column(Integer, nullable=False, default=0)
    cardio_minutes = Column(Integer, nullable=False, default=0)
    notes = Column(Text, nullable=True)
    completed_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="training_sessions")


class Supplement(Base):
    __tablename__ = 'supplements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    description = Column(Text)
    dosage_formula = Column(String(500))
    category = Column(String(50))
    contraindications = Column(Text)


class Exercise(Base):
    __tablename__ = 'exercises'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    description = Column(Text)
    muscle_group = Column(String(50))
    exercise_type = Column(String(50))
    equipment = Column(String(100))
    difficulty = Column(String(20))
    video_url = Column(String(500))


class WorkoutProgram(Base):
    __tablename__ = 'workout_programs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    description = Column(Text)
    level = Column(String(20))
    frequency = Column(Integer)
    duration_weeks = Column(Integer)
    goal = Column(String(20))

    workouts = relationship("ProgramWorkout", back_populates="program")


class ProgramWorkout(Base):
    __tablename__ = 'program_workouts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    program_id = Column(Integer, ForeignKey('workout_programs.id'))
    day_number = Column(Integer)
    name = Column(String(255))

    program = relationship("WorkoutProgram", back_populates="workouts")
    exercises = relationship("WorkoutExercise", back_populates="workout")


class WorkoutExercise(Base):
    __tablename__ = 'workout_exercises'

    id = Column(Integer, primary_key=True, autoincrement=True)
    workout_id = Column(Integer, ForeignKey('program_workouts.id'))
    exercise_id = Column(Integer, ForeignKey('exercises.id'))
    sets = Column(Integer)
    reps_min = Column(Integer)
    reps_max = Column(Integer)
    rest_seconds = Column(Integer)
    order_number = Column(Integer)

    workout = relationship("ProgramWorkout", back_populates="exercises")
    exercise = relationship("Exercise")


class UserProgram(Base):
    __tablename__ = 'user_programs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    program_id = Column(Integer, ForeignKey('workout_programs.id'))
    started_at = Column(DateTime, default=datetime.utcnow)
    current_week = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)


class CompletedWorkout(Base):
    __tablename__ = 'completed_workouts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    workout_id = Column(Integer, ForeignKey('program_workouts.id'))
    completed_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)

    user = relationship("User", back_populates="completed_workouts")
    exercises = relationship("CompletedExercise", back_populates="workout")


class CompletedExercise(Base):
    __tablename__ = 'completed_exercises'

    id = Column(Integer, primary_key=True, autoincrement=True)
    completed_workout_id = Column(Integer, ForeignKey('completed_workouts.id'))
    exercise_id = Column(Integer, ForeignKey('exercises.id'))
    set_number = Column(Integer)
    weight = Column(Float)
    reps = Column(Integer)

    workout = relationship("CompletedWorkout", back_populates="exercises")


class FoodLog(Base):
    __tablename__ = 'food_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    photo_path = Column(String(500))
    detected_foods = Column(Text)
    total_calories = Column(Float)
    confirmed = Column(Boolean, default=False)
    logged_at = Column(DateTime, default=datetime.utcnow)
