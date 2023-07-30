from typing import List
from sqlalchemy import (
    create_engine,
    select,
    String,
    Table,
    Column,
    ForeignKey,
    DateTime,
    PickleType,
    Date
)
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    Mapped,
    relationship,
    Session,
)
from sqlalchemy.sql import func
from settings import DB_PATH


class Base(DeclarativeBase):
    """Базовая таблица БД. Абстрактный класс."""
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        nullable=False,
        unique=True, primary_key=True,
        autoincrement=True
    )
    create_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )


category_vacancy = Table(
    "category_vacancy",
    Base.metadata,
    Column("category_id", ForeignKey("Category.id"), primary_key=True),
    Column("vacancy_id", ForeignKey("Vacancy.id"), primary_key=True),
)


class Category(Base):
    """Таблица категорий искомых вакансий"""
    __tablename__ = "Category"
    name: Mapped[PickleType] = mapped_column(PickleType, nullable=False)
    vacancy: Mapped[List["Vacancy"]] = relationship(
        secondary=category_vacancy,
        back_populates="category"
    )


class Vacancy(Base):
    """Таблица вакансий с hh"""
    __tablename__ = "Vacancy"
    hh_id: Mapped[int] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    employer: Mapped[str] = mapped_column(String(255), nullable=False)
    published_at: Mapped[Date] = mapped_column(Date)
    experience: Mapped[str] = mapped_column(String(50), nullable=True)
    metro_station: Mapped[str] = mapped_column(String(255), nullable=True)
    salary: Mapped[str] = mapped_column(String(255), nullable=True)
    url: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[List[Category]] = relationship(
        secondary=category_vacancy,
        back_populates="vacancy"
    )

    def __repr__(self) -> str:
        return f"name = {0}, employer = {1}, url = {2}".format(
            self.name,
            self.employer,
            self.url
        )


if __name__ == "__main__":
    engine = create_engine(f"sqlite:///{DB_PATH}vacancy.db", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:

        jun = Category(name=["junior"])
        jun_py = Category(name=["junior", "python"])
        jun_dev = Category(name=["junior", "devops"])
        jun_sre = Category(name=["junior", "sre"])
        bac_py = Category(name=["backend", "python"])
        dev = Category(name=["devops"])
        sre = Category(name=["sre"])
        session.add_all([jun, sre, jun_py, jun_dev, jun_sre, bac_py, dev, sre])
        py = Category(name=["python"])
        session.add_all(
            [jun, sre, jun_py, jun_dev, jun_sre, bac_py, dev, sre, py]
            )
        session.commit()
        command = select(Category)
        cat = session.scalars(command)
        for i in cat:
            print(i.id, i.name, " ".join(i.name))
        command = select(Category).where(Category.id == 1)
        cat = session.scalar(command)
        command = select(Vacancy).where(Vacancy.id == 1)
        vac = session.scalar(command)
