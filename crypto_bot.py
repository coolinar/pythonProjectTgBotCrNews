import logging
import feedparser
import telebot
from datetime import datetime, timedelta
import os
import json
import re
from apscheduler.schedulers.background import BackgroundScheduler
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Задаем токен вашего бота
TOKEN = '7129836981:AAHFu8oLtaQZgRk2rAmq0ky0Y92Amo6Jpb8'
bot = telebot.TeleBot(TOKEN)

# URLы RSS-лент для разных источников новостей
NEWS_SOURCES = {
    'CoinTelegraph': 'https://cointelegraph.com/rss',
    'CryptoNews': 'https://cryptonews.com/news/feed/'
}

# Путь к файлу для хранения состояния
STATE_FILE = 'news_state.json'

# Конфигурация логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем планировщик для отправки новостей
scheduler = BackgroundScheduler()
scheduler.start()


# Функция для загрузки состояния из файла
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {'subscribers': {}, 'last_sent_time': '1970-01-01T00:00:00'}


# Функция для сохранения состояния в файл
def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)


# Функция для разбиения текста на части
def split_message(text, max_length=4096):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]


# Функция для очистки HTML из текста
def clean_html(text):
    text = re.sub(r'<[^>]+>', '', text)  # Удаляет все HTML теги
    return text


# Функция для отправки новостей
def send_news(chat_id, source):
    feed = feedparser.parse(NEWS_SOURCES[source])

    if not feed.entries:
        bot.send_message(chat_id, "Нет доступных новостей.")
        return

    # Берем самую свежую новость
    entry = feed.entries[0]
    published = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d %H:%M:%S')

    news_item = (f"<b>Заголовок:</b> {entry.title}\n"
                 f"<b>Дата публикации:</b> {published}\n"
                 f"<b>Описание:</b> {clean_html(entry.summary)}\n"
                 f"<a href='{entry.link}'>Читать далее</a>\n")

    messages = split_message(news_item)
    for msg in messages:
        bot.send_message(chat_id, msg, parse_mode='HTML')


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    for source_name in NEWS_SOURCES.keys():
        markup.add(InlineKeyboardButton(source_name, callback_data=f"source:{source_name}"))

    bot.reply_to(message, "Привет! Выберите источник новостей:", reply_markup=markup)


# Обработчик выбора источника новостей
@bot.callback_query_handler(func=lambda call: call.data.startswith('source:'))
def handle_source_selection(call):
    source = call.data.split(':')[1]
    state = load_state()

    # Сохраняем выбранный источник для пользователя
    state['subscribers'][call.message.chat.id] = {'source': source}
    save_state(state)

    bot.send_message(call.message.chat.id, f"Вы выбрали {source}. Вы будете получать новости из этого источника.")

    # Отправляем самую последнюю новость сразу после выбора источника
    send_news(call.message.chat.id, source)


# Функция для регулярной отправки новостей
def schedule_news():
    state = load_state()
    for chat_id, user_info in state['subscribers'].items():
        source = user_info['source']
        send_news(chat_id, source)


# Запускаем задачу для отправки новостей каждые 5 минут
scheduler.add_job(schedule_news, 'interval', minutes=5)

if __name__ == '__main__':
    logging.info("Бот запущен и ожидает сообщений...")
    bot.polling(none_stop=True)
