import telebot
import sqlite3
from telebot import types
import os


bot = telebot.TeleBot("6524296769:AAGRFxfadYnCs1A_3VqK8MKDD5zM_AOSbUA")
category = ""
val = 0


@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    db_name = f"Income_{user_id}.sql"
    path_to_file = r"C:\Users\Никита\Desktop\Project\\" + db_name
    if not os.path.exists(path_to_file):
        try:
            conn = sqlite3.connect(db_name)
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS income (category varchar(50) primary key, val int)"
            )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при создании таблицы: {e}")
        finally:
            cur.close()
            conn.close()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Поздороваться")
    markup.add(btn1)
    bot.send_message(
        message.from_user.id,
        "Привет, я помогаю людям вести денежные расходы и доходы!",
        reply_markup=markup,
    )


@bot.message_handler(content_types=["text"])
def get_text_messages(message):
    user_id = message.from_user.id
    db_name = f"Income_{user_id}.sql"
    if message.text == "👋 Поздороваться" or message.text == "Начало":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Добавить траты")
        btn2 = types.KeyboardButton("Вывести категории")
        btn3 = types.KeyboardButton("Вывести текущую сумму трат за месяц")
        btn4 = types.KeyboardButton("Обнулить траты для следующего месяца")
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(
            message.from_user.id, "Мои возможности ниже", reply_markup=markup
        )
    elif message.text == "Добавить траты":
        bot.send_message(
            message.from_user.id,
            "Введите категорию и трату. Пример: Ресторан 1000. (Номинал не нужно писать)",
            parse_mode="Markdown",
        )
        bot.register_next_step_handler(message, lambda msg: write_data(msg, db_name))
    elif message.text == "Вывести категории":
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        cur.execute("SELECT category FROM income")
        categories = cur.fetchall()
        conn.close()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for category in categories:
            btn = types.KeyboardButton(category[0])
            markup.add(btn)
        btn_back = types.KeyboardButton("Начало")
        markup.add(btn_back)
        bot.send_message(
            message.from_user.id, "Выберите категорию:", reply_markup=markup
        )
        bot.register_next_step_handler(
            message, lambda msg: handle_category(msg, db_name)
        )
    elif message.text == "Вывести текущую сумму трат за месяц":
        cash = 0
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        all_in = """Категория Сумма\n"""
        for cat, val in cur.execute("SELECT * FROM income"):
            all_in += cat + " " + str(val) + "руб.\n"
            cash += val
        all_in += "\nОбщаяя сумма трат " + str(cash) + " руб."
        bot.send_message(message.from_user.id, all_in)
        conn.commit()
        cur.close()
        conn.close()
    elif message.text == "Обнулить траты для следующего месяца":
        conn = sqlite3.connect(db_name)
        cash = 0
        cur = conn.cursor()
        cur.execute("DELETE FROM income")
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(message.from_user.id, "Очистка произошла успешно")


def write_data(message, db_name):
    global category
    user_id = message.from_user.id
    db_name = f"Income_{user_id}.sql"
    global value
    splt_string = message.text.split()
    category = splt_string[0]
    try:
        value = int(splt_string[1])
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        info = cur.execute(
            "SELECT * FROM income WHERE category=?", (category,)
        ).fetchall()
        if len(info) == 0:
            cur.execute(
                "INSERT INTO income (category, val) VALUES (?, ?)", (category, value)
            )
            bot.send_message(message.from_user.id, "Я добавил трату")
        else:
            cur.execute("SELECT val FROM income WHERE category= ?", (category,))
            old_value = cur.fetchone()[0]
            summ = int(old_value) + value
            cur.execute("UPDATE income SET val= ? WHERE category= ?", (summ, category))
            bot.send_message(
                message.from_user.id, "Все прошло успешно, теперь значение обновлено"
            )
        conn.commit()
        cur.close()
        conn.close()
    except ValueError:
        bot.send_message(message.from_user.id, "Ошибка в написаннии суммы траты")


def handle_category(message, db_name):
    if message.text == "Начало":
        bot.register_next_step_handler(message, get_text_messages)
    else:
        user_id = message.from_user.id
        db_name = f"Income_{user_id}.sql"
        selected_category = message.text
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        cur.execute(
            "SELECT SUM(val) FROM income WHERE category = ?", (selected_category,)
        )
        total_expenses = cur.fetchone()[0]
        conn.close()
        bot.send_message(
            message.from_user.id,
            f"Вот сумма расходов по выбранной категории:\n| Категория | Сумма |\n{'-' * 35}\n| {selected_category}  | {str(total_expenses) + 'руб.'} |",
            parse_mode="Markdown",
        )


bot.polling(none_stop=True, interval=0, timeout=600)
