import telebot
import requests
import logging
from bs4 import BeautifulSoup
from telebot import types

# Токен бота
TOKEN = '8025501437:AAGL5SYUtj-ua-6LQxTp9PbklC980ssOA5M'
bot = telebot.TeleBot(TOKEN)

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Создаем клавиатуру с валютами
markup_valut = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
markup_valut.add(types.KeyboardButton('USD'), types.KeyboardButton('EUR'),
                 types.KeyboardButton('GBP'), types.KeyboardButton('JPY'),types.KeyboardButton('AUD'),
                 types.KeyboardButton('AZN'),types.KeyboardButton('AMD'),types.KeyboardButton('THB'),
                 types.KeyboardButton('BYN'),types.KeyboardButton('BGN'),types.KeyboardButton('BRL'),
                 types.KeyboardButton('KRW'),types.KeyboardButton('HKD'),types.KeyboardButton('UAH'),
                 types.KeyboardButton('INR'),types.KeyboardButton('EGP'),types.KeyboardButton('CAD'),
                 types.KeyboardButton('TRY'),types.KeyboardButton('KZT'))
logging.info('all constants executed')

# Функция для получения курса обмена
def get_currency_rate_from_cbr(target_currency_code):
    url = 'https://www.cbr.ru/currency_base/daily/?spm=a2ty_o01.29997173.0.0.6ec2c921o2FJHt'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        print("Status Code:", response.status_code)
        print("Response URL:", response.url)

        if response.status_code != 200:
            print(f"Ошибка HTTP: {response.status_code}")
            return f"Ошибка получения данных: {response.status_code}"

        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')

        table = soup.find('table')
        print("Table found:", table)

        if table is None:
            return "Не удалось найти таблицу с курсами валют"

        rows = table.find_all('tr')[1:]

        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 5:
                code = cols[1].text.strip()
                rate = cols[4].text.strip().replace(',', '.')
                if code == target_currency_code:
                    return float(rate)

        return "Валюта не найдена"
    except Exception as e:
        print(f"Ошибка при парсинге: {e}")
        return f"Ошибка получения курса: {e}"

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Я бот для проверки курсов валют.\nВыберите валюту ниже, чтобы узнать её курс к RUB:",
        reply_markup=markup_valut
    )
    logging.info("func start has executed")

# Обработчик текстовых сообщений (выбор валюты)
@bot.message_handler(content_types=['text'])
def handle_currency_choice(message):
    chat_id = message.chat.id
    currency = message.text.upper()
    available_currencies = ['USD', 'EUR', 'GBP', 'JPY','AUD','AZN','AMD','THB','BYN','BYN','BGN',
                            'BRL','KRW','HKD','UAH','INR','EGP','CAD','TRY','KZT']

    if currency in available_currencies:
        rate = get_currency_rate_from_cbr(currency)
        if isinstance(rate, float):
            bot.send_message(
                chat_id,
                f"💱 1 {currency} = {rate:.2f} RUB",
                reply_markup=markup_valut
            )
        else:
            bot.send_message(chat_id, f"Не удалось получить курс для {currency}.")
            logging.error(f"Error getting rate for {currency}: {rate}")
    else:
        bot.send_message(
            chat_id,
            "Извините, я не знаю эту валюту. Пожалуйста, выберите из предложенных:",
            reply_markup=markup_valut
        )
        logging.error("User activated unavailable variant")

if __name__ == '__main__':
    # Запуск бота
    bot.polling(none_stop=True)
    logging.info("Telegram bot started")