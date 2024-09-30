import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
import requests
from googletrans import Translator

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

# Храним результаты поиска и язык пользователя
user_search_results = {}
user_language = {}

# Инициализируем переводчик
translator = Translator()

# Возможные языки
LANGUAGES = {
    'ru': 'Русский',
    'en': 'English',
    'es': 'Español'
}


# Функция для поиска новостей в Google по ключевому слову
def search_news(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&num=5&sort=date"
    response = requests.get(url)

    logger.info(f"Request URL: {url}")

    if response.status_code == 200:
        results = response.json()
        logger.info(f"Response from Google API: {results}")

        news_items = [
            {
                'title': item['title'],
                'snippet': item.get('snippet', 'Описание не доступно'),
                'link': item['link']
            }
            for item in results.get('items', [])
        ]
        return news_items
    else:
        logger.error(f"Ошибка при поиске новостей: {response.status_code}, {response.text}")
        return []


# Приветственное сообщение с выбором языка
@dp.message_handler(commands=['start'])
async def welcome_message(message: types.Message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text='Русский', callback_data='lang_ru'),
        types.InlineKeyboardButton(text='English', callback_data='lang_en'),
        types.InlineKeyboardButton(text='Español', callback_data='lang_es'),
    ]
    markup.add(*buttons)

    welcome_text = "Пожалуйста, выберите язык:\n\nHello! Please choose your language:\n\n¡Hola! Por favor, elige tu idioma:"
    await bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


# Обработчик для выбора языка
@dp.callback_query_handler(lambda call: call.data.startswith('lang_'))
async def set_language(call: types.CallbackQuery):
    lang_code = call.data.split('_')[1]
    user_language[call.message.chat.id] = lang_code

    descriptions = {
        'ru': "Я бот для поиска новостей по ключевым словам и категориям. Вот что я умею:\n\n" \
              "🪙 Искать свежие новости о криптовалютах\n" \
              "💻 Искать технологические новости\n" \
              "💵 Обновления в мире финансов\n" \
              "🔍 Поиск новостей по любому ключевому слову",
        'en': "I am a bot for searching news by keywords and categories. Here's what I can do:\n\n" \
              "🪙 Search for the latest cryptocurrency news\n" \
              "💻 Search for tech news\n" \
              "💵 Financial updates\n" \
              "🔍 Search for news by any keyword",
        'es': "Soy un bot para buscar noticias por palabras clave y categorías. Esto es lo que puedo hacer:\n\n" \
              "🪙 Buscar noticias de criptomonedas\n" \
              "💻 Buscar noticias tecnológicas\n" \
              "💵 Actualizaciones financieras\n" \
              "🔍 Buscar noticias por cualquier palabra clave",
    }

    await bot.send_message(call.message.chat.id, descriptions.get(lang_code, descriptions['en']))
    await send_category_options(call)


# Функция для отправки вариантов выбора категорий на выбранном языке
async def send_category_options(call: types.CallbackQuery):
    lang = user_language.get(call.message.chat.id, 'en')
    markup = types.InlineKeyboardMarkup(row_width=3)

    category_buttons = {
        'ru': [
            ('🪙 Криптовалюта', 'cryptocurrency'),
            ('💻 Технологии', 'technology'),
            ('💵 Финансы', 'finance'),
            ('🔍 Поиск по ключевому слову', 'search_by_keyword'),
        ],
        'en': [
            ('🪙 Crypto', 'cryptocurrency'),
            ('💻 Tech', 'technology'),
            ('💵 Finance', 'finance'),
            ('🔍 Keyword Search', 'search_by_keyword'),
        ],
        'es': [
            ('🪙 Criptomonedas', 'cryptocurrency'),
            ('💻 Tecnología', 'technology'),
            ('💵 Finanzas', 'finance'),
            ('🔍 Búsqueda por palabra clave', 'search_by_keyword'),
        ],
    }

    buttons = [types.InlineKeyboardButton(text=text, callback_data=data) for text, data in
               category_buttons.get(lang, category_buttons['en'])]
    markup.add(*buttons[:3])  # Первые три кнопки
    markup.add(buttons[3])  # Четвертая кнопка

    text = {
        'ru': "Выберите категорию или введите ключевое слово для поиска новостей.",
        'en': "Choose a category or enter a keyword to search for news.",
        'es': "Elige una categoría o ingresa una palabra clave para buscar noticias."
    }

    await bot.send_message(call.message.chat.id, text.get(lang, text['en']), reply_markup=markup)


# Функция для отправки новости
async def send_news(message, news_items, news_index=0):
    lang = user_language.get(message.chat.id, 'en')
    if news_index < len(news_items):
        news = news_items[news_index]
        title_translated = translator.translate(news['title'], dest=lang).text
        snippet_translated = translator.translate(news['snippet'], dest=lang).text
        text = f"<b>{title_translated}</b>\n{snippet_translated}\n<a href='{news['link']}'>Read more</a>"

        markup = types.InlineKeyboardMarkup()
        if news_index < len(news_items) - 1:
            next_button = types.InlineKeyboardButton('Next News ➡️', callback_data=f'next_{news_index + 1}')
            markup.add(next_button)
        new_search_button = types.InlineKeyboardButton('🔍 New Search', callback_data='new_search')
        markup.add(new_search_button)

        await bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)
    else:
        await bot.send_message(message.chat.id, "No news available.")


# Обработчик для выбора категории
@dp.callback_query_handler(lambda call: call.data in ['cryptocurrency', 'technology', 'finance', 'search_by_keyword'])
async def handle_callback(call: types.CallbackQuery):
    query_map = {
        'cryptocurrency': "cryptocurrency news",
        'technology': "technology news",
        'finance': "finance news",
    }

    query = query_map.get(call.data, None)
    if query is None:
        await bot.send_message(call.message.chat.id, "Введите ключевое слово для поиска.")
        return

    news_items = search_news(query)
    user_search_results[call.message.chat.id] = news_items
    await send_news(call.message, news_items, news_index=0)


# Обработчик кнопки "Следующая новость"
@dp.callback_query_handler(lambda call: call.data.startswith('next_'))
async def handle_next_news(call: types.CallbackQuery):
    news_index = int(call.data.split('_')[1])
    news_items = user_search_results.get(call.message.chat.id, [])
    await send_news(call.message, news_items, news_index=news_index)


# Обработчик кнопки "Новый поиск"
@dp.callback_query_handler(lambda call: call.data == 'new_search')
async def handle_new_search(call: types.CallbackQuery):
    await send_category_options(call)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
