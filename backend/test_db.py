# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Создаем базовый класс для моделей
Base = declarative_base()

# Простая модель для теста
class TestOrg(Base):
    __tablename__ = "test_org"
    id = Column(Integer, primary_key=True)
    name = Column(String)

# Подключаемся к базе
engine = create_engine("postgresql://postgres:QAZwsxr$t5@localhost/ofs_db_new")

try:
    # Создаем таблицы
    Base.metadata.create_all(engine)

    # Создаем сессию
    Session = sessionmaker(bind=engine)
    session = Session()

    # Пробуем создать запись
    test_org = TestOrg(name="Test Org")
    session.add(test_org)
    session.commit()

    # Проверяем что создалось
    result = session.query(TestOrg).first()
    print(f"Created org: {result.name}")

except Exception as e:
    print(f"Error: {str(e)}")