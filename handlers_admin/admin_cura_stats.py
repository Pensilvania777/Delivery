import asyncio
import logging
import sys
import sqlite3
from datetime import datetime, timedelta
from calendar import monthrange

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



async def stats_cura_name_day(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
            SELECT DISTINCT external_id
            FROM data_shop
        '''
        cursor.execute(sql_query)
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
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=results[i][0], callback_data=f'ex_cura_{results[i][0]}'))
                    row.append(
                        InlineKeyboardButton(text=results[i + 1][0],
                                             callback_data=f'ex_cura_{results[i + 1][0]}'))
                    key_city.inline_keyboard.append(row)
                else:
                    row.append(
                        InlineKeyboardButton(text=results[i][0], callback_data=f'ex_cura_{results[i][0]}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ])
            await bot.send_message(user_id, f"Выберите курьера", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)

    except Exception as e:
        print(e)


async def delivery_analys_month(call: CallbackQuery, bot: Bot):
    try:
        cura = call.data.split('_')[2]
        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        sql_query = '''
            SELECT DISTINCT data_create
            FROM data_shop
            WHERE external_id = ?;
        '''
        cursor.execute(sql_query, (cura,))
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
                        InlineKeyboardButton(text=results[i][0],
                                             callback_data=f'month_delivery_{results[i][0]}_{cura}'))
                    row.append(
                        InlineKeyboardButton(text=results[i + 1][0],
                                             callback_data=f'month_delivery_{results[i + 1][0]}_{cura}'))
                    key_city.inline_keyboard.append(row)
                else:
                    row.append(
                        InlineKeyboardButton(text=results[i][0],
                                             callback_data=f'month_delivery_{results[i][0]}_{cura}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='stats_cura_day')
            ])
            await bot.send_message(user_id, "Выберите месяц:", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def delivery_analys_day(call: CallbackQuery, bot: Bot):
    try:
        month = call.data.split('_')[2]
        cura = call.data.split('_')[3]
        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        sql_query = '''
                    SELECT DISTINCT data_day
                    FROM data_shop
                    WHERE external_id = ?;
                '''
        cursor.execute(sql_query, (cura,))

        # Получение результатов запроса
        results = cursor.fetchall()
        conn.close()
        print(results)

        if len(results) == 0:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data=f'ex_cura_{cura}')
                ]

            ])

            await bot.send_message(user_id, "Нет доступных услугу для просмотра.", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            key_city = InlineKeyboardMarkup(inline_keyboard=[])

            for i in range(0, len(results), 2):
                row = []
                # Добавляем две кнопки в строку, если есть два города
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=results[i][0],
                                             callback_data=f'day_delivery_{results[i][0]}_{month}_{cura}'))
                    row.append(
                        InlineKeyboardButton(text=results[i + 1][0],
                                             callback_data=f'day_delivery_{results[i + 1][0]}_{month}_{cura}'))
                # Если остался один город, добавляем его в отдельную кнопку
                else:
                    row.append(
                        InlineKeyboardButton(text=results[i][0],
                                             callback_data=f'day_delivery_{results[i][0]}_{month}_{cura}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data=f'ex_cura_{cura}')
            ])
            await bot.send_message(user_id, f"Выберите день для месяца {month}:", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def delivery_analys_end(call: CallbackQuery, bot: Bot):
    try:
        day = call.data.split('_')[2]
        month = call.data.split('_')[3]
        curas = call.data.split('_')[4]
        user_id = call.message.chat.id

        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
                    SELECT 
                        number_delivery AS number,
                        name_tovar AS item,
                        name_tovar_tho AS item_tho,
                        name_tovar_three AS item_three,
                        name_tovar_four AS item_four,
                        cash_card AS item_type,
                        SUM(CASE WHEN cash_card = 'нал' THEN coll_tovar ELSE 0 END) AS total_quantity_cash,
                        SUM(CASE WHEN cash_card = 'нал' THEN coll_tovar_tho ELSE 0 END) AS total_quantity2_cash,
                        SUM(CASE WHEN cash_card = 'нал' THEN coll_tovar_three ELSE 0 END) AS total_quantity3_cash,
                        SUM(CASE WHEN cash_card = 'нал' THEN coll_tovar_four ELSE 0 END) AS total_quantity4_cash,
                        SUM(CASE WHEN cash_card = 'нал' THEN price_shop ELSE 0 END) AS total_shop_price_cash,
                        SUM(CASE WHEN cash_card = 'нал' THEN price_deliver ELSE 0 END) AS total_delivery_price_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN coll_tovar ELSE 0 END) AS total_quantity_non_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN coll_tovar_tho ELSE 0 END) AS total_quantity2_non_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN coll_tovar_three ELSE 0 END) AS total_quantity3_non_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN coll_tovar_four ELSE 0 END) AS total_quantity4_non_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN price_shop ELSE 0 END) AS total_shop_price_non_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN price_deliver ELSE 0 END) AS total_delivery_price_non_cash
                    FROM 
                        data_shop 
                    WHERE 
                        external_id = ?
                        AND 
                        data_create = ? 
                        AND data_day = ?
                    GROUP BY 
                        number_delivery;
                '''

        cursor.execute(sql_query, (curas, month, day))
        uslugs = cursor.fetchall()
        conn.close()
        print(uslugs)

        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
            SELECT DISTINCT
                COUNT(*)
            FROM 
                data_shop 
            WHERE 
                external_id = ?
                AND data_create = ? 
                AND data_day = ?;
        '''
        cursor.execute(sql_query, (curas, month, day))
        count = cursor.fetchone()[0]
        conn.close()
        summ = 0
        cura = 0
        all_summ = 0
        nall = 0
        beznall = 0
        cura_nall = 0
        tovar = ""
        tovar_tho = ""
        tovar_three = ""
        tovar_four = ""
        name_one = ""
        name_tho = ""
        name_three = ""
        name_four = ""
        cura_beznal = 0
        for item in uslugs:
            nall += item[10]
            beznall += int(item[16])
            summ += int(item[10]) + int(item[16])
            cura_nall += int(item[11])
            cura_beznal += int(item[17])
            cura += int(item[11]) + int(item[17])

            one_tovar = int(item[6]) + int(item[12])
            tho_tovar = int(item[7]) + int(item[13])
            three_tovar = int(item[8]) + int(item[14])
            four_tovar = int(item[9]) + int(item[15])
            name_one = item[1]
            name_tho = item[2]
            name_three = item[3]
            name_four = item[4]
            tovar += f"\n{item[1]} - {one_tovar} г"
            tovar_tho += f"\n{item[2]} - {tho_tovar} г"
            tovar_three += f"\n{item[3]} - {three_tovar} г"
            tovar_four += f"\n{item[4]} - {four_tovar} г"

        all_final_sum = summ + cura
        all_nall = nall + cura_nall
        all_beznall = beznall + cura_beznal
        all_summ += all_final_sum - cura - all_beznall
        finall_shop_summ = all_summ + all_beznall

        key_city = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data='month_delivery_')
            ],
            [
                InlineKeyboardButton(text="Выйти в меню ❌", callback_data='admin_return_')
            ]

        ])
        message_content = (f"Месяц : {month}\n"
                            f"День : {day}\n"
                            f"Количество заказов: {count}\n"
                            f"==================\n"
                            f"Касса :\n"
                            f"Общая : {all_final_sum} zl\n\n"
                            f"Нал :  {all_nall}\n"
                            f"Без-нал : {all_beznall}\n"
                            f"Курьер : {cura} zl\n"
                            f"Кура в кассу : {all_summ} zl\n"
                            f"==================\n"
                            f"Общее количество проданного товара :\n")
        tovar_dict = {}

        for item in uslugs:
            item_names = [item[1], item[2], item[3], item[4]]
            item_quantities = [sum([item[6], item[12]]), sum([item[7], item[13]]), sum([item[8], item[14]]),
                               sum([item[9], item[15]])]

            for item_name, item_quantity in zip(item_names, item_quantities):
                if item_name:
                    if item_name in tovar_dict:
                        tovar_dict[item_name] += item_quantity
                    else:
                        tovar_dict[item_name] = item_quantity

        # Формируем строку для сообщения на основе данных из словаря
        tovar_message = ""
        for item_name, total_quantity in tovar_dict.items():
            tovar_message += f"{item_name} - {total_quantity} г\n"

        # Добавляем эту строку в основное сообщение
        message_content += tovar_message
        await bot.send_message(user_id, message_content, reply_markup=key_city)
        await bot.delete_message(user_id, call.message.message_id)

    except Exception as e:
        print(e)


async def stats_cura_name_week(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        # Выполняем SQL-запрос для выборки столбца external_id
        sql_query = '''
            SELECT DISTINCT external_id
            FROM data_shop
        '''
        cursor.execute(sql_query)
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
                        InlineKeyboardButton(text=results[i][0], callback_data=f'week_cura_{results[i][0]}'))
                    row.append(
                        InlineKeyboardButton(text=results[i + 1][0],
                                             callback_data=f'week_cura_{results[i + 1][0]}'))
                    key_city.inline_keyboard.append(row)
                else:
                    row.append(
                        InlineKeyboardButton(text=results[i][0], callback_data=f'week_cura_{results[i][0]}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ])
            await bot.send_message(user_id, f"Выберите курьера", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)

    except Exception as e:
        print(e)


async def delivery_analys_month_week(call: CallbackQuery, bot: Bot):
    try:
        cura = call.data.split('_')[2]
        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        sql_query = '''
                    SELECT DISTINCT data_create
                    FROM data_shop
                    WHERE external_id = ?;
                '''
        cursor.execute(sql_query, (cura,))

        # Получение результатов запроса
        results = cursor.fetchall()
        conn.close()

        if len(results) == 0:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='stats_cura_week')
                ]

            ])

            await bot.send_message(user_id, "Нет доступных услугу для просмотра.", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            key_city = InlineKeyboardMarkup(inline_keyboard=[])

            for i in range(0, len(results), 2):
                row = []
                # Добавляем две кнопки в строку, если есть два города
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=f"Месяц : {results[i][0]}",
                                             callback_data=f'week_delivery_{results[i][0]}_{cura}'))
                    row.append(
                        InlineKeyboardButton(text=f"Месяц : {results[i + 1][0]}",
                                             callback_data=f'week_delivery_{results[i + 1][0]}_{cura}'))
                # Если остался один город, добавляем его в отдельную кнопку
                else:
                    row.append(
                        InlineKeyboardButton(text=f"Месяц : {results[i][0]}",
                                             callback_data=f'week_delivery_{results[i][0]}_{cura}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='stats_cura_week')
            ])
            await bot.send_message(user_id, "Выберите месяц:", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def get_weeks_in_month(month):
    moth = int(month)
    current_year = datetime.now().year  # Получаем текущий год
    num_days = int(monthrange(current_year, moth)[1])  # Определяем количество дней в месяце
    weeks = []

    start_day = 1
    print(start_day, num_days)
    while start_day <= num_days:
        end_day = min(start_day + 6, num_days)  # Определяем конец недели
        weeks.append((start_day, end_day))
        start_day = end_day + 1  # Переходим к следующей неделе

    return weeks


async def delivery_week(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        month = call.data.split('_')[2]
        cura = call.data.split('_')[3]
        weeks_in_march = await get_weeks_in_month(month=month)
        key_city = InlineKeyboardMarkup(inline_keyboard=[])
        for week_num, (start_day, end_day) in enumerate(weeks_in_march, start=1):
            key_city.inline_keyboard.append([
                InlineKeyboardButton(text=f"Неделя {week_num}: {start_day}-{end_day}",
                                     callback_data=f'week_end_{month}_{start_day}_{end_day}_{cura}')
            ])

        # Добавление кнопки "Назад"
        key_city.inline_keyboard.append([
            InlineKeyboardButton(text="Назад", callback_data=f'week_cura_{cura}')
        ])
        await bot.send_message(user_id, "Выберите неделю:", reply_markup=key_city)
    except Exception as e:
        print(e)


async def delivery_week_end(call: CallbackQuery, bot: Bot):
    try:
        month = call.data.split('_')[2]
        start_day = call.data.split('_')[3]
        end_day = call.data.split('_')[4]
        curas = call.data.split('_')[5]

        print(month, start_day, end_day)
        user_id = call.message.chat.id
        days_range = list(range(int(start_day), int(end_day) + 1))
        days_placeholders = ', '.join(['?' for _ in days_range])
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
                    SELECT 
                        number_delivery AS number,
                        name_tovar AS item,
                        name_tovar_tho AS item_tho,
                        name_tovar_three AS item_three,
                        name_tovar_four AS item_four,
                        cash_card AS item_type,
                        SUM(CASE WHEN cash_card = 'нал' THEN coll_tovar ELSE 0 END) AS total_quantity_cash,
                        SUM(CASE WHEN cash_card = 'нал' THEN coll_tovar_tho ELSE 0 END) AS total_quantity2_cash,
                        SUM(CASE WHEN cash_card = 'нал' THEN coll_tovar_three ELSE 0 END) AS total_quantity3_cash,
                        SUM(CASE WHEN cash_card = 'нал' THEN coll_tovar_four ELSE 0 END) AS total_quantity4_cash,
                        SUM(CASE WHEN cash_card = 'нал' THEN price_shop ELSE 0 END) AS total_shop_price_cash,
                        SUM(CASE WHEN cash_card = 'нал' THEN price_deliver ELSE 0 END) AS total_delivery_price_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN coll_tovar ELSE 0 END) AS total_quantity_non_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN coll_tovar_tho ELSE 0 END) AS total_quantity2_non_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN coll_tovar_three ELSE 0 END) AS total_quantity3_non_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN coll_tovar_four ELSE 0 END) AS total_quantity4_non_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN price_shop ELSE 0 END) AS total_shop_price_non_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN price_deliver ELSE 0 END) AS total_delivery_price_non_cash
                    FROM 
                        data_shop 
                    WHERE 
                        external_id = ? AND 
                        data_create = ? 
                        AND data_day IN ({})
                    GROUP BY 
                        number_delivery;
                '''.format(days_placeholders)

        query_params = (curas,month,) + tuple(days_range)
        cursor.execute(sql_query, query_params)
        uslugs = cursor.fetchall()
        conn.close()
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
            SELECT COUNT(*) 
            FROM data_shop 
            WHERE external_id = ? AND data_create = ? AND data_day IN ({})
        '''.format(days_placeholders)
        query_params = (curas, month) + tuple(days_range)

        cursor.execute(sql_query, query_params)
        num_records = cursor.fetchone()[0]
        conn.close()
        print(num_records)

        # Выводим данные в требуемом формате
        print(f"Месяц: {month}\n")
        print("==================")
        print("Касса:")
        if uslugs is None:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data=f'week_delivery_{month}_{curas}')
                ],
                [
                    InlineKeyboardButton(text="Вёрнуться в меню", callback_data='admin_return_')
                ]
            ])
            await bot.send_message(user_id, "Данные отсутствуют", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            summ = 0
            cura = 0
            all_summ = 0
            nall = 0
            beznall = 0
            cura_nall = 0
            tovar = ""
            tovar_tho = ""
            tovar_three = ""
            tovar_four = ""
            name_one = ""
            name_tho = ""
            name_three = ""
            name_four = ""
            cura_beznal = 0
            for item in uslugs:
                nall += item[10]
                beznall += int(item[16])
                summ += int(item[10]) + int(item[16])
                cura_nall += int(item[11])
                cura_beznal += int(item[17])
                cura += int(item[11]) + int(item[17])

                one_tovar = int(item[6]) + int(item[12])
                tho_tovar = int(item[7]) + int(item[13])
                three_tovar = int(item[8]) + int(item[14])
                four_tovar = int(item[9]) + int(item[15])
                name_one = item[1]
                name_tho = item[2]
                name_three = item[3]
                name_four = item[4]
                tovar += f"\n{item[1]} - {one_tovar} г"
                tovar_tho += f"\n{item[2]} - {tho_tovar} г"
                tovar_three += f"\n{item[3]} - {three_tovar} г"
                tovar_four += f"\n{item[4]} - {four_tovar} г"

            all_final_sum = summ + cura
            all_nall = nall + cura_nall
            all_beznall = beznall + cura_beznal
            all_summ += all_final_sum - cura - all_beznall

            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data=f'week_delivery_{month}_{curas}')
                ],

                [
                    InlineKeyboardButton(text="Выйти в меню ❌", callback_data='admin_return_')
                ]

            ])
            message_content = (f"Месяц : {month}\n"
                               f"Период Дней : {start_day} - {end_day}\n"
                               f"Количество заказов : {num_records}\n"
                               f"==================\n"
                               f"Касса :\n"
                               f"Общая : {all_final_sum} zl\n\n"
                               f"Нал :  {all_nall}\n"
                               f"Без-нал : {all_beznall}\n"
                               f"Курьер : {cura} zl\n"
                               f"Кура в кассу : {all_summ} zl\n"
                               f"==================\n"
                               f"Общее количество проданного товара :\n")
            tovar_dict = {}

            for item in uslugs:
                item_names = [item[1], item[2], item[3], item[4]]
                item_quantities = [sum([item[6], item[12]]), sum([item[7], item[13]]), sum([item[8], item[14]]),
                                   sum([item[9], item[15]])]

                for item_name, item_quantity in zip(item_names, item_quantities):
                    if item_name:
                        if item_name in tovar_dict:
                            tovar_dict[item_name] += item_quantity
                        else:
                            tovar_dict[item_name] = item_quantity

            # Формируем строку для сообщения на основе данных из словаря
            tovar_message = ""
            for item_name, total_quantity in tovar_dict.items():
                tovar_message += f"{item_name} - {total_quantity} г\n"

            # Добавляем эту строку в основное сообщение
            message_content += tovar_message
            await bot.send_message(user_id, message_content
                                   , reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)


    except Exception as e:
        print(e)

async def stats_cura_name_month(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        # Выполняем SQL-запрос для выборки столбца external_id
        sql_query = '''
            SELECT DISTINCT external_id
            FROM data_shop
        '''
        cursor.execute(sql_query)
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
                        InlineKeyboardButton(text=results[i][0], callback_data=f'month_cura_{results[i][0]}'))
                    row.append(
                        InlineKeyboardButton(text=results[i + 1][0],
                                             callback_data=f'month_cura_{results[i + 1][0]}'))
                    key_city.inline_keyboard.append(row)
                else:
                    row.append(
                        InlineKeyboardButton(text=results[i][0], callback_data=f'month_cura_{results[i][0]}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ])
            await bot.send_message(user_id, f"Выберите курьера", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)

    except Exception as e:
        print(e)

async def stats_analys_month(call: CallbackQuery, bot: Bot):
    try:
        cura = call.data.split('_')[2]
        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        sql_query = '''
                    SELECT DISTINCT data_create
                    FROM data_shop
                    WHERE external_id = ?;
                '''
        cursor.execute(sql_query, (cura,))

        # Получение результатов запроса
        results = cursor.fetchall()
        conn.close()

        if len(results) == 0:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='stats_cura_week')
                ]

            ])

            await bot.send_message(user_id, "Нет доступных услугу для просмотра.", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            key_city = InlineKeyboardMarkup(inline_keyboard=[])

            for i in range(0, len(results), 2):
                row = []
                # Добавляем две кнопки в строку, если есть два города
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=f"Месяц : {results[i][0]}",
                                             callback_data=f'ends_delivery_{results[i][0]}_{cura}'))
                    row.append(
                        InlineKeyboardButton(text=f"Месяц : {results[i + 1][0]}",
                                             callback_data=f'ends_delivery_{results[i + 1][0]}_{cura}'))
                # Если остался один город, добавляем его в отдельную кнопку
                else:
                    row.append(
                        InlineKeyboardButton(text=f"Месяц : {results[i][0]}",
                                             callback_data=f'ends_delivery_{results[i][0]}_{cura}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='stats_cura_month')
            ])
            await bot.send_message(user_id, "Выберите месяц:", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def stats_cura_month_end(call: CallbackQuery, bot: Bot):
    try:
        month = call.data.split('_')[2]
        curas = call.data.split('_')[3]
        user_id = call.message.chat.id

        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
                    SELECT 
                        number_delivery AS number,
                        name_tovar AS item,
                        name_tovar_tho AS item_tho,
                        name_tovar_three AS item_three,
                        name_tovar_four AS item_four,
                        cash_card AS item_type,
                        SUM(CASE WHEN cash_card = 'нал' THEN coll_tovar ELSE 0 END) AS total_quantity_cash,
                        SUM(CASE WHEN cash_card = 'нал' THEN coll_tovar_tho ELSE 0 END) AS total_quantity2_cash,
                        SUM(CASE WHEN cash_card = 'нал' THEN coll_tovar_three ELSE 0 END) AS total_quantity3_cash,
                        SUM(CASE WHEN cash_card = 'нал' THEN coll_tovar_four ELSE 0 END) AS total_quantity4_cash,
                        SUM(CASE WHEN cash_card = 'нал' THEN price_shop ELSE 0 END) AS total_shop_price_cash,
                        SUM(CASE WHEN cash_card = 'нал' THEN price_deliver ELSE 0 END) AS total_delivery_price_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN coll_tovar ELSE 0 END) AS total_quantity_non_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN coll_tovar_tho ELSE 0 END) AS total_quantity2_non_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN coll_tovar_three ELSE 0 END) AS total_quantity3_non_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN coll_tovar_four ELSE 0 END) AS total_quantity4_non_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN price_shop ELSE 0 END) AS total_shop_price_non_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN price_deliver ELSE 0 END) AS total_delivery_price_non_cash
                    FROM 
                        data_shop 
                    WHERE 
                        external_id = ? AND
                        data_create = ? 
                    GROUP BY 
                        number_delivery;
                '''
        cursor.execute(sql_query, (curas, month))
        uslugs = cursor.fetchall()
        conn.close()
        print(uslugs)

        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
            SELECT 
                COUNT(*)
            FROM 
                data_shop 
            WHERE 
                external_id = ? 
            AND data_create = ?;

        '''
        cursor.execute(sql_query, (curas, month))
        count = cursor.fetchone()[0]
        conn.close()
        summ = 0
        cura = 0
        all_summ = 0
        nall = 0
        beznall = 0
        cura_nall = 0
        tovar = ""
        tovar_tho = ""
        tovar_three = ""
        tovar_four = ""
        cura_beznal = 0

        for item in uslugs:
            nall += item[10]
            beznall += int(item[16])
            summ += int(item[10]) + int(item[16])
            cura_nall += int(item[11])
            cura_beznal += int(item[17])
            cura += int(item[11]) + int(item[17])

            one_tovar = int(item[6]) + int(item[12])
            tho_tovar = int(item[7]) + int(item[13])
            three_tovar = int(item[8]) + int(item[14])
            four_tovar = int(item[9]) + int(item[15])
            tovar += f"\n{item[1]} - {one_tovar} г"
            tovar_tho += f"\n{item[2]} - {tho_tovar} г"
            tovar_three += f"\n{item[3]} - {three_tovar} г"
            tovar_four += f"\n{item[4]} - {four_tovar} г"

        # Вычисление общей суммы
        all_final_sum = summ + cura
        all_nall = nall + cura_nall
        all_beznall = beznall + cura_beznal
        all_summ += all_final_sum - cura - all_beznall
        finall_shop_summ = all_summ + all_beznall
        message_content = (f"Месяц : {month}\n"
                            f"Количество заказов: {count}\n"
                            f"==================\n"
                            f"Касса :\n"
                            f"Общая : {all_final_sum} zl\n\n"
                            f"Нал :  {all_nall} zl\n"
                            f"Без-нал : {all_beznall} zl\n"
                            f"Курьер : {cura} zl\n"
                            f"Кура в кассу : {all_summ} zl\n"
                            f"==================\n"
                            f"Общее количество проданного товара :\n"
                           )
        tovar_dict = {}

        for item in uslugs:
            item_names = [item[1], item[2], item[3], item[4]]
            item_quantities = [sum([item[6], item[12]]), sum([item[7], item[13]]), sum([item[8], item[14]]),
                               sum([item[9], item[15]])]

            for item_name, item_quantity in zip(item_names, item_quantities):
                if item_name:
                    if item_name in tovar_dict:
                        tovar_dict[item_name] += item_quantity
                    else:
                        tovar_dict[item_name] = item_quantity

        tovar_message = ""
        for item_name, total_quantity in tovar_dict.items():
            tovar_message += f"{item_name} - {total_quantity} г\n"
        message_content += tovar_message

        key_city = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'stats_shop_month')

            ],
            [
                InlineKeyboardButton(text="Выйти в меню ❌", callback_data='admin_return_')
            ]

        ])
        await bot.send_message(user_id, message_content, reply_markup=key_city)
        await bot.delete_message(user_id, call.message.message_id)

    except Exception as e:
        print(e)