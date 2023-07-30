import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from tools import user_permission
from settings import DB_PATH, TOKEN
from view import VacancyView, CategoryView


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.ERROR
)

ANY_ID = None


async def reply_text_vacancy(update: Update, message: str):
    count = 0
    if not message:
        message = "По данному запросу вакансии не найдены"
    try:
        while message or count == 30:
            await update.effective_message.reply_text(message[:4050])
            message = message[4050:]
            count += 1
    except Exception as e:
        await update.effective_message.reply_text(f"Ошибка {e}")


async def vacancy_menu(update: Update):
    """Функция создающая кнопки категорий."""

    category = await category_view.get_all_category()

    # Создание клавиатуры
    buttons = []
    for i in category:
        buttons.append(
            InlineKeyboardButton(" ".join(i.name), callback_data=i.id),
        )
    key_len = len(buttons)
    value = key_len // 2
    keyboard = list(zip(buttons[:value], buttons[value:]))
    if key_len - value * 2 != 0:
        keyboard.append((buttons[-1], ))

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Выбери категорию:",
        reply_markup=reply_markup
    )


async def buttons_click(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """Функция обрабатывабщая нажатие кнопок из vacancy_menu."""
    query = update.callback_query
    await query.answer()

    buttons_name = (
        "Сегодняшние вакансии",
        "Все вакансии",
        "Удалить категорию"
    )
    keyboard = [(KeyboardButton(name), ) for name in buttons_name]

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.effective_message.reply_text(
        "Действия",
        reply_markup=reply_markup
    )
    global ANY_ID
    ANY_ID = query.data


@user_permission
async def start(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """Функция с которой начинается взаимодействие с ботом.
    Создаёт кнопки под строкой ввода в чате."""

    buttons_name = (
        "Все категории",
        "Добавить новую категорию"
    )
    keyboard = [(KeyboardButton(name), ) for name in buttons_name]

    menu_button = ReplyKeyboardMarkup(keyboard)
    await update.effective_message.reply_text(
        "Главное меню",
        reply_markup=menu_button
    )


@user_permission
async def text_processing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция обработки вводимых текстовых сообщений.
    Реализует работу с кнопками на русском языке."""
    global ANY_ID

    if ANY_ID and ANY_ID != "new_cat":

        if update.message.text == "Все вакансии":
            message = await vacancy_view.get_category_vacancy(ANY_ID)
            await reply_text_vacancy(update, message)

        elif update.message.text == "Удалить категорию":
            await category_view.delete_category_by_id(ANY_ID)

        elif update.message.text == "Сегодняшние вакансии":
            message = await vacancy_view.get_today_vacancy_by_id(ANY_ID)
            await reply_text_vacancy(update, message)
        await start(update, context)
        ANY_ID = None

    elif ANY_ID != "new_cat":
        if update.message.text == "Все категории":
            await vacancy_menu(update)

        elif update.message.text == "Добавить новую категорию":
            message = "{0} {1} {2}".format(
                "Введите через пробел ключевые слова,",
                "которые должны быть в названии",
                "вакансий. По этим словам будет осуществляться поиск."
            )
            await update.effective_message.reply_text(
                message,
                reply_markup=ReplyKeyboardRemove()
            )
            ANY_ID = "new_cat"
    else:
        message = await category_view.set_category(update.message.text)
        await update.effective_message.reply_text(message)
        ANY_ID = None
        await start(update, context)

if __name__ == "__main__":

    engine = create_engine(f"sqlite:///{DB_PATH}vacancy.db", echo=False)
    session = Session(engine)

    category_view = CategoryView(session)
    vacancy_view = VacancyView(session)

    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    text_processing_handler = MessageHandler(filters.ALL, text_processing)
    buttons_click_handler = CallbackQueryHandler(buttons_click)

    application.add_handler(start_handler)
    application.add_handler(buttons_click_handler)
    application.add_handler(text_processing_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)
    session.close()
