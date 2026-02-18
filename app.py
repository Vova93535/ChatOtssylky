from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import os
import threading
import time
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*", ping_interval=25, ping_timeout=60)

messages_history = []
MAX_HISTORY = 100

# Список фраз для бота
BOT_PHRASES = [
    "Привет! Как дела?",
    "Кто тут сегодня общается?",
    "Интересно, о чём поговорим?",
    "Я просто бот, но тоже хочу участвовать!",
    "Не скучайте без меня 😊",
    "Погода сегодня отличная, кстати.",
    "Чат жив?",
    "Помните, я всегда здесь."
]

def bot_speaker():
    """Функция для периодической отправки сообщений от бота (запускается в фоне)"""
    while True:
        time.sleep(1800)  # 30 минут
        msg = {
            'nick': '🤖 Бот',
            'text': random.choice(BOT_PHRASES),
            'time': datetime.now().strftime('%H:%M')
        }
        messages_history.append(msg)
        if len(messages_history) > MAX_HISTORY:
            messages_history.pop(0)
        # Убрали broadcast=True
        socketio.emit('message', msg)

# Запускаем фоновый поток (только один раз)
threading.Thread(target=bot_speaker, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    emit('history', messages_history[-MAX_HISTORY:])

@socketio.on('message')
def handle_message(data):
    nick = data.get('nick', 'Anonymous')
    text = data.get('text', '').strip()
    if not text:
        return

    msg = {
        'nick': nick,
        'text': text,
        'time': datetime.now().strftime('%H:%M')
    }

    # Обработка команд бота
    if text.startswith('!бот'):
        parts = text.split(' ', 1)
        if len(parts) > 1:
            response = f"Вы сказали: {parts[1]}. Я просто демо-бот 😊"
        else:
            response = "Я здесь! Напишите !бот <что-то> и я повторю."
        bot_msg = {
            'nick': '🤖 Бот',
            'text': response,
            'time': datetime.now().strftime('%H:%M')
        }
        messages_history.append(bot_msg)
        if len(messages_history) > MAX_HISTORY:
            messages_history.pop(0)
        socketio.emit('message', bot_msg)  # убрали broadcast

        # Сохраняем исходное сообщение
        messages_history.append(msg)
        if len(messages_history) > MAX_HISTORY:
            messages_history.pop(0)
        socketio.emit('message', msg)  # убрали broadcast
    else:
        # Обычное сообщение
        messages_history.append(msg)
        if len(messages_history) > MAX_HISTORY:
            messages_history.pop(0)
        socketio.emit('message', msg)  # убрали broadcast

@socketio.on('set_nick')
def handle_set_nick(data):
    nick = data.get('nick', '').strip()
    if nick:
        session['nick'] = nick
        emit('nick_set', {'nick': nick})
        # Бот приветствует нового пользователя
        welcome_msg = {
            'nick': '🤖 Бот',
            'text': f"Добро пожаловать, {nick}! Приятно видеть нового участника.",
            'time': datetime.now().strftime('%H:%M')
        }
        messages_history.append(welcome_msg)
        if len(messages_history) > MAX_HISTORY:
            messages_history.pop(0)
        socketio.emit('message', welcome_msg)  # убрали broadcast

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)