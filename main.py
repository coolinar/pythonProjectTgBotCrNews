import requests
import sqlite3


# Функция для создания подключения к базе данных
def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn


# Функция для создания таблицы
def create_table(conn):
    sql_create_currencies_table = """
    CREATE TABLE IF NOT EXISTS currencies (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL
    );
    """
    cursor = conn.cursor()
    cursor.execute(sql_create_currencies_table)
    conn.commit()


# Функция для загрузки данных о криптовалютах
def load_currencies(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM currencies")
    return {row[0]: row[1] for row in cursor.fetchall()}


# Функция для получения текущего курса любой пары валют
def get_price(base_currency, quote_currency):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={base_currency}&vs_currencies={quote_currency}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if base_currency in data and quote_currency in data[base_currency]:
            return data[base_currency][quote_currency]
    return None


# Функция для проверки основных криптовалют
def get_main_currency_id(currency):
    main_cryptos = {
        'btc': 'bitcoin',
        'eth': 'ethereum',
        'usdt': 'tether',
        'xrp': 'ripple',
        'ltc': 'litecoin',
        'bch': 'bitcoin-cash',
        'ada': 'cardano',
        'dot': 'polkadot'
    }
    return main_cryptos.get(currency, currency)  # возвращает id основной криптовалюты, если есть


# Функция для проверки поддерживаемых валют (криптовалюты и фиатные валюты)
def is_supported_currency(currency, currency_dict):
    # Проверяем, если валюта - основная криптовалюта
    currency_id = get_main_currency_id(currency)
    if currency_id in currency_dict:
        return True
    # Проверяем, если валюта является фиатной (usd, eur, gbp и т.д.)
    supported_fiat = ['usd', 'eur', 'gbp', 'jpy', 'rub', 'cny', 'inr', 'aud', 'cad', 'chf', 'nzd', 'sgd', 'hkd']
    if currency in supported_fiat:
        return True
    return False


# Функция для конвертации валюты
def convert_currency(base_currency, quote_currency, amount, currency_dict):
    # Проверяем, если оба введенных значения являются поддерживаемыми валютами
    base_currency_id = get_main_currency_id(base_currency)
    quote_currency_id = get_main_currency_id(quote_currency)
    if is_supported_currency(base_currency_id, currency_dict) and is_supported_currency(quote_currency_id, currency_dict):
        price = get_price(base_currency_id, quote_currency_id)
        if price:
            converted_amount = amount * price
            base_currency_name = currency_dict.get(base_currency_id, base_currency.upper())
            print(f"Конвертация {amount} {base_currency_name} в {quote_currency.upper()}...")
            print(f"Текущий курс: 1 {base_currency_name} = {price} {quote_currency.upper()}")
            print(f"{amount} {base_currency_name} = {converted_amount} {quote_currency.upper()}")
            return True
        else:
            print(f"Не удалось получить курс для пары {base_currency.upper()} в {quote_currency.upper()}.")
            return False
    else:
        print(f"Одна из введенных валют не поддерживается: {base_currency.upper()} или {quote_currency.upper()}.")
        return False


# Функция для подсказок валют на основе введенного пользователем текста
def suggest_currencies(input_str, currency_dict):
    # Список приоритетных криптовалют
    prioritized = ['bitcoin', 'ethereum', 'tether', 'usd-coin', 'solana', 'cardano', 'polkadot', 'ripple', 'dogecoin', 'toncoin', 'mantle']

    # Прямое совпадение по имени
    exact_matches = [k for k in currency_dict.keys() if k == input_str.lower()]

    # Совпадение по начальным символам
    startswith_matches = [k for k in currency_dict.keys() if k.startswith(input_str.lower()) and k not in exact_matches]

    # Частичные совпадения, где строка содержится внутри названия валюты
    partial_matches = [k for k in currency_dict.keys() if input_str.lower() in k and k not in startswith_matches and k not in exact_matches]

    # Сортируем: сначала приоритетные криптовалюты
    sorted_matches = sorted(exact_matches + startswith_matches + partial_matches, key=lambda x: (x not in prioritized, x))

    # Ограничиваем список до 5 элементов и включаем приоритетные
    suggestions = sorted([s for s in sorted_matches if s in prioritized] + sorted_matches[:5], key=lambda x: x not in prioritized)

    return suggestions[:5]


# Основная функция программы
def main():
    database = "currencies.db"
    conn = create_connection(database)
    create_table(conn)

    currency_dict = load_currencies(conn)

    while True:
        base_currency = input("Введите исходную валюту (например, btc или usd): ").strip().lower()

        if not is_supported_currency(base_currency, currency_dict):
            suggestions = suggest_currencies(base_currency, currency_dict)
            if suggestions:
                print("Возможные варианты криптовалют: ", ", ".join(suggestions))
            else:
                print("Криптовалюта не найдена.")
            continue

        quote_currency = input("Введите целевую валюту (например, usd, eur, btc): ").strip().lower()

        if not is_supported_currency(quote_currency, currency_dict):
            suggestions = suggest_currencies(quote_currency, currency_dict)
            if suggestions:
                print("Возможные варианты криптовалют: ", ", ".join(suggestions))
            else:
                print("Криптовалюта не найдена.")
            continue

        amount = float(input("Введите сумму для конвертации: "))

        if convert_currency(base_currency, quote_currency, amount, currency_dict):
            check_again = input("Хотите проверить курс другой валюты? (y/n): ").strip().lower()
            if check_again == 'n':
                break

    conn.close()


if __name__ == "__main__":
    main()
