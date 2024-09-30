import logging
import telebot
import requests
import os
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
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&num=5"
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
        return ["Ошибка при поиске новостей. Попробуйте позже."]


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "Привет! Я бот для поиска новостей. Выберите источник или введите ключевое слово.")


# Обработчик команды /news
@bot.message_handler(commands=['news'])
def news(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Крипто')
    button2 = types.KeyboardButton('Технологии')
    button3 = types.KeyboardButton('Финансы')
    markup.add(button1, button2, button3)

    bot.send_message(message.chat.id, "Выберите категорию или введите ключевое слово:", reply_markup=markup)


# Обработчик для выбора категории
@bot.message_handler(func=lambda message: message.text in ['Крипто', 'Технологии', 'Финансы'])
def send_news_by_category(message):
    if message.text == 'Крипто':
        news_items = search_news("cryptocurrency news")
    elif message.text == 'Технологии':
        news_items = search_news("technology news")
    elif message.text == 'Финансы':
        news_items = search_news("finance news")

    if news_items:
        for news in news_items:
            bot.send_message(message.chat.id, news, parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, "Новостей по этой категории не найдено.")


# Обработчик текстовых сообщений для поиска по ключевым словам
@bot.message_handler(func=lambda message: True)
def search_news_by_keyword(message):
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
