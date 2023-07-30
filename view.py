from sqlalchemy import select, delete, ScalarResult
from sqlalchemy.orm import Session
from datetime import datetime
from models import Vacancy, Category


class CategoryView():
    """Класс для работы с категориями вакансий"""

    def __init__(self, session: Session) -> None:
        """Инициализация объекта. Принимаем при создании сессию"""
        self._session = session

    async def get_all_category(self) -> ScalarResult:
        """Метод выгружающий из БД все категории и возвращающий
        их в качестве результата"""

        command = select(Category)
        return self._session.scalars(command)
    
    async def set_category(self, message: str) -> str:
        """Метод создания новой категории вакансий"""
        message = message.strip()
        cat_words = message.lower().split()
        if all([word.isalpha() for word in cat_words]):
            self._session.add(
                Category(name=cat_words)
            )
            self._session.commit()
            return f"Новая категория '{message}' успешно создана"
        else:
            return "Ошибка: ключевые слова могут состоять только из букв алфавита"

    async def delete_category_by_id(self, id: int) -> None:
        """Метод удаляющий категорию из БД"""
        command = delete(Category).where(Category.id == id)
        self._session.execute(command)
        self._session.commit()


class VacancyView():
    """Класс для работы с вакансиями"""

    def __init__(self, session: Session) -> None:
        """Инициализация объекта. Принимаем при создании сессию"""
        self._session = session

    def _get_all_vacancy(self, id: int) -> ScalarResult:
        """Метод получающая запрашиваемые вакансии"""
        command = select(Vacancy).where(
            Vacancy.category.any(Category.id==id)
        ).order_by(
            Vacancy.published_at
        )
        return self._session.scalars(command)

    def _view_vacancy(self, vacancy: ScalarResult) -> str:
        """Метод формирующая строковое сообщение,
        которое в дальнейшем отправится в чат пользователю"""
        message = []
        for i in vacancy:
            vac_str = "{0}\n🏢 {1}\n{2}\n💸 {3}\n🚇 {4}\n📅 {5}\n🖥️ {6}".format(
                i.name,
                i.employer,
                i.experience,
                i.salary,
                i.metro_station,
                i.published_at,
                i.url
            )
            message.append(vac_str)
        return "\n\n".join(message)

    async def get_category_vacancy(self, id: int) -> str:
        """Метод возвращающий вакансии определённой категории"""
        vacancy = self._get_all_vacancy(id)
        message = self._view_vacancy(vacancy)
        return message
    
    async def get_today_vacancy_by_id(self, id: int) -> str:
        """Метод получения вакансий заданной 
        категории, опубликованных сегодня"""
        today = datetime.today().date()
        command = select(Vacancy).where(
            Vacancy.category.any(Category.id==id)
        ).where(
            Vacancy.published_at == today
        )
        vacancy = self._session.scalars(command)
        message = self._view_vacancy(vacancy)
        return message
