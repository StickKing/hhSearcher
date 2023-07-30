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
