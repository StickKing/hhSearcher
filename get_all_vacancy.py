import sys
from time import time
from datetime import datetime
from dateutil.parser import parse
from requests import get as req_get
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import Session
from models import Category
from models import VacanciesHH
from settings import EXPERIENCE, DB_PATH, URL

#Изменяем место вывода
sys.stdout = open('log_set_vac.txt', 'a')

response_count = 0

def get_vacancies(data, category: Category, hh_id: int) -> list[VacanciesHH]:
    """Функция отбирает вакансии которые нужно добавить в БД.
    И возвращает список классов вакансий в ответ"""
    vacancies = []
    for vacanci in data:
        vac_name = vacanci['name'].lower()
        if (all(i in vac_name for i in category.name) and
            vacanci['experience']['name'].lower() in EXPERIENCE and
            vacanci['id'] not in hh_id):
            if vacanci['address'] and vacanci['address']['metro']:
                metro = vacanci['address']['metro'].get('station_name', None)
            else:
                metro = "Метро не указано"
            if vacanci['salary']:
                salary = '{0} до {1} {2}'.format(
                    vacanci['salary']['from'],
                    vacanci['salary']['to'],
                    vacanci['salary']['currency']
                )
            else:
                salary = "ЗП не указана"
            vacancies.append(
                VacanciesHH(
                    hh_id = vacanci['id'],
                    name = vacanci['name'],
                    employer = vacanci['employer']['name'],
                    published_at = parse(vacanci['published_at']),
                    experience = vacanci['experience']['name'],
                    metro_station = metro,
                    salary = salary,
                    url = f"{vacanci['alternate_url']}?from=share_android",
                    category = category
                )
            )
    return vacancies         

def main() -> None:
    """Главная функция"""
    engine = create_engine(f"sqlite:///{DB_PATH}vacancy.db", echo=False)
    with Session(engine) as session:
        #Получаем необходимые для работы данные
        command = select(Category)
        categories = session.scalars(command)
        command = select(VacanciesHH.hh_id)
        hh_id = session.scalars(command)
        hh_id = [str(i) for i in hh_id]

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
                global response_count
                response_count += 1
                if response.status_code == 200:
                    data = response.json()['items']
                    vacancies = get_vacancies(data, category, hh_id)
                    if vacancies:
                        session.add_all(vacancies)
                        session.commit()
                    page += 1
                    pages = response.json()['pages']
                else:
                    print(fr"""{datetime.now()} - {category.name}: 
                          ОШИБКА ЗАПРОСА: {response.status_code} {response.text}""")
                    break

        
if __name__ == '__main__':
    main()
