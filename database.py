from sqlalchemy import create_engine, Column, Integer, String, DateTime, inspect
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

# Обновленный вызов declarative_base() для SQLAlchemy 2.0+
Base = declarative_base()
engine = create_engine("sqlite:///news_bot.db")
Session = sessionmaker(bind=engine)
session = Session()

class RequestLog(Base):
    __tablename__ = 'request_logs'

    id = Column(Integer, primary_key=True)
    command = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

def create_db():
    """Создает базу данных и таблицы, если они не существуют"""
    inspector = inspect(engine)
    if 'request_logs' not in inspector.get_table_names():
        Base.metadata.create_all(engine)
        print("База данных успешно создана.")
    else:
        print("База данных была создана ранее.")

def log_request(command: str):
    """Логирование запросов"""
    log_entry = RequestLog(command=command)
    session.add(log_entry)
    session.commit()

def get_last_request():
    """Получить время последнего запроса"""
    last_entry = session.query(RequestLog).order_by(RequestLog.timestamp.desc()).first()
    return last_entry.timestamp if last_entry else "Нет данных"

# Вызов функции создания базы данных для тестирования
if __name__ == "__main__":
    create_db()
