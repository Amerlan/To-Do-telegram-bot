import telebot
from telebot import types
import sqlite3
from datetime import datetime

API = "1408998008:AAHbgddInojBnCMC3YXcc6BBcgjyqv_D-xk"
bot = telebot.TeleBot(API)


def get_name(msg):
    db = sqlite3.connect('todo.db')
    cursor = db.cursor()
    cursor.execute(
            f'INSERT INTO users (user_id, nick, username) VALUES ({msg.from_user.id}, "{msg.text}", "{msg.from_user.username}")')
    db.commit()
    bot.send_message(msg.from_user.id, f'Nice to meet You, {msg.text}')
    db.close()
    bot.send_message(msg.from_user.id, 'Menu')
    menu(msg)


@bot.message_handler(commands=['start'])
def start(msg):
    db = sqlite3.connect('todo.db')
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER primary key, nick TEXT NOT NULL, username TEXT)')
    cursor.execute("""CREATE TABLE IF NOT EXISTS tasks (task_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
                    task TEXT NOT NULL, path_media TEXT, status INTEGER DEFAULT 0, foreign key(user_id) references users (user_id))""")
    if cursor.execute(f"SELECT user_id FROM users WHERE user_id={msg.from_user.id}").fetchone():
        name = cursor.execute(f"SELECT nick FROM users WHERE user_id={msg.from_user.id}").fetchone()
        keyboard = types.InlineKeyboardMarkup()
        change = types.InlineKeyboardButton(text='Change name', callback_data='change')
        keyboard.add(change)
        bot.send_message(msg.from_user.id, f'Hi, {name[0]}!', reply_markup=None)
        menu(msg)
    else:
        bot.send_message(msg.from_user.id, "Hello. I'm To do list bot. This pet project is done by Amerlan Tokhtarov", reply_markup=None)
        bot.send_message(msg.from_user.id, "We don't know each other. Let's change it. How can I call You?")
        bot.send_message(msg.from_user.id, 'Enter your name please')
        bot.register_next_step_handler(msg, get_name)
        # bot.send_message(msg.from_user.id, 'List clears every day at 12 a.m. ')
    db.commit()
    db.close()


def change_name(msg):
    db = sqlite3.connect('todo.db')
    cursor = db.cursor()
    cursor.execute(f"UPDATE users SET nick='{msg.text}' WHERE user_id={msg.from_user.id}")
    db.commit()
    db.close()
    bot.send_message(msg.from_user.id, f"That's it. {msg.text.capitalize()}, what's next?", reply_markup=None)
    menu(msg)


def menu(msg):
    actions = types.ReplyKeyboardMarkup(resize_keyboard=True)
    actions.row('Add to-do', 'All')
    bot.send_message(msg.from_user.id, 'Choose action', reply_markup=actions)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'change':
        bot.send_message(call.from_user.id, 'Enter your new name')
        bot.register_next_step_handler(call.message, change_name)
    elif call.data == 'add picture':
        bot.send_message(call.from_user.id, 'Send me a picture')
        bot.register_next_step_handler(call.message, add_picture)
    elif call.data == 'add task':
        bot.send_message(call.from_user.id, 'Enter what you need to do')
        bot.register_next_step_handler(call.message, add_task)
    else:
        checkup(call)



@bot.message_handler(content_types=['text'])
def controller(msg):
    if msg.text == 'Add to-do':
        bot.send_message(msg.from_user.id, 'Enter what you need to do', reply_markup=None)
        bot.register_next_step_handler(msg, add_task)
    elif msg.text == 'All':
        show_tasks(msg)


def add_task(msg):
    db = sqlite3.connect('todo.db')
    cursor = db.cursor()
    cursor.execute(f'INSERT INTO tasks (user_id, task) VALUES ({msg.from_user.id}, "{msg.text}")')
    db.commit()
    db.close()
    keyboard = types.InlineKeyboardMarkup()
    add_more = types.InlineKeyboardButton(text='Add one more', callback_data='add task')
    add_pic = types.InlineKeyboardButton(text='Add picture to the task', callback_data='add picture')
    keyboard.add(add_more)
    keyboard.add(add_pic)
    bot.send_message(msg.from_user.id, "Task added", reply_markup=keyboard)


def add_picture(msg):
    db = sqlite3.connect('todo.db')
    cursor = db.cursor()
    task_id = cursor.execute(f'SELECT task_id FROM tasks WHERE user_id={msg.from_user.id} ORDER BY task_id DESC').fetchone()[0]
    cursor.execute(f"UPDATE tasks SET path_media='{msg.photo[-1].file_id}' WHERE task_id={int(task_id)}")
    db.commit()
    db.close()
    bot.send_message(msg.from_user.id, 'Photo added')

def show_tasks(msg):
    db = sqlite3.connect('todo.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM tasks where user_id={msg.from_user.id}")
    result = cursor.fetchall()
    if result:
        for x in result:
            keyboard = types.InlineKeyboardMarkup()
            change = types.InlineKeyboardButton(text='Check up', callback_data=x[0])
            keyboard.add(change)
            if x[4]:
                if x[3]:
                    bot.send_photo(msg.from_user.id, str(x[3]), caption=f'*{x[0]}\.* ~{x[2]}~', parse_mode='MarkdownV2', reply_markup=keyboard)
                else:
                    bot.send_message(msg.from_user.id, f'*{x[0]}\.* ~{x[2]}~', parse_mode='MarkdownV2', reply_markup=keyboard)
            else:
                if x[3]:
                    bot.send_photo(msg.from_user.id, str(x[3]), caption=f'*{x[0]}\.* `{x[2]}`', parse_mode='MarkdownV2', reply_markup=keyboard)
                else:
                    bot.send_message(msg.from_user.id, f'*{x[0]}\.* `{x[2]}`', parse_mode='MarkdownV2', reply_markup=keyboard)
    else:
        bot.send_message(msg.from_user.id, 'Empty to do')


def checkup(call):
    db = sqlite3.connect('todo.db')
    cursor = db.cursor()
    cursor.execute(f"UPDATE tasks SET status=1 WHERE user_id={call.from_user.id} AND task_id={call.data}")
    db.commit()
    db.close()

while True:
    try:
        bot.polling()
    except:
        pass