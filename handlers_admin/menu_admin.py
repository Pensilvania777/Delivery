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

from aiogram import F


async def admin_menu(message: Message, bot: Bot):
    try:
        user_id = message.chat.id
        key_city = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Админ", callback_data='admin_set_'),
                InlineKeyboardButton(text="Курьер", callback_data='cura_set_')
            ],
            [
                InlineKeyboardButton(text="Товар", callback_data='tovar_set'),
                InlineKeyboardButton(text="Доставки", callback_data='delivery_set')
            ],
            [
                InlineKeyboardButton(text="Статистика", callback_data='admin_stats')
            ],
            [
                InlineKeyboardButton(text="Выйти в меню", callback_data='menu_return_')
            ]
        ])

        await bot.send_message(user_id, "Приветствую в боте Доставок.", reply_markup=key_city)
        await bot.delete_message(user_id, message.message_id)

    except:
        pass


async def admin_menu_return(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        key_city = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Админ", callback_data='admin_set_'),
                InlineKeyboardButton(text="Курьер", callback_data='cura_set_')
            ],
            [
                InlineKeyboardButton(text="Товар", callback_data='tovar_set'),
                InlineKeyboardButton(text="Доставки", callback_data='delivery_set')
            ],
            [
                InlineKeyboardButton(text="Статистика", callback_data='admin_stats')
            ],
            [
                InlineKeyboardButton(text="Выйти в меню", callback_data='menu_return_')
            ]

        ])

        await bot.send_message(user_id, "Приветствую в боте Доставок.", reply_markup=key_city)
        await bot.delete_message(user_id, call.message.message_id)
    except:
        pass