import asyncio
import logging
import sys
import sqlite3
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import (Message,
                           InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery)
from config.config import TOKEN
import re
from aiogram import F


async def menu_delivery(message: Message, bot: Bot):
    try:
        user_id = message.chat.id

        user_external_id = message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        # Выполняем SQL-запрос для проверки наличия пользователя с заданным external_id в таблице админов
        cursor.execute('SELECT external_admin FROM cura WHERE external_admin = ?', (user_external_id,))
        admin = cursor.fetchone()

        # Закрываем соединение с базой данных
        conn.close()

        if admin is not None:
            admin_str = admin[0]

            # Используем регулярное выражение для удаления всех символов, кроме цифр
            digits_only = re.sub(r'\D', '', admin_str)

            # Преобразуем user_external_id в строку, чтобы сравнить с digits_only
            user_external_id_str = str(user_external_id)

            if digits_only == user_external_id_str:
                conn = sqlite3.connect('shop.db')
                cursor = conn.cursor()
                sql_query = '''
                                    SELECT * FROM cura_tovar WHERE external_cura = ?
                                '''
                cursor.execute(sql_query, (user_external_id_str,))
                rows = cursor.fetchall()
                conn.close()
                items_and_quantities = []
                for row in rows:
                    item_and_quantity = f"{row[2]} - {row[3]}"
                    items_and_quantities.append(item_and_quantity)

                # Теперь объединим все строки в одну, разделив их переносом строки
                item_coll_string = "\n".join(items_and_quantities)
                user_id = message.chat.id
                key_city = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="Доставка запись", callback_data='dev_add')
                    ]

                ])

                await bot.send_message(user_id, "Приветствую в боте Доставок.\n"
                                                "Товар в наличии:\n"
                                                f"{item_coll_string}\n", reply_markup=key_city)
                await bot.delete_message(user_id, message.message_id)
            else:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="Вернуться в меню", callback_data='menu_return_')
                    ]
                ])
                await bot.send_message(message.chat.id, "У вас нет доступа этой функции!",
                                       reply_markup=keyboard)
                await bot.delete_message(message.chat.id, message.message_id)
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Вернуться в меню", callback_data='menu_return_')
                ]
            ])
            await bot.send_message(message.chat.id, "У вас нет доступа этой функции!", reply_markup=keyboard)
            await bot.delete_message(message.chat.id, message.message_id)

    except Exception as e:
        print(e)


async def menu_delivery_return(call: CallbackQuery, bot: Bot):
    try:
        user_external_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        # Выполняем SQL-запрос для проверки наличия пользователя с заданным external_id в таблице админов
        cursor.execute('SELECT external_admin FROM cura WHERE external_admin = ?', (user_external_id,))
        admin = cursor.fetchone()

        # Закрываем соединение с базой данных
        conn.close()

        if admin is not None:
            admin_str = admin[0]

            # Используем регулярное выражение для удаления всех символов, кроме цифр
            digits_only = re.sub(r'\D', '', admin_str)

            # Преобразуем user_external_id в строку, чтобы сравнить с digits_only
            user_external_id_str = str(user_external_id)

            if digits_only == user_external_id_str:
                conn = sqlite3.connect('shop.db')
                cursor = conn.cursor()
                sql_query = '''
                                                    SELECT * FROM cura_tovar WHERE external_cura = ?
                                                '''
                cursor.execute(sql_query, (user_external_id_str,))
                rows = cursor.fetchall()
                conn.close()
                items_and_quantities = []
                for row in rows:
                    item_and_quantity = f"{row[2]} - {row[3]}"
                    items_and_quantities.append(item_and_quantity)

                # Теперь объединим все строки в одну, разделив их переносом строки
                item_coll_string = "\n".join(items_and_quantities)

                user_id = call.message.chat.id
                key_city = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="Доставка запись", callback_data='dev_add')
                    ]
                ])

                await bot.send_message(user_id, "Приветствую в боте Доставок.\n"
                                                "Товар в наличии:\n"
                                                f"{item_coll_string}\n", reply_markup=key_city)
                await bot.delete_message(user_id, call.message.message_id)
            else:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="Вернуться в меню", callback_data='menu_return_')
                    ]
                ])
                await bot.send_message(call.message.chat.id, "У вас нет доступа этой функции!",
                                       reply_markup=keyboard)
                await bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Вернуться в меню", callback_data='menu_return_')
                ]
            ])
            await bot.send_message(call.message.chat.id, "У вас нет доступа этой функции!", reply_markup=keyboard)
            await bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        print(e)