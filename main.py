import logging
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    KeyboardButton, 
    ReplyKeyboardMarkup,
    KeyboardButtonPollType
    )
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    CallbackQueryHandler,
    ConversationHandler
    )
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import Session
from models import Category
from other import user_permission, view_vacancy, get_vacancy
from settings import DB_PATH, TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)


async def vacancy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция создающая кнопки категорий.
    Выгружает данные из такблицы категорий и преобразуя
    в читаемый вид возвращает кнопки в самом чате."""  
    command = select(Category)
    category = session.scalars(command)
    """Список нужных кнопок"""
    keyboard = []
    for i in category:
        keyboard.append(
            InlineKeyboardButton(' '.join(i.name), callback_data=i.id),
        )
    value = len(keyboard) // 2
    keyboard = list(zip(keyboard[:value], keyboard[value:]))

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выбери категорию:", reply_markup=reply_markup)

async def buttons_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция обрабатывабщая нажатие кнопок из vacancy_menu."""
    query = update.callback_query

    await query.answer()
    vacancy = await get_vacancy(query.data, session)
    message = await view_vacancy(vacancy)

    while message:
        await update.effective_message.reply_html(message[:4050])
        message = message[4050:]

@user_permission
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция с которой начинается взаимодействие с ботом. 
    Создаёт кнопки под строкой ввода в чате."""
    button1 = [
        [KeyboardButton("Категории вакансий")],
        [KeyboardButton("Добавить новую категорию")]
        ]
    menu_button = ReplyKeyboardMarkup(button1, resize_keyboard=True)
    await update.effective_message.reply_text("Добро пожаловать!", reply_markup=menu_button)

@user_permission
async def text_processing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция обработки вводимых текстовых сообщений.
    Реализует работу с кнопками на русском языке."""
    if update.message.text == "Категории вакансий":
        await vacancy_menu(update, context)
    elif update.message.text == 'Добавить новую категорию':
        pass
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Такой команды нет {type(update.message.from_user.id)}"
        )


if __name__ == '__main__':

    engine = create_engine(f"sqlite:///{DB_PATH}vacancy.db", echo=False)
    session = Session(engine)

    new_category = []
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    text_processing_handler = MessageHandler(filters.ALL, text_processing)
    buttons_click_handler = CallbackQueryHandler(buttons_click)
    
    application.add_handler(start_handler)
    application.add_handler(buttons_click_handler)
    application.add_handler(text_processing_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)