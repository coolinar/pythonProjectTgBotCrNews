import logging
import telebot
import requests
from telebot import types

# Задаем токен вашего бота
TOKEN = '7129836981:AAHFu8oLtaQZgRk2rAmq0ky0Y92Amo6Jpb8'
bot = telebot.TeleBot(TOKEN)

# API Key и CX для Google Custom Search
GOOGLE_API_KEY = 'AIzaSyBlK55E7c5Zf3CWE54GHKges7xfjD2klbk'
SEARCH_ENGINE_ID = '360e7dcbfef5c417b'

# Конфигурация логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
            news_items.append(f"<b>{title}</b>\n{snippet}\n<a href='{link}'>Читать далее</a>\n")
        return news_items
    else:
        logger.error(f"Ошибка при поиске новостей: {response.status_code}")
        return ["Ошибка при поиске новостей. Попробуйте позже."]


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton(text='🪙 Крипто', callback_data='cryptocurrency')
    button2 = types.InlineKeyboardButton(text='💻 Технологии', callback_data='technology')
    button3 = types.InlineKeyboardButton(text='💵 Финансы', callback_data='finance')
    button4 = types.InlineKeyboardButton(text='🔍 Поиск по ключевому слову', callback_data='search_by_keyword')
    markup.add(button1, button2, button3, button4)

    bot.send_message(message.chat.id,
                     "Привет! Я бот для поиска новостей. Выберите категорию или введите ключевое слово.",
                     reply_markup=markup)


# Обработчик для выбора категории
@bot.callback_query_handler(
    func=lambda call: call.data in ['cryptocurrency', 'technology', 'finance', 'search_by_keyword'])
def handle_callback(call):
    if call.data == 'cryptocurrency':
        query = "cryptocurrency news"
    elif call.data == 'technology':
        query = "technology news"
    elif call.data == 'finance':
        query = "finance news"
    elif call.data == 'search_by_keyword':
        bot.send_message(call.message.chat.id, "Введите ключевое слово для поиска:")
        return

    news_items = search_news(query)
    if news_items:
        for news in news_items:
            bot.send_message(call.message.chat.id, news, parse_mode='HTML')
    else:
        bot.send_message(call.message.chat.id, "Новостей по этой категории не найдено.")


# Обработчик текстовых сообщений для поиска по ключевым словам
@bot.message_handler(func=lambda message: True)
def search_news_by_keyword(message):
    if message.text not in ['Крипто', 'Технологии', 'Финансы', 'Поиск по ключевому слову']:
        query = message.text
        news_items = search_news(query)

        if news_items:
            for news in news_items:
                bot.send_message(message.chat.id, news, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "Новостей по вашему запросу не найдено.")


if __name__ == '__main__':
    logging.info("Бот запущен и ожидает сообщений...")
    bot.polling(none_stop=True)
