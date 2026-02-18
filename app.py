from flask import Flask, render_template, request, session, g, redirect, url_for
from flask_socketio import SocketIO, emit
from datetime import datetime
import os
import threading
import time
import random
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*", ping_interval=25, ping_timeout=60)

messages_history = []
MAX_HISTORY = 100

# Загрузка переводов для языка
def load_translations(lang):
    try:
        with open(f'locales/{lang}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        # По умолчанию русский
        with open('locales/ru.json', 'r', encoding='utf-8') as f:
            return json.load(f)

# Контекстный процессор для использования переводов в шаблонах
@app.context_processor
def inject_translations():
    return dict(_=lambda key: g.translations.get(key, key))

@app.before_request
def before_request():
    # Устанавливаем язык из сессии или определяем по заголовкам
    if 'lang' not in session:
        session['lang'] = request.accept_languages.best_match(['ru', 'en', 'es']) or 'ru'
    g.translations = load_translations(session['lang'])

@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in ['ru', 'en', 'es']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

# Фоновый поток для бота (использует русский язык)
def bot_speaker():
    ru_translations = load_translations('ru')
    bot_phrases = ru_translations.get('bot_phrases', [])
    while True:
        time.sleep(1800)  # 30 минут
        if bot_phrases:
            msg = {
                'nick': '🤖 Бот',
                'text': random.choice(bot_phrases),
                'time': datetime.now().strftime('%H:%M')
            }
            messages_history.append(msg)
            if len(messages_history) > MAX_HISTORY:
                messages_history.pop(0)
            socketio.emit('message', msg)

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

    # Определяем язык пользователя, отправившего сообщение
    user_lang = session.get('lang', 'ru')
    translations = load_translations(user_lang)

    msg = {
        'nick': nick,
        'text': text,
        'time': datetime.now().strftime('%H:%M')
    }

    # Обработка команд бота
    if text.startswith('!бот'):
        parts = text.split(' ', 1)
        if len(parts) > 1:
            response = translations.get('bot_response', 'You said: {}. I\'m just a demo bot 😊').format(parts[1])
        else:
            response = translations.get('bot_help', 'I\'m here! Write !bot <something> and I\'ll repeat.')
        bot_msg = {
            'nick': '🤖 Бот',
            'text': response,
            'time': datetime.now().strftime('%H:%M')
        }
        messages_history.append(bot_msg)
        if len(messages_history) > MAX_HISTORY:
            messages_history.pop(0)
        socketio.emit('message', bot_msg)

        # Сохраняем исходное сообщение
        messages_history.append(msg)
        if len(messages_history) > MAX_HISTORY:
            messages_history.pop(0)
        socketio.emit('message', msg)
    else:
        # Обычное сообщение
        messages_history.append(msg)
        if len(messages_history) > MAX_HISTORY:
            messages_history.pop(0)
        socketio.emit('message', msg)

@socketio.on('set_nick')
def handle_set_nick(data):
    nick = data.get('nick', '').strip()
    if nick:
        session['nick'] = nick
        emit('nick_set', {'nick': nick})

        # Приветствие на языке пользователя
        user_lang = session.get('lang', 'ru')
        translations = load_translations(user_lang)
        welcome_text = translations.get('welcome', 'Welcome, {nick}! Nice to see a new participant.').format(nick=nick)

        welcome_msg = {
            'nick': '🤖 Бот',
            'text': welcome_text,
            'time': datetime.now().strftime('%H:%M')
        }
        messages_history.append(welcome_msg)
        if len(messages_history) > MAX_HISTORY:
            messages_history.pop(0)
        socketio.emit('message', welcome_msg)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)