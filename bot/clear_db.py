from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Настройте строку подключения
DATABASE_URL = "postgresql+asyncpg://wg_forge:42a@localhost/wg_forge_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def clear_database():
    # Удаление всех таблиц
    Base.metadata.drop_all(engine)

if __name__ == "__main__":
    clear_database()
    print("База данных успешно очищена.")