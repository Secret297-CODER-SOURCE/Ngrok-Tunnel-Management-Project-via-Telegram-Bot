# -*- coding: utf-8 -*-
import os
import subprocess
import sys
import threading
import json
import socket
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from pyngrok import ngrok, conf

# Файл для сохранения конфигурации
CONFIG_FILE = "config.json"


# Проверка и установка зависимостей
def install_dependencies():
    required_packages = ["pyngrok", "pytelegrambotapi"]
    for package in required_packages:
        try:
            # Проверка, установлен ли пакет
            __import__(package)
            print(f"{package} уже установлен.")
        except ImportError:
            print(f"{package} не найден. Устанавливаем...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--break-system-packages"])


# Загрузка конфигурации
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


# Сохранение конфигурации
def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)


# Настройка конфигурации (ручной ввод)
def configure():
    config = load_config()
    if not config.get("TELEGRAM_BOT_TOKEN"):
        config["TELEGRAM_BOT_TOKEN"] = input("Введите токен Telegram бота: ").strip()
    if not config.get("NGROK_AUTH_TOKEN"):
        config["NGROK_AUTH_TOKEN"] = input("Введите токен Ngrok: ").strip()
    if not config.get("CHAT_ID"):
        config["CHAT_ID"] = input("Введите ваш Chat ID: ").strip()
    save_config(config)
    return config


# Проверка и установка Ngrok
def setup_ngrok(auth_token):
    try:
        ngrok_path = conf.get_default().ngrok_path
        if not os.path.exists(ngrok_path):
            print("Ngrok не найден. Устанавливаем...")
            os.system("wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-linux-amd64.zip")
            os.system("unzip ngrok-stable-linux-amd64.zip")
            os.system("mv ngrok /usr/local/bin/")
            os.system("rm ngrok-stable-linux-amd64.zip")
        ngrok.set_auth_token(auth_token)
    except Exception as e:
        print(f"Ошибка настройки Ngrok: {e}")


# Проверка, используется ли порт
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("localhost", port)) == 0


# Установка зависимостей
install_dependencies()

# Настройка конфигурации
config = configure()

# Инициализация Ngrok
setup_ngrok(config["NGROK_AUTH_TOKEN"])

# Инициализация бота
bot = TeleBot(config["TELEGRAM_BOT_TOKEN"])
CHAT_ID = config["CHAT_ID"]
tunnels = {}  # Словарь для хранения запущенных туннелей


# Создание клавиатуры
def create_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton("HTTP"),
        KeyboardButton("HTTPS"),
        KeyboardButton("SSH"),
        KeyboardButton("VNC"),
        KeyboardButton("FTP"),
        KeyboardButton("FTPS"),
        KeyboardButton("Остановить все туннели"),
    ]
    markup.add(*buttons)
    return markup


# Создание инлайн-кнопки
def create_stop_button(protocol):
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="Остановить туннель", callback_data=f"stop_{protocol}")
    markup.add(button)
    return markup


# Функция для запуска Ngrok
def start_ngrok(protocol, port):
    if is_port_in_use(port) and port != 22:
        return f"Порт {port} уже используется другим процессом. Запуск туннеля невозможен.", None

    try:
        if protocol in tunnels:
            return f"Туннель {protocol} уже запущен: {tunnels[protocol].public_url}", None
        tunnel = ngrok.connect(port, protocol)
        tunnels[protocol] = tunnel
        return f"Ngrok запущен для {protocol.upper()}: {tunnel.public_url}", create_stop_button(protocol)
    except Exception as e:
        return f"Ошибка запуска туннеля {protocol.upper()}: {e}", None


# Функция для остановки туннеля
def stop_tunnel(protocol):
    try:
        if protocol in tunnels:
            ngrok.disconnect(tunnels[protocol].public_url)
            del tunnels[protocol]
            return f"Туннель {protocol.upper()} остановлен."
        else:
            return f"Туннель {protocol.upper()} не найден."
    except Exception as e:
        return f"Ошибка остановки туннеля {protocol.upper()}: {e}"


# Функция для остановки всех туннелей
def stop_all_tunnels():
    try:
        ngrok.kill()
        tunnels.clear()
        return "Все туннели остановлены."
    except Exception as e:
        return f"Ошибка остановки туннелей: {e}"


# Обработчик команд и кнопок
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    response = ""
    markup = None
    if message.text == "HTTP":
        response, markup = start_ngrok("http", 80)
    elif message.text == "HTTPS":
        response, markup = start_ngrok("http", 443)
    elif message.text == "SSH":
        response, markup = start_ngrok("tcp", 22)
    elif message.text == "VNC":
        response, markup = start_ngrok("tcp", 5900)
    elif message.text == "FTP":
        response, markup = start_ngrok("tcp", 21)
    elif message.text == "FTPS":
        response, markup = start_ngrok("tcp", 990)
    elif message.text == "Остановить все туннели":
        response = stop_all_tunnels()
    else:
        response = "Пожалуйста, выберите действие из меню."

    bot.send_message(CHAT_ID, response, reply_markup=markup if markup else create_main_menu())


# Обработчик инлайн-кнопок
@bot.callback_query_handler(func=lambda call: call.data.startswith("stop_"))
def handle_stop_button(call):
    protocol = call.data.split("_")[1]
    response = stop_tunnel(protocol)
    bot.send_message(CHAT_ID, response, reply_markup=create_main_menu())


# Запуск бота
def main():
    bot.send_message(CHAT_ID, "Бот запущен. Выберите протокол для запуска туннеля или остановите все туннели.",
                     reply_markup=create_main_menu())
    bot.infinity_polling()


if __name__ == "__main__":
    main()
