import telebot
import sqlite3 
from telebot import types


bot = telebot.TeleBot('')
category = ''
val = 0
flag = 0
cash = 0


@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('Income.sql')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS income (category varchar(50) primary key, val int)')
    conn.commit()
    cur.close()
    conn.close()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Поздороваться")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "👋 Привет, я помогаю людям вести денежные расходы и доходы!", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '👋 Поздороваться':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True) 
        btn1 = types.KeyboardButton('Добавить траты')
        btn2 = types.KeyboardButton('Вывести текущий баланс за месяц')
        btn3 = types.KeyboardButton('Обнулить траты для следующего месяца')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, 'Мои возможности ниже', reply_markup=markup)
    elif message.text == 'Добавить траты':
        bot.send_message(message.from_user.id, 'Введите категорию и трату. Пример: Банк 1000', parse_mode='Markdown')
        bot.register_next_step_handler(message, write_data)
    elif message.text == 'Вывести текущий баланс за месяц':
        global cash
        conn = sqlite3.connect('Income.sql')
        cur = conn.cursor()
        all_in = '''Категория Сумма\n'''
        for cat, val in cur.execute("SELECT * FROM income"):
            all_in += cat + ' ' + str(val) + "руб.\n"
            cash += val 
        all_in += "\nОбщаяя сумма трат " + str(cash) + " руб."
        bot.send_message(message.from_user.id, all_in)
        conn.commit()
        cur.close()
        conn.close()
    elif message.text == 'Обнулить траты для следующего месяца':
        conn = sqlite3.connect('Income.sql')
        cur = conn.cursor()
        cur.execute("DELETE FROM income")
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(message.from_user.id, 'Очистка произошла успешно')

def write_data(message):
    global category
    global value
    splt_string = message.text.split()
    category = splt_string[0]
    value = int(splt_string[1])
    conn = sqlite3.connect('Income.sql')
    cur = conn.cursor()
    info = cur.execute('SELECT * FROM income WHERE category=?', (category, )).fetchall()
    if len(info) == 0:
        cur.execute("INSERT INTO income (category, val) VALUES ('%s', '%d')" % (category, value))
        bot.send_message(message.from_user.id, 'Я создал поле')
    else:
        cur.execute("SELECT val FROM income WHERE category='%s'" % (category))
        old_value = cur.fetchone()[0]
        summ = int(old_value) + value
        cur.execute("UPDATE income SET val='%s' WHERE category='%s'" % (summ, category))
        bot.send_message(message.from_user.id, 'Все прошло успешно, теперь значение обновлено')
    conn.commit()
    cur.close()
    conn.close()
bot.polling(none_stop=True, interval=0) 

