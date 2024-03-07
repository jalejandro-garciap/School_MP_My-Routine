from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session
from database.models import Passenger, History, Station
from database.connection import engine

def get_passenger_by_card_id(card_id):
    with Session(engine) as session:
        return session.query(Passenger).filter(Passenger.card_id == card_id).first()

def has_exercised_today(passenger_id):
    with Session(engine) as session:
        today_count = session.query(History).filter(
            History.passenger_id == passenger_id,
            History.date == date.today()
        ).count()
        return today_count > 0

def get_station_by_name(name):
    with Session(engine) as session:
        return session.query(Station).filter(Station.name == name).first()
    
def recharge_passenger_balance(passenger, amount=9.5):
    with Session(engine) as session:
        try:
            session.add(passenger)
            passenger.balance += amount
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            #print(f"Error updating passenger balance: {e}")
            return False
    
def get_max_history_id(session):
    max_id = session.query(func.max(History.id)).scalar()
    return max_id or 0

def insert_history_record(challenge_completed, duration, exercise, repetitions_done, target_reps, passenger_id, station_id):
    with Session(engine) as session:
        new_history = History(
            id=get_max_history_id(session)+1,
            challenge_completed=challenge_completed,
            date=date.today(),
            duration=duration,
            exercise=exercise,
            repetitions_done=repetitions_done,
            target_reps=target_reps,
            passenger_id=passenger_id,
            station_id=station_id
        )
        try:
            session.add(new_history)
            session.commit()            
            return new_history.id
        except Exception as e:
            session.rollback()
            #print(f"Error inserting into history: {e}")
            return None
