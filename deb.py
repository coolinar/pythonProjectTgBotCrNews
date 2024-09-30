import os
import json

# Путь к файлу для хранения информации о последней новостях
STATE_FILE = 'news_state.json'


# Функция для загрузки состояния из файла
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {'last_news': None}


# Функция для сохранения состояния в файл
def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)


# Пример использования
if __name__ == "__main__":
    state = load_state()
    print("Текущее состояние:", state)

    # Обновляем состояние
    state['last_news'] = {'title': 'Latest News', 'link': 'https://example.com/news',
                          'snippet': 'Latest news snippet here'}
    save_state(state)
