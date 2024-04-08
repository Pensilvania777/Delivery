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

async def stats_admin_oper(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        key_city = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="За день", callback_data='stats_oper_day'),
            ],
            [
                InlineKeyboardButton(text="За неделю", callback_data='stats_oper_week')
            ],
            [
                InlineKeyboardButton(text="За месяц", callback_data='stats_oper_month')
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data='admin_stats')
            ]

        ])
        await bot.send_message(user_id, "Статистика Опера:", reply_markup=key_city)
        await bot.delete_message(user_id, call.message.message_id)
    except:
        pass


async def stats_oper_day_month(call: CallbackQuery, bot: Bot):
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
                    InlineKeyboardButton(text="Назад", callback_data='stats_oper_menu')
                ]

            ])

            await bot.send_message(user_id, "Нет статистики !", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            key_city = InlineKeyboardMarkup(inline_keyboard=[])

            for i in range(0, len(results), 2):
                row = []
                # Добавляем две кнопки в строку, если есть два города
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=results[i][0], callback_data=f'month_oper_{results[i][0]}'))
                    row.append(
                        InlineKeyboardButton(text=results[i + 1][0],
                                             callback_data=f'month_oper_{results[i + 1][0]}'))
                    key_city.inline_keyboard.append(row)
                else:
                    row.append(
                        InlineKeyboardButton(text=results[i][0], callback_data=f'month_oper_{results[i][0]}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='stats_oper_menu')
            ])
            await bot.send_message(user_id, "Выберите месяц:", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def stats_oper_day_day(call: CallbackQuery, bot: Bot):
    try:
        month = call.data.split('_')[2]

        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        sql_query = '''
                    SELECT DISTINCT data_day
                    FROM data_shop
                    WHERE data_create = ?;
                '''
        cursor.execute(sql_query, (month,))
        results = cursor.fetchall()
        conn.close()
        print(results)

        if len(results) == 0:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='stats_oper_day')
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
                                             callback_data=f'day_oper_{results[i][0]}_{month}'))
                    row.append(
                        InlineKeyboardButton(text=results[i + 1][0],
                                             callback_data=f'day_oper_{results[i + 1][0]}_{month}'))
                # Если остался один город, добавляем его в отдельную кнопку
                else:
                    row.append(
                        InlineKeyboardButton(text=results[i][0],
                                             callback_data=f'day_oper_{results[i][0]}_{month}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='stats_oper_day')
            ])
            await bot.send_message(user_id, f"Выберите день для месяца {month} :", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def stats_oper_day_end(call: CallbackQuery, bot: Bot):
    try:
        day = call.data.split('_')[2]
        month = call.data.split('_')[3]
        print(day)
        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
            SELECT 
                COUNT(*)
            FROM 
                data_shop 
            WHERE 
                data_create = ? 
                AND data_day = ?;
        '''
        cursor.execute(sql_query, (month, day))
        count = cursor.fetchone()[0]
        conn.close()

        key_city = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'month_oper_{month}')

            ],
            [
                InlineKeyboardButton(text="Выйти в меню ❌", callback_data='admin_return_')
            ]

        ])
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
                        data_create = ? 
                        AND data_day = ?
                    GROUP BY 
                        number_delivery;
                '''

        cursor.execute(sql_query, (month, day))
        uslugs = cursor.fetchall()
        conn.close()
        beznall = 0
        for item in uslugs:
            beznall += int(item[16])

        summ = int(count) * 5
        await bot.send_message(user_id, f"Месяц : {month}\n"
                                        f"День : {day}\n"
                                        f"Количество заказов: {count}\n"
                                        f"Безнал: {beznall}\n"
                                        f"==================\n"
                                        f"Касса опера: {summ} zl \n"
                                        f"==================\n"
                               , reply_markup=key_city)
        await bot.delete_message(user_id, call.message.message_id)

    except Exception as e:
        print(e)


async def stats_oper_week_month(call: CallbackQuery, bot: Bot):
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
                    InlineKeyboardButton(text="Назад", callback_data='stats_oper_menu')
                ]

            ])

            await bot.send_message(user_id, "Нет статистики !", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            key_city = InlineKeyboardMarkup(inline_keyboard=[])

            for i in range(0, len(results), 2):
                row = []
                # Добавляем две кнопки в строку, если есть два города
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=results[i][0], callback_data=f'oper_week_{results[i][0]}'))
                    row.append(
                        InlineKeyboardButton(text=results[i + 1][0],
                                             callback_data=f'oper_week_{results[i + 1][0]}'))
                    key_city.inline_keyboard.append(row)
                else:
                    row.append(
                        InlineKeyboardButton(text=results[i][0], callback_data=f'oper_week_{results[i][0]}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='stats_shop_menu')
            ])
            await bot.send_message(user_id, "Выберите месяц:", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def stats_oper_weeks_in_month(month):
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


async def stats_oper_delivery_week(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        month = call.data.split('_')[2]
        weeks_in_march = await stats_oper_weeks_in_month(month=month)
        key_city = InlineKeyboardMarkup(inline_keyboard=[])
        for week_num, (start_day, end_day) in enumerate(weeks_in_march, start=1):
            key_city.inline_keyboard.append([
                InlineKeyboardButton(text=f"Неделя {week_num}: {start_day}-{end_day}",
                                     callback_data=f'statsoper_end_{month}_{start_day}_{end_day}')
            ])
        key_city.inline_keyboard.append([
            InlineKeyboardButton(text="Назад", callback_data='stats_oper_week')
        ])
        await bot.send_message(user_id, "Выберите неделю:", reply_markup=key_city)
        await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def stats_oper_week_end(call: CallbackQuery, bot: Bot):
    try:
        month = call.data.split('_')[2]
        start_day = call.data.split('_')[3]
        end_day = call.data.split('_')[4]
        print(month, start_day, end_day)
        user_id = call.message.chat.id
        days_range = list(range(int(start_day), int(end_day) + 1))
        days_placeholders = ', '.join(['?' for _ in days_range])

        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
            SELECT COUNT(*) 
            FROM data_shop 
            WHERE data_create = ? AND data_day IN ({})
        '''.format(days_placeholders)
        query_params = (month,) + tuple(days_range)

        cursor.execute(sql_query, query_params)
        num_records = cursor.fetchone()[0]
        conn.close()
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
                        data_create = ? 
                        AND data_day IN ({})
                    GROUP BY 
                        number_delivery;
                '''.format(days_placeholders)
        query_params = (month,) + tuple(days_range)
        cursor.execute(sql_query, query_params)
        uslugs = cursor.fetchall()
        conn.close()
        beznall = 0
        for item in uslugs:
            beznall += int(item[16])

        key_city = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'oper_week_{month}')
            ],
            [
                InlineKeyboardButton(text="Выйти в меню ❌", callback_data='admin_return_')
            ]

        ])
        summ = int(num_records) * 5
        await bot.send_message(user_id, f"Месяц : {month}\n"
                                        f"Период Дней : {start_day} - {end_day}\n"
                                        f"Количество заказов : {num_records}\n"
                                        f"Количество кладов : {beznall}\n"
                                        f"==================\n"
                                        f"Касса опера : {summ} zl\n"
                                        f"==================\n"
                               , reply_markup=key_city)
        await bot.delete_message(user_id, call.message.message_id)


    except Exception as e:
        print(e)


async def stats_oper_month_month(call: CallbackQuery, bot: Bot):
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
                    InlineKeyboardButton(text="Назад", callback_data='stats_oper_menu')
                ]

            ])

            await bot.send_message(user_id, "Нет статистики !", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            key_city = InlineKeyboardMarkup(inline_keyboard=[])

            for i in range(0, len(results), 2):
                row = []
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=results[i][0], callback_data=f'oper_month_{results[i][0]}'))
                    row.append(
                        InlineKeyboardButton(text=results[i + 1][0],
                                             callback_data=f'oper_month_{results[i + 1][0]}'))
                    key_city.inline_keyboard.append(row)
                else:
                    row.append(
                        InlineKeyboardButton(text=results[i][0], callback_data=f'oper_month_{results[i][0]}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='stats_oper_menu')
            ])
            await bot.send_message(user_id, "Выберите месяц:", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def stats_oper_month_end(call: CallbackQuery, bot: Bot):
    try:
        month = call.data.split('_')[2]
        user_id = call.message.chat.id

        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
            SELECT 
                COUNT(*)
            FROM 
                data_shop 
            WHERE 
                data_create = ?;

        '''
        cursor.execute(sql_query, (month,))
        count = cursor.fetchone()[0]
        conn.close()

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
                        SUM(CASE WHEN cash_card = 'нал' THEN coll_tovar ELSE 0 END) AS total_quantity0_cash,
                        SUM(CASE WHEN cash_card = 'нал' THEN coll_tovar_tho ELSE 0 END) AS total_quantity234_cash,
                        SUM(CASE WHEN cash_card = 'нал' THEN coll_tovar_three ELSE 0 END) AS total_quantity14_cash,
                        SUM(CASE WHEN cash_card = 'нал' THEN coll_tovar_four ELSE 0 END) AS total_quantity100_cash,
                        SUM(CASE WHEN cash_card = 'нал' THEN price_shop ELSE 0 END) AS total_shop_price99_cash,
                        SUM(CASE WHEN cash_card = 'нал' THEN price_deliver ELSE 0 END) AS total_delivery23_price8_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN coll_tovar ELSE 0 END) AS total_quantity1_non6_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN coll_tovar_tho ELSE 0 END) AS total_quantity51_non_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN coll_tovar_three ELSE 0 END) AS total_quantity52_non_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN coll_tovar_four ELSE 0 END) AS total_quantity63_non_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN price_shop ELSE 0 END) AS total_shop_price55_non_cash,
                        SUM(CASE WHEN cash_card = 'карта' THEN price_deliver ELSE 0 END) AS total_delivery66_price6_non_cash
                    FROM 
                        data_shop 
                    WHERE 
                        data_create = ? 
                    AND 
                        external_id = ?
                    GROUP BY 
                        number_delivery;

                '''
        cursor.execute(sql_query, (month, user_id))
        uslugs = cursor.fetchall()
        conn.close()
        beznall = 0
        for item in uslugs:
            beznall += int(item[16])
        key_city = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'stats_oper_month')

            ],
            [
                InlineKeyboardButton(text="Выйти в меню ❌", callback_data='admin_return')
            ]

        ])
        summ = int(count) * 5
        await bot.send_message(user_id, f"Месяц : {month}\n"
                                        f"Количество заказов: {count}\n"
                                        f"Количество кладов : {beznall}\n"
                                        f"==================\n"
                                        f"Касса опера : {summ} zl\n"
                                        f"==================\n"
                               , reply_markup=key_city)
        await bot.delete_message(user_id, call.message.message_id)

    except Exception as e:
        print(e)



