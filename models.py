from typing import List
from typing import Optional
from sqlalchemy import create_engine, select
from sqlalchemy import Integer, String
from sqlalchemy import ForeignKey, DateTime, PickleType
from sqlalchemy.orm import DeclarativeBase 
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from settings import DB_PATH


class Base(DeclarativeBase):
    """Базовая таблица БД. Абстрактный класс."""
    __abstract__ = True

    id: Mapped[int] = mapped_column(nullable=False, 
                unique=True, primary_key=True,
                autoincrement=True)
    create_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

class Category(Base):
    """Таблица категорий искомых вакансий"""
    __tablename__ = "Category"
    name: Mapped[PickleType] = mapped_column(PickleType, nullable=False)
    no_search: Mapped[PickleType] = mapped_column(PickleType, nullable=True)
    vacanciHH: Mapped[List["VacanciesHH"]] = relationship(
        back_populates="category", cascade="all, delete-orphan"
    )

class VacanciesHH(Base):
    """Таблица вакансий с hh"""
    __tablename__ = "VacanciesHH"
    hh_id: Mapped[int] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    employer: Mapped[str] = mapped_column(String(255), nullable=False)
    published_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    experience: Mapped[str] = mapped_column(String(50), nullable=True)
    metro_station: Mapped[str] = mapped_column(String(255), nullable=True)
    salary: Mapped[str] = mapped_column(String(255), nullable=True)
    url: Mapped[str] = mapped_column(nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("Category.id"))
    category: Mapped["Category"] = relationship(back_populates="vacanciHH")

    def __repr__(self) -> str:
        return f"name = {self.name}, employer = {self.employer}, url = {self.url}"
    
if __name__ == "__main__":
    engine = create_engine(f"sqlite:///{DB_PATH}vacancy.db", echo=True) 
    Base.metadata.create_all(engine)
    
    with Session(engine) as session:
        jun = Category(name=['junior'])
        jun_py = Category(name=['junior', 'python'])
        jun_dev = Category(name=['junior', 'devops'])
        jun_sre = Category(name=['junior', 'sre'])
        bac_py = Category(name=['backend', 'python'])
        dev = Category(name=['devops'])
        sre = Category(name=['sre'])
        session.add_all([jun, sre, jun_py, jun_dev, jun_sre, bac_py, dev, sre])
        session.commit()
        command = select(Category)
        cat = session.scalars(command)
        for i in cat:
            print(i.name, ' '.join(i.name))