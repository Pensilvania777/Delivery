from aiogram import Bot
from aiogram.types import (Message,
                           InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery)
import sqlite3
import re
from utils.state import Cura_tovar, Tovar_cura
import logging
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta


async def cura_tovar_menu(call: CallbackQuery, bot: Bot):
    try:
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Добавить товар курьеру", callback_data='add_tovar_cura_')
            ],
            [
                InlineKeyboardButton(text="Редактировать товар курьеру", callback_data='redit_tovar_cura_')
            ],
            [
                InlineKeyboardButton(text="Удалить товар курьеру", callback_data='del_tovar_cura_')
            ],
            [
                InlineKeyboardButton(text="Просмотр товара у курьера", callback_data='show_tovar_cura_')

            ],
            [
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ]
        ])
        await bot.send_message(call.message.chat.id, "Выберите действие.", reply_markup=key_admin)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        print(e)
async def cura_name_edit(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name_admin FROM cura")
        results = cursor.fetchall()
        conn.close()

        key_city = InlineKeyboardMarkup(inline_keyboard=[])
        if len(results) == 0:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='tovar_set')
                ]

            ])

            await bot.send_message(user_id, "Нет доступных курьеров.", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            for i in range(0, len(results), 2):
                row = []
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=f"Курьер : {results[i][0]}",
                                             callback_data=f'cura_edit_edit_{results[i][0]}'))
                    row.append(
                        InlineKeyboardButton(text=f"Курьер : {results[i + 1][0]}",
                                             callback_data=f'cura_edit_edit_{results[i + 1][0]}'))
                else:
                    row.append(
                        InlineKeyboardButton(text=f"Курьер : {results[i][0]}",
                                             callback_data=f'cura_edit_edit_{results[i][0]}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='tovar_set')
            ])
            await bot.send_message(user_id, "Выберите Курьера:", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)

    except Exception as e:
        print(e)

async def cura_tovar_edit(call: CallbackQuery, bot: Bot):
    try:
        external_cura_value = call.data.split('_')[3]
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = f'''
            SELECT name_item, coll_tovar
            FROM cura_tovar
            WHERE external_cura = ?;
        '''
        cursor.execute(sql_query, (external_cura_value,))
        rows = cursor.fetchall()
        name_item = ""
        coll_tovar = ""
        message = ""
        for row in rows:
            name_item, coll_tovar = row
            print(name_item, coll_tovar)
            formatted_name_item = f"Товар : {name_item}\n"
            formatted_coll_tovar = f"Кол-во : {coll_tovar}\n\n"
            message += formatted_name_item + formatted_coll_tovar
        print(message)
        conn.close()
        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name_item FROM cura_tovar WHERE external_cura = ?;", (external_cura_value,))
        results = cursor.fetchall()
        conn.close()

        key_city = InlineKeyboardMarkup(inline_keyboard=[])
        if len(results) == 0:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='redit_tovar_cura_')
                ]

            ])

            await bot.send_message(user_id, "Нет доступных курьеров.", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            for i in range(0, len(results), 2):
                row = []
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=f"Товар : {results[i][0]}",
                                             callback_data=f'cura_tovar_edit_{results[i][0]}_{external_cura_value}'))
                    row.append(
                        InlineKeyboardButton(text=f"Товар : {results[i + 1][0]}",
                                             callback_data=f'cura_tovar_edit_{results[i + 1][0]}_{external_cura_value}'))
                else:
                    row.append(
                        InlineKeyboardButton(text=f"Товар : {results[i][0]}",
                                             callback_data=f'cura_tovar_edit_{results[i][0]}_{external_cura_value}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='redit_tovar_cura_')
            ])

            await bot.send_message(call.message.chat.id, f"Курьер {external_cura_value}\n\n"
                                                         f"{message}\n"
                                                         f"Выберите товар для изменения: ", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)

async def cura_mid_edit(call: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        external_cura_value = call.data.split('_')[4]
        name_tovar = call.data.split('_')[3]

        await state.update_data(external_cura=external_cura_value)
        await state.update_data(name_tovar=name_tovar)
        await bot.send_message(call.message.chat.id, f"Укажите новое кол-во товара {name_tovar}: ")
        await state.set_state(Tovar_cura.tovar_cura)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        print(e)

async def cura_end_edit(message: Message, bot: Bot, state: FSMContext):
    try:
        coll_tovar = message.text
        data = await state.get_data()
        external_cura = data.get('external_cura')
        name_tovar = data.get('name_tovar')

        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
            UPDATE cura_tovar
            SET coll_tovar = ?
            WHERE external_cura = ? AND name_item = ?;
        '''
        cursor.execute(sql_query, (coll_tovar, external_cura, name_tovar))
        conn.commit()
        conn.close()
        await bot.delete_message(message.chat.id, message.message_id - 1)
        key_city = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ]
        ])
        await bot.send_message(message.chat.id, f"Новое кол-во {coll_tovar} товара {name_tovar}. ", reply_markup=key_city)
        await bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        print(e)






async def cura_name_add(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name_admin FROM cura")
        results = cursor.fetchall()
        conn.close()

        key_city = InlineKeyboardMarkup(inline_keyboard=[])
        if len(results) == 0:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='admin_return_')
                ]

            ])

            await bot.send_message(user_id, "Нет доступных курьеров.", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            for i in range(0, len(results), 2):
                row = []
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=f"Курьер : {results[i][0]}",
                                             callback_data=f'cura_name_{results[i][0]}'))
                    row.append(
                        InlineKeyboardButton(text=f"Курьер : {results[i + 1][0]}",
                                             callback_data=f'cura_name_{results[i + 1][0]}'))
                else:
                    row.append(
                        InlineKeyboardButton(text=f"Курьер : {results[i][0]}",
                                             callback_data=f'cura_name_{results[i][0]}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ])
            await bot.send_message(user_id, "Выберите Курьера:", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def cura_tovar_add(call: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        cura = call.data.split('_')[2]
        await state.update_data(cura=cura)
        user_id = call.message.chat.id
        key_city = InlineKeyboardMarkup(inline_keyboard=[])
        key_city.inline_keyboard.append([
            InlineKeyboardButton(text="Назад", callback_data='admin_return_')
        ])
        await state.set_state(Cura_tovar.name_tovar)
        await bot.send_message(user_id, "ШАБЛОН!\n"
                                        "ТОВАР КОЛИЧЕСТВО\n"
                                        "шш 100\n"
                                        "меф 100 \n"
                                        "================\n"
                                        "Введите весь товар: ", reply_markup=key_city)
        await bot.delete_message(user_id, call.message.message_id)

    except Exception as e:
        print(e)

async def cura_tovar_add_end(message: Message, state: FSMContext, bot: Bot):
    try:
        user_id = message.chat.id
        data = await state.get_data()
        cura = data.get('cura')
        print(cura)
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
            SELECT external_admin
            FROM cura
            WHERE name_admin = ?
        '''
        cursor.execute(sql_query, (cura,))
        result = cursor.fetchone()
        conn.close()
        if result:
            id_cura = result[0]
            name_tovar = message.text.lower()
            await bot.delete_message(user_id, message.message_id - 1)
            lines = name_tovar.split('\n')
            parsed_data = []
            print(f"Linii: {lines}")
            for line in lines:
                parts = line.split()
                if len(parts) == 2:
                    item = str(parts[0])
                    quantity = str(parts[1])
                    parsed_data.append((item, quantity))
                    conn = sqlite3.connect('shop.db')
                    cursor = conn.cursor()
                    sql_query = '''
                                INSERT INTO cura_tovar (external_cura, name_item, coll_tovar)
                                VALUES (?, ?, ?)
                            '''
                    cursor.execute(sql_query, (id_cura, item, quantity))
                    conn.commit()
                    conn.close()
                    print(parsed_data)
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='admin_return_')
                ]
            ])
            await bot.send_message(user_id, "Товар успешно добавлен:\n"
                                            f"Курьеру : {cura}\n"
                                            f"Товар : \n{name_tovar}", reply_markup=key_city)
            await bot.delete_message(user_id, message.message_id)
        else:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='admin_return_')
                ]
            ])
            await bot.send_message(user_id, "Такого курьера нет в базе данных.", reply_markup=key_city)
            await bot.delete_message(user_id, message.message_id)
    except Exception as e:
        print(e)

async def cura_del_name(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name_admin FROM cura")
        results = cursor.fetchall()
        conn.close()

        key_city = InlineKeyboardMarkup(inline_keyboard=[])
        if len(results) == 0:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='admin_return_')
                ]

            ])

            await bot.send_message(user_id, "Нет доступных курьеров.", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            for i in range(0, len(results), 2):
                row = []
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=f"Курьер : {results[i][0]}",
                                             callback_data=f'cura_del_{results[i][0]}'))
                    row.append(
                        InlineKeyboardButton(text=f"Курьер : {results[i + 1][0]}",
                                             callback_data=f'cura_del_{results[i + 1][0]}'))
                else:
                    row.append(
                        InlineKeyboardButton(text=f"Курьер : {results[i][0]}",
                                             callback_data=f'cura_del_{results[i][0]}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ])
            await bot.send_message(user_id, "Выберите Курьера:", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)

async def cura_del_tovar(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        cura = call.data.split('_')[2]
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
                            SELECT external_admin
                            FROM cura
                            WHERE name_admin = ?
                        '''
        cursor.execute(sql_query, (cura,))
        result = cursor.fetchone()
        conn.close()
        id_cura = result[0]
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name_item, coll_tovar FROM cura_tovar WHERE external_cura = ?", (id_cura,))
        results = cursor.fetchall()
        conn.close()
        key_city = InlineKeyboardMarkup(inline_keyboard=[])
        if len(results) == 0:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='admin_return_')
                ]

            ])

            await bot.send_message(user_id, f"Нет товара у курьера {cura}.", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            for i in range(0, len(results), 2):
                row = []
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=f"{results[i][0]} : {results[i][1]}",
                                             callback_data=f'tovar_del_{results[i][0]}_{results[i][1]}_{id_cura}'))
                    row.append(
                        InlineKeyboardButton(text=f"{results[i + 1][0]} : {results[i + 1][1]}",
                                             callback_data=f'tovar_del_{results[i + 1][0]}_{results[i + 1][1]}_{id_cura}'))
                else:
                    row.append(
                        InlineKeyboardButton(text=f"{results[i][0]} : {results[i][1]}",
                                             callback_data=f'tovar_del_{results[i][0]}_{results[i][1]}_{id_cura}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ])
            await bot.send_message(user_id, "Выберите товар для удаления:", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)

    except Exception as e:
        print(e)

async def cura_del_tovar_end(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        name_tovar = call.data.split('_')[2]
        coll_tovar = call.data.split('_')[3]
        cura = call.data.split('_')[4]
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        # Выполнение SQL-запроса на удаление записи
        cursor.execute('''DELETE FROM cura_tovar 
                                  WHERE external_cura = ? 
                                  AND name_item = ? 
                                  AND coll_tovar = ?''',
                       (cura, name_tovar, coll_tovar))

        # Применение изменений и закрытие соединения
        conn.commit()
        conn.close()
        key_city = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ]
        ])
        await bot.send_message(user_id, f"У курьера {cura} удален Товар {name_tovar} кол-во {coll_tovar}. ",
                               reply_markup=key_city)
        await bot.delete_message(user_id, call.message.message_id)


    except Exception as e:
        print(e)

async def cura_show_tovar(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name_admin FROM cura")
        results = cursor.fetchall()
        conn.close()

        key_city = InlineKeyboardMarkup(inline_keyboard=[])
        if len(results) == 0:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='admin_return_')
                ]

            ])

            await bot.send_message(user_id, "Нет доступных курьеров.", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            for i in range(0, len(results), 2):
                row = []
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=f"Курьер : {results[i][0]}",
                                             callback_data=f'cura_showtovar_{results[i][0]}'))
                    row.append(
                        InlineKeyboardButton(text=f"Курьер : {results[i + 1][0]}",
                                             callback_data=f'cura_showtovar_{results[i + 1][0]}'))
                else:
                    row.append(
                        InlineKeyboardButton(text=f"Курьер : {results[i][0]}",
                                             callback_data=f'cura_showtovar_{results[i][0]}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ])
            await bot.send_message(user_id, "Выберите Курьера:", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)

async def cura_show_tovar_end(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        cura = call.data.split('_')[2]
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
                    SELECT external_admin
                    FROM cura
                    WHERE name_admin = ?
                '''
        cursor.execute(sql_query, (cura,))
        result = cursor.fetchone()
        conn.close()
        id_cura = result[0]
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
                    SELECT * FROM cura_tovar WHERE external_cura = ?
                '''
        cursor.execute(sql_query, (id_cura,))
        rows = cursor.fetchall()
        conn.close()
        items_and_quantities = []
        for row in rows:
            item_and_quantity = f"{row[2]} - {row[3]}"
            items_and_quantities.append(item_and_quantity)

        # Теперь объединим все строки в одну, разделив их переносом строки
        item_coll_string = "\n".join(items_and_quantities)
        key_city = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ]
        ])
        await bot.send_message(user_id, f"Курьер : {cura}\n"
                                        f"Товар в наличии :\n"
                                        f"{item_coll_string}\n", reply_markup=key_city)
        await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)

