import sys
from datetime import datetime
from dateutil.parser import parse
from requests import get as req_get
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import Session
from models import Category
from models import Vacancy
from settings import EXPERIENCE, DB_PATH, URL

#Изменяем место вывода
sys.stdout = open('log_set_vac.txt', 'a')


def complete_vacancy(vacancy, category) -> Vacancy:
    if (all(i in vacancy['name'].lower() for i in category.name) and
        vacancy['experience']['name'].lower() in EXPERIENCE):
        if vacancy['address'] and vacancy['address']['metro']:
            metro = vacancy['address']['metro'].get('station_name', None)
        else:
            metro = "Метро не указано"  
        if vacancy['salary']:
            salary = '{0} до {1} {2}'.format(
                vacancy['salary']['from'],
                vacancy['salary']['to'],
                vacancy['salary']['currency']
            )
        else:
            salary = "ЗП не указана"
        new_vac = Vacancy(
            hh_id = vacancy['id'],
            name = vacancy['name'],
            employer = vacancy['employer']['name'],
            published_at = parse(vacancy['published_at']).date(),
            experience = vacancy['experience']['name'],
            metro_station = metro,
            salary = salary,
            url = f"{vacancy['alternate_url']}?from=share_android",
        )
        new_vac.category.append(category)
        return new_vac

def get_vacancies(data, category, session):
    """Функция отбирает вакансии которые нужно добавить в БД.
    И возвращает список классов вакансий в ответ"""
    command = select(Vacancy.hh_id)
    hh_id = session.scalars(command)
    hh_id = tuple(i for i in hh_id)
    vacancies = []
    for vacancy in data:
        
        if (all(i in vacancy['name'].lower() for i in category.name) and
            vacancy['experience']['name'].lower() in EXPERIENCE):
                if int(vacancy['id']) not in hh_id:
                    new_vac = complete_vacancy(vacancy, category)
                    if new_vac:
                        vacancies.append(new_vac)
                else:
                    command = select(Vacancy).where(Vacancy.hh_id==int(vacancy['id']))
                    vac = session.scalar(command)
                    if category not in vac.category:
                        category.vacancy.append(vac)
                        vacancies.append(category)
                
    return vacancies         

def main() -> None:
    """Главная функция"""
    engine = create_engine(f"sqlite:///{DB_PATH}vacancy.db", echo=False)
    with Session(engine) as session:
        #Получаем необходимые для работы данные
        command = select(Category)
        categories = session.scalars(command)

        #Запрашиваем данные
        for category in categories:
            page = 0
            pages = 1
            while page != pages:
                params = {'text': category.name[0], 
                          'area':'1',
                          'per_page':'100', 
                          'page':page
                          }
                response = req_get(URL, params=params)
                global request_count
                request_count += 1
                if response.status_code == 200:
                    data = response.json()['items']
                    vacancies = get_vacancies(data, category, session)
                    if vacancies:
                        session.add_all(vacancies)
                        session.commit()
                    page += 1
                    pages = response.json()['pages']
                else:
                    message_error = '{0} - {1}: ОШИБКА ЗАПРОСА: {2} {3}'.format(
                        datetime.now(),
                        category.name,
                        response.status_code,
                        response.text,
                    )
                    print(message_error)
                    break

        
if __name__ == '__main__':
    main()
