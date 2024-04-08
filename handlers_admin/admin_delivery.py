import asyncio
import logging
import sys
import sqlite3
from datetime import datetime

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import (Message,
                           InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery)
from config.config import TOKEN
import re
from aiogram import F
from aiogram.fsm.context import FSMContext
from utils.state import Admin_cura


async def dev_admin_menu(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        key_city = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Удалить заказ", callback_data='del_admin_delivery_')
            ],
            [
                InlineKeyboardButton(text="Просмотреть заказы", callback_data='show_admin_delivery_')
            ],
            [
                InlineKeyboardButton(text="Редактировать заказ", callback_data='edit_admin_delivery_')
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ]

        ])

        await bot.send_message(user_id, "Приветствую в боте Доставок.", reply_markup=key_city)
        await bot.delete_message(user_id, call.message.message_id)
    except:
        pass


async def add_delivery_name_cura(call: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name_admin FROM cura")
        admin_names = cursor.fetchall()
        conn.close()

        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=admin_name[0], callback_data=f'_cura_name_{admin_name[0]}') for admin_name in
                admin_names
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ]

        ])

        await bot.send_message(call.message.chat.id, "Выберите Курьера:", reply_markup=key_admin)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass




async def del_delivery_name_cura(call: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name_admin FROM cura")
        admin_names = cursor.fetchall()
        conn.close()

        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=admin_name[0], callback_data=f'_del_namecura_{admin_name[0]}') for admin_name
                in
                admin_names
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ]

        ])

        await bot.send_message(call.message.chat.id, "Выберите Курьера:", reply_markup=key_admin)
        await bot.delete_message(call.message.chat.id, call.message.message_id)

    except Exception as e:
        print(e)


async def del_delivery_month(call: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        user_id = call.message.chat.id
        name_cura = call.data.split('_')[3]
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT external_admin FROM cura WHERE name_admin = ?''', (name_cura,))
        result = cursor.fetchone()
        id_cura = result[0]
        conn.close()
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        sql_query = '''
                    SELECT DISTINCT data_create
                    FROM data_shop
                    WHERE external_id = ?;
                '''
        cursor.execute(sql_query, (id_cura,))
        results = cursor.fetchall()
        conn.close()
        if len(results) == 0:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='admin_return_')
                ]

            ])

            await bot.send_message(user_id, "Нет доступных Заказов у курьера.", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            key_city = InlineKeyboardMarkup(inline_keyboard=[])

            for i in range(0, len(results), 2):
                row = []
                # Добавляем две кнопки в строку, если есть два города
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=results[i][0], callback_data=f'month_set_{results[i][0]}_{id_cura}'))
                    row.append(
                        InlineKeyboardButton(text=results[i + 1][0],
                                             callback_data=f'month_set_{results[i + 1][0]}_{id_cura}'))
                    key_city.inline_keyboard.append(row)
                else:
                    row.append(
                        InlineKeyboardButton(text=results[i][0], callback_data=f'month_set_{results[i][0]}_{id_cura}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ])
            await bot.send_message(user_id, f"Кура: {name_cura}\n"
                                            "Выберите месяц:", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def del_delivery_day(call: CallbackQuery, bot: Bot):
    try:
        month = call.data.split('_')[2]
        id_cura = call.data.split('_')[3]

        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        sql_query = '''
                    SELECT DISTINCT data_day
                    FROM data_shop
                    WHERE external_id = ? AND data_create = ?;
                '''
        cursor.execute(sql_query, (id_cura, month))

        # Получение результатов запроса
        results = cursor.fetchall()
        conn.close()
        print(results)

        if len(results) == 0:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='admin_return_')
                ]

            ])

            await bot.send_message(user_id, "Нет доступных дат у курьера для просмотра.", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            key_city = InlineKeyboardMarkup(inline_keyboard=[])

            for i in range(0, len(results), 2):
                row = []
                # Добавляем две кнопки в строку, если есть два города
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=results[i][0],
                                             callback_data=f'day_set_{results[i][0]}_{month}_{id_cura}'))
                    row.append(
                        InlineKeyboardButton(text=results[i + 1][0],
                                             callback_data=f'day_set_{results[i + 1][0]}_{month}_{id_cura}'))
                # Если остался один город, добавляем его в отдельную кнопку
                else:
                    row.append(
                        InlineKeyboardButton(text=results[i][0],
                                             callback_data=f'day_set_{results[i][0]}_{month}_{id_cura}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ])
            await bot.send_message(user_id, f"Курьер: {id_cura}\n"
                                            f"Выберите день для месяца {month} :", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def del_delivery_mid(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        day = call.data.split('_')[2]
        month = call.data.split('_')[3]
        id_cura = call.data.split('_')[4]
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        cursor.execute(
            '''SELECT number_delivery FROM data_shop WHERE external_id = ? AND data_create = ? AND data_day = ?''',
            (id_cura, month, day))
        results = cursor.fetchall()
        conn.close()
        if len(results) == 0:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='admin_return_')
                ]

            ])

            await bot.send_message(user_id, "Нет доступных заказов у курьера для удаления.", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            key_city = InlineKeyboardMarkup(inline_keyboard=[])

            for i in range(0, len(results), 2):
                row = []
                # Добавляем две кнопки в строку, если есть два города
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=results[i][0],
                                             callback_data=f'del_dev_end_{results[i][0]}_{month}_{id_cura}_{day}'))
                    row.append(
                        InlineKeyboardButton(text=results[i + 1][0],
                                             callback_data=f'del_dev_end_{results[i + 1][0]}_{month}_{id_cura}_{day}'))
                # Если остался один город, добавляем его в отдельную кнопку
                else:
                    row.append(
                        InlineKeyboardButton(text=results[i][0],
                                             callback_data=f'del_dev_end_{results[i][0]}_{month}_{id_cura}_{day}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ])
            await bot.send_message(user_id, f"Курьер: {id_cura}\n"
                                            f"Месяц : {month}\n"
                                            f"День : {day}", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def del_delivery_center(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        number_delivery = call.data.split('_')[3]
        month = call.data.split('_')[4]
        id_cura = call.data.split('_')[5]
        day = call.data.split('_')[6]

        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        cursor.execute('''SELECT id, number_delivery, adress_delivery, coll_tovar, name_tovar, coll_tovar_tho, name_tovar_tho,
                                        coll_tovar_three, name_tovar_three, coll_tovar_four, name_tovar_four, price_shop, price_deliver,
                                        data_create, data_day, cash_card, external_id 
                                  FROM data_shop 
                                  WHERE number_delivery = ? AND data_create = ? AND data_day = ? AND external_id = ?''',
                       (number_delivery, month, day, id_cura))

        results = cursor.fetchall()
        conn.close()
        adress_delivery = ""
        coll_tovar = ""
        name_tovar = ""
        coll_tovar_tho = ""
        name_tovar_tho = ""
        coll_tovar_three = ""
        name_tovar_three = ""
        coll_tovar_four = ""
        name_tovar_four = ""
        cash_card = ""
        price_shop = ""
        price_deliver = ""
        id = 0
        for row in results:
            (id, number_delivery, adress_delivery, coll_tovar, name_tovar, coll_tovar_tho, name_tovar_tho,
             coll_tovar_three, name_tovar_three, coll_tovar_four, name_tovar_four, price_shop,
             price_deliver, data_create, data_day, cash_card, external_id) = row
        summ = int(price_shop) + int(price_deliver)
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Подтвердить ✅", callback_data=f'del_dev_yes_{id}'),
            ],
            [
                InlineKeyboardButton(text="Отменить ❌", callback_data=f'day_set_{day}_{month}_{id_cura}'),
            ]
        ])
        await bot.send_message(user_id,
                               f"Вы действительно хотите удалить заказ?\n"
                               f"Месяц : {month}\n"
                               f"День : {day}\n"
                               f"Номер заказа: {number_delivery}\n"
                               f"Адресс заказа {adress_delivery}\n"
                               f"1 товар:{name_tovar} / Кол-во : {coll_tovar}\n"
                               f"2 товар:{name_tovar_tho} / Кол-во : {coll_tovar_tho}\n"
                               f"3 товар:{name_tovar_three} / Кол-во : {coll_tovar_three}\n"
                               f"4 товар:{name_tovar_four} / Кол-во : {coll_tovar_four}\n"
                               f"Цена заказа :{summ}({price_deliver})\n"
                               f"Способ оплаты : {cash_card}", reply_markup=key_admin)
        await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)
        await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def del_delivery_end(call: CallbackQuery, bot: Bot):
    try:
        id = call.data.split('_')[3]

        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute('''DELETE FROM data_shop WHERE id = ?''', (id,))
        conn.commit()
        conn.close()
        key_city = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Меню", callback_data='admin_return_')
            ]
        ])
        await bot.send_message(call.message.chat.id, "Заказ успешно удален", reply_markup=key_city)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        print(e)


async def show_delivery_name_cura(call: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name_admin FROM cura")
        admin_names = cursor.fetchall()
        conn.close()

        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=admin_name[0], callback_data=f'_show_namecura_{admin_name[0]}') for admin_name
                in
                admin_names
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ]

        ])

        await bot.send_message(call.message.chat.id, "Просмотр\n"
                                                     "Выберите Курьера:", reply_markup=key_admin)
        await bot.delete_message(call.message.chat.id, call.message.message_id)

    except Exception as e:
        print(e)


async def show_delivery_month(call: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        user_id = call.message.chat.id
        name_cura = call.data.split('_')[3]
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT external_admin FROM cura WHERE name_admin = ?''', (name_cura,))
        result = cursor.fetchone()
        id_cura = result[0]
        conn.close()
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        sql_query = '''
                    SELECT DISTINCT data_create
                    FROM data_shop
                    WHERE external_id = ?;
                '''
        cursor.execute(sql_query, (id_cura,))
        results = cursor.fetchall()
        conn.close()
        if len(results) == 0:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='admin_return_')
                ]

            ])

            await bot.send_message(user_id, "Нет доступных Заказов у курьера.", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            key_city = InlineKeyboardMarkup(inline_keyboard=[])

            for i in range(0, len(results), 2):
                row = []
                # Добавляем две кнопки в строку, если есть два города
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=results[i][0], callback_data=f'month_show_{results[i][0]}_{id_cura}'))
                    row.append(
                        InlineKeyboardButton(text=results[i + 1][0],
                                             callback_data=f'month_show_{results[i + 1][0]}_{id_cura}'))
                    key_city.inline_keyboard.append(row)
                else:
                    row.append(
                        InlineKeyboardButton(text=results[i][0], callback_data=f'month_show_{results[i][0]}_{id_cura}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ])
            await bot.send_message(user_id, f"Просмотр\n"
                                            f"Кура: {name_cura}\n"
                                            "Выберите месяц:", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def show_delivery_day(call: CallbackQuery, bot: Bot):
    try:
        month = call.data.split('_')[2]
        id_cura = call.data.split('_')[3]

        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        sql_query = '''
                    SELECT DISTINCT data_day
                    FROM data_shop
                    WHERE external_id = ?;
                '''
        cursor.execute(sql_query, (id_cura,))

        # Получение результатов запроса
        results = cursor.fetchall()
        conn.close()
        print(results)

        if len(results) == 0:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='admin_return_')
                ]

            ])

            await bot.send_message(user_id, "Нет доступных дат у курьера для просмотра.", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            key_city = InlineKeyboardMarkup(inline_keyboard=[])

            for i in range(0, len(results), 2):
                row = []
                # Добавляем две кнопки в строку, если есть два города
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=results[i][0],
                                             callback_data=f'day_show_{results[i][0]}_{month}_{id_cura}'))
                    row.append(
                        InlineKeyboardButton(text=results[i + 1][0],
                                             callback_data=f'day_show_{results[i + 1][0]}_{month}_{id_cura}'))
                # Если остался один город, добавляем его в отдельную кнопку
                else:
                    row.append(
                        InlineKeyboardButton(text=results[i][0],
                                             callback_data=f'day_show_{results[i][0]}_{month}_{id_cura}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ])
            await bot.send_message(user_id, f"Просмотр\n"
                                            f"Курьер: {id_cura}\n"
                                            f"Выберите день для месяца {month} :", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def show_delivery_mid(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        day = call.data.split('_')[2]
        month = call.data.split('_')[3]
        id_cura = call.data.split('_')[4]
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        cursor.execute('''SELECT id, number_delivery, adress_delivery, coll_tovar, name_tovar, coll_tovar_tho, name_tovar_tho,
                                        coll_tovar_three, name_tovar_three, coll_tovar_four, name_tovar_four, price_shop, price_deliver,
                                        data_create, data_day, cash_card, external_id 
                                  FROM data_shop 
                                  WHERE data_create = ? AND data_day = ? AND external_id = ?''',
                       (month, day, id_cura))
        results = cursor.fetchall()
        conn.close()
        if len(results) == 0:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='admin_return_')
                ]

            ])

            await bot.send_message(user_id, "Нет доступных заказов у курьера для удаления.", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            message_text = ""
            if results:
                for result in results:
                    (id, number_delivery, adress_delivery, coll_tovar, name_tovar, coll_tovar_tho, name_tovar_tho,
                     coll_tovar_three, name_tovar_three, coll_tovar_four, name_tovar_four, price_shop,
                     price_deliver, data_create, data_day, cash_card, external_id) = result
                    message_text += f"Месяц : {data_create}\n"
                    message_text += f"День : {data_day}\n"
                    message_text += f"Номер заказа: {number_delivery}\n"
                    message_text += f"Адресс заказа {adress_delivery}\n"
                    message_text += f"1 товар: {name_tovar} / Кол-во : {coll_tovar}\n"
                    message_text += f"2 товар: {name_tovar_tho} / Кол-во : {coll_tovar_tho}\n"
                    message_text += f"3 товар: {name_tovar_three} / Кол-во : {coll_tovar_three}\n"
                    message_text += f"4 товар: {name_tovar_four} / Кол-во : {coll_tovar_four}\n"
                    summ = int(result[11]) + int(result[12])
                    message_text += f"Цена заказа : {summ}({price_deliver})\n"

                    message_text += f"Способ оплаты {cash_card}\n"
                    message_text += f"ID курьера : {external_id}\n\n"

                    key_admin = InlineKeyboardMarkup(inline_keyboard=[
                        [
                            InlineKeyboardButton(text="Меню", callback_data=f'admin_return_'),
                        ],
                        [
                            InlineKeyboardButton(text="Назад ", callback_data=f'month_show_{month}_{id_cura}'),
                        ]
                    ])
                await bot.send_message(user_id,
                                       message_text, reply_markup=key_admin)
                await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def show_delivery_end(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        number_delivery = call.data.split('_')[3]
        month = call.data.split('_')[4]
        id_cura = call.data.split('_')[5]
        day = call.data.split('_')[6]

        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        cursor.execute('''SELECT id, number_delivery, adress_delivery, coll_tovar, name_tovar, coll_tovar_tho, name_tovar_tho,
                                coll_tovar_three, name_tovar_three, coll_tovar_four, name_tovar_four, price_shop, price_deliver,
                                data_create, data_day, cash_card, external_id 
                          FROM data_shop 
                          WHERE number_delivery = ? AND data_create = ? AND data_day = ? AND external_id = ?''',
                       (number_delivery, month, day, id_cura))

        results = cursor.fetchall()
        conn.close()
        adress_delivery = ""
        coll_tovar = ""
        name_tovar = ""
        coll_tovar_tho = ""
        name_tovar_tho = ""
        coll_tovar_three = ""
        name_tovar_three = ""
        coll_tovar_four = ""
        name_tovar_four = ""
        cash_card = ""
        price_shop = ""
        price_deliver = ""
        id = 0
        for row in results:
            (id, number_delivery, adress_delivery, coll_tovar, name_tovar,coll_tovar_tho, name_tovar_tho,
             coll_tovar_three, name_tovar_three, coll_tovar_four, name_tovar_four, price_shop,
             price_deliver, data_create, data_day, cash_card, external_id) = row
        summ = int(price_shop) + int(price_deliver)
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Меню", callback_data=f'admin_return_'),
            ],
            [
                InlineKeyboardButton(text="Назад ", callback_data=f'day_set_{day}_{month}_{id_cura}'),
            ]
        ])
        await bot.send_message(user_id,
                               f"Просмотр\n"
                               f"Месяц : {month}\n"
                               f"День : {day}\n"
                               f"Номер заказа: {number_delivery}\n"
                               f"Адресс заказа {adress_delivery}\n"
                               f"1 товар:{name_tovar} / Кол-во : {coll_tovar}\n"
                               f"2 товар:{name_tovar_tho} / Кол-во : {coll_tovar_tho}\n"
                               f"3 товар:{name_tovar_three} / Кол-во : {coll_tovar_three}\n"
                               f"4 товар:{name_tovar_four} / Кол-во : {coll_tovar_four}\n"
                               f"Цена заказа :{summ}({price_deliver})\n"
                               f"Способ оплаты : {cash_card}", reply_markup=key_admin)
        await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def edit_delivery_month(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        sql_query = '''
                            SELECT DISTINCT data_create
                            FROM data_shop
                        '''
        cursor.execute(sql_query)
        results = cursor.fetchall()
        conn.close()
        if len(results) == 0:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='delivery_set')
                ]

            ])

            await bot.send_message(user_id, "Нет доступных Заказов у курьера.", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            key_city = InlineKeyboardMarkup(inline_keyboard=[])

            for i in range(0, len(results), 2):
                row = []
                # Добавляем две кнопки в строку, если есть два города
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=results[i][0], callback_data=f'edit_dev_{results[i][0]}'))
                    row.append(
                        InlineKeyboardButton(text=results[i + 1][0],
                                             callback_data=f'edit_dev_{results[i + 1][0]}'))
                    key_city.inline_keyboard.append(row)
                else:
                    row.append(
                        InlineKeyboardButton(text=results[i][0], callback_data=f'edit_dev_{results[i][0]}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='delivery_set')
            ])
            await bot.send_message(user_id, "Выберите месяц:", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def edit_delivery_day(call: CallbackQuery, bot: Bot):
    try:
        month = call.data.split('_')[2]

        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
                    SELECT DISTINCT data_day
                    FROM data_shop
                '''
        cursor.execute(sql_query)
        results = cursor.fetchall()
        conn.close()

        if len(results) == 0:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='edit_admin_delivery_')
                ]

            ])

            await bot.send_message(user_id, "Нет доступных дат у курьера для просмотра.", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            key_city = InlineKeyboardMarkup(inline_keyboard=[])

            for i in range(0, len(results), 2):
                row = []
                # Добавляем две кнопки в строку, если есть два города
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=results[i][0],
                                             callback_data=f'day_edit_{results[i][0]}_{month}'))
                    row.append(
                        InlineKeyboardButton(text=results[i + 1][0],
                                             callback_data=f'day_edit_{results[i + 1][0]}_{month}'))
                # Если остался один город, добавляем его в отдельную кнопку
                else:
                    row.append(
                        InlineKeyboardButton(text=results[i][0],
                                             callback_data=f'day_edit_{results[i][0]}_{month}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='edit_admin_delivery_')
            ])
            await bot.send_message(user_id, f"Выберите день для месяца {month} :", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def edit_delivery_mid(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        day = call.data.split('_')[2]
        month = call.data.split('_')[3]
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        cursor.execute(
            '''SELECT number_delivery FROM data_shop WHERE data_create = ? AND data_day = ?''',
            (month, day))
        results = cursor.fetchall()
        conn.close()
        if len(results) == 0:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='edit_dev_')
                ]

            ])

            await bot.send_message(user_id, "Нет доступных заказов у курьера для удаления.", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            key_city = InlineKeyboardMarkup(inline_keyboard=[])

            for i in range(0, len(results), 2):
                row = []
                # Добавляем две кнопки в строку, если есть два города
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=results[i][0],
                                             callback_data=f'edit_edit_end_{results[i][0]}_{month}_{day}'))
                    row.append(
                        InlineKeyboardButton(text=results[i + 1][0],
                                             callback_data=f'edit_edit_end_{results[i + 1][0]}_{month}_{day}'))
                # Если остался один город, добавляем его в отдельную кнопку
                else:
                    row.append(
                        InlineKeyboardButton(text=results[i][0],
                                             callback_data=f'edit_edit_end_{results[i][0]}_{month}_{day}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='edit_dev_')
            ])
            await bot.send_message(user_id, f"Месяц : {month}\n"
                                            f"День : {day}", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def edit_delivery_center(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        number_delivery = call.data.split('_')[3]
        month = call.data.split('_')[4]
        day = call.data.split('_')[5]

        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        cursor.execute('''SELECT id, number_delivery, adress_delivery, coll_tovar, name_tovar, price_shop, price_deliver,
                                data_create, data_day, cash_card, external_id 
                          FROM data_shop 
                          WHERE number_delivery = ? AND data_create = ? AND data_day = ?''',
                       (number_delivery, month, day))
        results = cursor.fetchall()
        conn.close()
        adress_delivery = ""
        coll_tovar = ""
        name_tovar = ""
        coll_tovar_tho = ""
        name_tovar_tho = ""
        coll_tovar_three = ""
        name_tovar_three = ""
        coll_tovar_four = ""
        name_tovar_four = ""
        cash_card = ""
        price_shop = ""
        price_deliver = ""
        external_id = ""
        id = 0
        for row in results:
            (id, number_delivery, adress_delivery, coll_tovar, name_tovar, coll_tovar_tho, name_tovar_tho,
             coll_tovar_three, name_tovar_three, coll_tovar_four, name_tovar_four, price_shop,
             price_deliver, data_create, data_day, cash_card, external_id) = row
        summ = int(price_shop) + int(price_deliver)
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
            SELECT name_admin
            FROM cura
            WHERE external_admin = ?
        '''
        cursor.execute(sql_query, (external_id,))
        results = cursor.fetchall()
        conn.close()
        name_cura = results[0]

        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Месяц",
                                     callback_data=f'edit_month_end_{month}_{number_delivery}_{day}_{id}'),
                InlineKeyboardButton(text="День", callback_data=f'edit_day_end_{month}_{number_delivery}_{day}_{id}')
            ],
            [
                InlineKeyboardButton(text="Номер заказа",
                                     callback_data=f'edit_number_end_{month}_{number_delivery}_{day}_{id}'),
                InlineKeyboardButton(text="Адрес заказа",
                                     callback_data=f'edit_address_end_{adress_delivery}_{number_delivery}_{month}_{day}_{id}')
            ],
            [
                InlineKeyboardButton(text="Кол-во",
                                     callback_data=f'edit_coll_tovar_end_{coll_tovar}_{number_delivery}_{month}_{day}_{id}'),
                InlineKeyboardButton(text="Наим-ие товара",
                                     callback_data=f'edit_name_tovar_end_{name_tovar}_{number_delivery}_{month}_{day}_{id}')
            ],
            [
                InlineKeyboardButton(text="Цена шопа",
                                     callback_data=f'edit_price_shop_end_{price_shop}_{number_delivery}_{month}_{day}_{id}'),
                InlineKeyboardButton(text="Цена курьера",
                                     callback_data=f'edit_price_deliver_end_{price_deliver}_{number_delivery}_{month}_{day}_{id}')
            ],
            [
                InlineKeyboardButton(text="Способ оплаты",
                                     callback_data=f'edit_cash_card_end_{cash_card}_{number_delivery}_{month}_{day}_{id}'),
                InlineKeyboardButton(text="Курьер",
                                     callback_data=f'edit_name_cura_end_{name_cura}_{number_delivery}_{month}_{day}_{id}')
            ],
            [
                InlineKeyboardButton(text="Назад ", callback_data=f'day_edit_{day}_{month}'),
                InlineKeyboardButton(text="Меню", callback_data=f'admin_return_')
            ]
        ])
        await bot.send_message(user_id,
                               f"Выберите строку для редактирования\n"
                               f"Месяц : {month}\n"
                               f"День : {day}\n"
                               f"Номер заказа: {number_delivery}\n"
                               f"Адресс заказа {adress_delivery}\n"
                               f"1 товар:{name_tovar} / Кол-во : {coll_tovar}\n"
                               f"2 товар:{name_tovar_tho} / Кол-во : {coll_tovar_tho}\n"
                               f"3 товар:{name_tovar_three} / Кол-во : {coll_tovar_three}\n"
                               f"4 товар:{name_tovar_four} / Кол-во : {coll_tovar_four}\n"
                               f"Цена заказа :{summ}({price_deliver})\n"
                               f"Способ оплаты : {cash_card}", reply_markup=key_admin)
        await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)

