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
from datetime import datetime, timedelta
from calendar import monthrange

from aiogram import F


async def delivery_analys_menu(call: CallbackQuery, bot: Bot):
    try:
        key_city = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="По дню", callback_data='delivery_analys_day')
            ],
            [
                InlineKeyboardButton(text="По неделе", callback_data='delivery_analys_week')
            ]
        ])
        await bot.send_message(call.message.chat.id, "Выберите промежуток:", reply_markup=key_city)
        await bot.delete_message(call.message.chat.id, call.message.message_id)

    except:
        pass

