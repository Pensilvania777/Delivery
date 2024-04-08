import sqlite3
import time
import datetime
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import (Message,
                           InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery)


async def check_and_send_messages(bot: Bot):
    try:
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute("SELECT external_cura, name_item, coll_tovar FROM cura_tovar WHERE coll_tovar <= 5")
        gays = cursor.fetchall()
        conn.close()
        external_cura = ""
        for row in gays:
            external_cura = row[0]
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        # Выбираем данные из таблицы по значению external_admin
        cursor.execute('''SELECT name_admin FROM cura WHERE external_admin = ?''', (external_cura,))
        rows = cursor.fetchall()
        name_cura = ""
        for row in rows:
            name_cura = row[0]

        conn.close()
        key_city = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Удалить", callback_data=f'delete_message_')
            ],
        ])

        key = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Удалить", callback_data=f'delete_users_')
            ],
        ])
        for row in gays:
            external_cura, name_item, coll_tovar = row
            message = f"У вас заканчивается товар {name_item}. Осталось всего {coll_tovar} шт."
            await bot.send_message(external_cura, message, reply_markup=key)
            message_tho = f"У курьера {name_cura}  заканчивается товар {name_item}. Осталось всего {coll_tovar} шт."
            await bot.send_message(-4198917823, message_tho, reply_markup=key_city)
    except:
        pass

async def delete_users(bot: Bot, message: Message):
    try:
        user_id = message.chat.id
        await bot.delete_message(user_id, message.message_id)
    except:
        pass


async def delete_message(bot: Bot):
    try:
        await bot.delete_message(-4198917823, 1)
    except:
        pass

