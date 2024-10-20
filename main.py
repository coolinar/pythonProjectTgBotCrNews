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


# Функция для получения текущего курса
def get_price(base_currency, quote_currency):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={base_currency}&vs_currencies={quote_currency}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {}


# Функция для конвертации валюты
def convert_currency(base_currency, quote_currency, amount, currency_dict):
    price_data = get_price(base_currency, quote_currency)
    if price_data:
        price = price_data[base_currency][quote_currency]
        converted_amount = amount * price
        print(f"Конвертация {amount} {currency_dict[base_currency]} в {quote_currency}...")
        print(f"Текущий курс: 1 {currency_dict[base_currency]} = {price} {quote_currency}")
        print(f"{amount} {currency_dict[base_currency]} = {converted_amount} {quote_currency}")
        return True
    print(f"Не удалось получить курс обмена для {base_currency} в {quote_currency}.")
    return False


# Функция для проверки доступных валют
def suggest_currencies(input_str, currency_dict):
    suggestions = [k for k in currency_dict.keys() if k.startswith(input_str.lower())]
    return suggestions


# Основная функция программы
def main():
    database = "currencies.db"
    conn = create_connection(database)
    create_table(conn)

    currency_dict = load_currencies(conn)

    while True:
        base_currency = input("Введите исходную криптовалюту (например, btc): ").strip().lower()

        if base_currency not in currency_dict:
            suggestions = suggest_currencies(base_currency, currency_dict)
            if suggestions:
                print("Возможные варианты: ", ", ".join(suggestions))
            else:
                print("Криптовалюта не найдена.")
            continue

        quote_currency = input("Введите целевую криптовалюту (например, usd): ").strip().lower()

        if quote_currency not in currency_dict:
            suggestions = suggest_currencies(quote_currency, currency_dict)
            if suggestions:
                print("Возможные варианты: ", ", ".join(suggestions))
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
