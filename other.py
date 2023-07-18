from sqlalchemy import select
from sqlalchemy.orm import Session
from models import VacanciesHH
from settings import USER_ID


def user_permission(func):
    """Декоратор ограничивающий доступ к
    функциям бота"""
    async def check_permission(*args):
        message_user_id = args[0].message.from_user.id
        if USER_ID == message_user_id:
            return await func(*args)
        else:
            await args[1].bot.send_message(
            chat_id=args[0].effective_chat.id,
            text="Доступ к данному боту запрещён."
        )
    return check_permission

async def view_vacancy(vacancy: list[VacanciesHH]) -> str:
    """Функция формирующая строковое сообщение,
    которое в дальнейшем отправится в чат пользователю"""
    message = []
    for i in vacancy:
        message.append(
            f"<b>{i.name}</b>\n"
            f"🏢 <b>{i.employer}</b>\n"
            f"{i.experience}\n"
            f"💸 {i.salary}\n"
            f"🚇 {i.metro_station}\n"
            f"📅 {i.published_at}\n"
            f"🖥️ <i>{i.url}</i>"
        )
    return '\n\n'.join(message)

async def get_vacancy(id: int, session: Session):
    """Функция получающая запрашиваемые вакансии"""
    command = select(VacanciesHH).where(VacanciesHH.category_id==id).order_by(
        VacanciesHH.published_at
    )
    return session.scalars(command)
