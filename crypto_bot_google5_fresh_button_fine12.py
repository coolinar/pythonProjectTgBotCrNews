import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
import requests

# Токен вашего бота
TOKEN = '7129836981:AAHFu8oLtaQZgRk2rAmq0ky0Y92Amo6Jpb8'
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# API Key и CX для Google Custom Search
GOOGLE_API_KEY = 'AIzaSyBlK55E7c5Zf3CWE54GHKges7xfjD2klbk'
SEARCH_ENGINE_ID = '360e7dcbfef5c417b'

# Конфигурация логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Храним результаты поиска и индекс текущей новости для каждого пользователя
user_search_results = {}


# Функция для поиска новостей в Google по ключевому слову
def search_news(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&num=5&sort=date"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json()
        news_items = []
        for item in results.get('items', []):
            title = item['title']
            link = item['link']
            snippet = item.get('snippet', 'Описание не доступно')
            news_items.append({
                'title': title,
                'snippet': snippet,
                'link': link
            })
        return news_items
    else:
        logger.error(f"Ошибка при поиске новостей: {response.status_code}")
        return []


# Приветственное сообщение при первом запуске
@dp.message_handler(commands=['start'])
async def welcome_message(message: types.Message):
    user_name = message.from_user.first_name if message.from_user.first_name else "друг"

    # Приветственное сообщение с описанием возможностей бота
    welcome_text = (
        f"Привет, {user_name}! Я бот для поиска новостей по ключевым словам и категориям. "
        f"Вот что я умею:\n\n"
        f"🪙 Искать свежие новости о криптовалютах\n"
        f"💻 Искать технологические новости\n"
        f"💵 Обновления в мире финансов\n"
        f"🔍 Поиск новостей по любому ключевому слову\n\n"
        "Выберите категорию или введите ключевое слово для поиска новостей."
    )

    await bot.send_message(message.chat.id, welcome_text)
    await show_categories(message)


# Функция для отображения категорий новостей
async def show_categories(message: types.Message):
    markup = types.InlineKeyboardMarkup(row_width=3)  # Устанавливаем ширину строки в 3
    button1 = types.InlineKeyboardButton(text='🪙 Крипто', callback_data='cryptocurrency')
    button2 = types.InlineKeyboardButton(text='💻 Технологии', callback_data='technology')
    button3 = types.InlineKeyboardButton(text='💵 Финансы', callback_data='finance')

    # Добавляем кнопки в одну строку
    markup.add(button1, button2, button3)

    # Добавляем кнопку "Поиск по ключевому слову" под остальными кнопками
    button4 = types.InlineKeyboardButton(text='🔍 Поиск по ключевому слову', callback_data='search_by_keyword')
    markup.add(button4)

    await bot.send_message(
        message.chat.id,
        "Выберите категорию или введите ключевое слово для поиска новостей.",
        reply_markup=markup
    )


# Функция для отправки новости с возможностью переключения
async def send_news(message, news_items, news_index=0):
    if news_index < len(news_items):
        news = news_items[news_index]
        text = f"<b>{news['title']}</b>\n{news['snippet']}\n<a href='{news['link']}'>Читать далее</a>\n"

        markup = types.InlineKeyboardMarkup()
        if news_index < len(news_items) - 1:
            next_button = types.InlineKeyboardButton('Следующая новость ➡️', callback_data=f'next_{news_index + 1}')
            markup.add(next_button)

        new_search_button = types.InlineKeyboardButton('🔍 Новый поиск', callback_data='new_search')
        markup.add(new_search_button)

        # Добавляем кнопку "Вернуться к категориям"
        return_to_categories_button = types.InlineKeyboardButton('🏠 Вернуться к категориям',
                                                                 callback_data='return_to_categories')
        markup.add(return_to_categories_button)

        await bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)
    else:
        await bot.send_message(message.chat.id, "Нет доступных новостей.")


# Обработчик для выбора категории
@dp.callback_query_handler(lambda call: call.data in ['cryptocurrency', 'technology', 'finance', 'search_by_keyword'])
async def handle_callback(call: types.CallbackQuery):
    if call.data == 'cryptocurrency':
        query = "cryptocurrency news"
    elif call.data == 'technology':
        query = "technology news"
    elif call.data == 'finance':
        query = "finance news"
    elif call.data == 'search_by_keyword':
        await bot.send_message(call.message.chat.id, "Введите ключевое слово для поиска: ")
        return

    news_items = search_news(query)

    if news_items:
        user_search_results[call.message.chat.id] = news_items
        await send_news(call.message, news_items, news_index=0)
    else:
        await bot.send_message(call.message.chat.id, "Новостей по этой категории не найдено.")


# Обработчик кнопки "Следующая новость"
@dp.callback_query_handler(lambda call: call.data.startswith('next_'))
async def handle_next_news(call: types.CallbackQuery):
    news_index = int(call.data.split('_')[1])
    news_items = user_search_results.get(call.message.chat.id, [])

    if news_items:
        await send_news(call.message, news_items, news_index=news_index)
    else:
        await bot.send_message(call.message.chat.id, "Нет доступных новостей.")


# Обработчик кнопки "Новый поиск"
@dp.callback_query_handler(lambda call: call.data == 'new_search')
async def handle_new_search(call: types.CallbackQuery):
    user_name = call.from_user.first_name if call.from_user.first_name else "друг"
    await bot.send_message(call.message.chat.id, f"{user_name}, введите новое ключевое слово для поиска.")


# Обработчик кнопки "Вернуться к категориям"
@dp.callback_query_handler(lambda call: call.data == 'return_to_categories')
async def handle_return_to_categories(call: types.CallbackQuery):
    await show_categories(call.message)


# Обработчик текстовых сообщений для поиска по ключевым словам
@dp.message_handler(lambda message: True)
async def search_news_by_keyword(message: types.Message):
    query = message.text
    news_items = search_news(query)

    if news_items:
        user_search_results[message.chat.id] = news_items
        await send_news(message, news_items, news_index=0)
    else:
        await bot.send_message(message.chat.id, "Новостей по вашему запросу не найдено.")


if __name__ == '__main__':
    logging.info("Бот запущен и ожидает сообщений...")
    executor.start_polling(dp, skip_updates=True)
