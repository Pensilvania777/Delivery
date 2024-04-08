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
from utils.state import Edit_deliver


async def edit_month_center(call: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        month = call.data.split('_')[3]
        number_delivery = call.data.split('_')[4]
        day = call.data.split('_')[5]
        id = call.data.split('_')[6]
        await state.update_data(id=id)
        await state.update_data(day=day)
        await state.update_data(number=number_delivery)

        user_id = call.message.chat.id
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'edit_edit_end_{number_delivery}_{month}_{day}')
            ]
        ])
        await bot.send_message(user_id, f"Старый месяц {month}\n"
                                        f"Введите новый:", reply_markup=key_admin)
        await state.set_state(Edit_deliver.month)

        await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def edit_month_end(message: Message, bot: Bot, state: FSMContext):
    try:
        month = message.text
        context_data = await state.get_data()
        id = context_data.get('id')
        day = context_data.get('day')
        number = context_data.get('number')
        await bot.delete_message(message.chat.id, message.message_id - 1)
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
            UPDATE data_shop
            SET data_create = ?
            WHERE id = ?
        '''
        cursor.execute(sql_query, (month, id))
        conn.commit()
        conn.close()
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'edit_edit_end_{number}_{month}_{day}')
            ],
            [
                InlineKeyboardButton(text="Выйти в меню", callback_data='admin_return_')
            ]
        ])
        await bot.send_message(message.chat.id, f"Новый месяц {month}", reply_markup=key_admin)
        await bot.delete_message(message.chat.id, message.message_id)

    except Exception as e:
        print(e)


async def edit_day_center(call: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        month = call.data.split('_')[3]
        number_delivery = call.data.split('_')[4]
        day = call.data.split('_')[5]
        id = call.data.split('_')[6]
        await state.update_data(id=id)
        await state.update_data(month=month)
        await state.update_data(number=number_delivery)
        user_id = call.message.chat.id
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'edit_edit_end_{number_delivery}_{month}_{day}')
            ]
        ])
        await bot.send_message(user_id, f"Старый день {day}\n"
                                        f"Введите новый:", reply_markup=key_admin)
        await state.set_state(Edit_deliver.day)

        await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def edit_day_end(message: Message, bot: Bot, state: FSMContext):
    try:
        day = message.text
        context_data = await state.get_data()
        id = context_data.get('id')
        month = context_data.get('month')
        number = context_data.get('number')
        await bot.delete_message(message.chat.id, message.message_id - 1)
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
            UPDATE data_shop
            SET data_day = ?
            WHERE id = ?
        '''
        cursor.execute(sql_query, (day, id))
        conn.commit()
        conn.close()
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'edit_edit_end_{number}_{month}_{day}')
            ],
            [
                InlineKeyboardButton(text="Выйти в меню", callback_data='admin_return_')
            ]
        ])
        await bot.send_message(message.chat.id, f"Новый день {day}", reply_markup=key_admin)
        await bot.delete_message(message.chat.id, message.message_id)

    except Exception as e:
        print(e)


async def edit_number_center(call: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        month = call.data.split('_')[3]
        number_delivery = call.data.split('_')[4]
        day = call.data.split('_')[5]
        id = call.data.split('_')[6]
        await state.update_data(id=id)
        await state.update_data(month=month)
        await state.update_data(day=day)
        user_id = call.message.chat.id
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'edit_edit_end_{number_delivery}_{month}_{day}')
            ]
        ])
        await bot.send_message(user_id, f"Старый номер заказ {number_delivery}\n"
                                        f"Введите новый:", reply_markup=key_admin)
        await state.set_state(Edit_deliver.number_delivery)

        await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def edit_number_end(message: Message, bot: Bot, state: FSMContext):
    try:
        number = message.text
        context_data = await state.get_data()
        id = context_data.get('id')
        month = context_data.get('month')
        day = context_data.get('day')
        await bot.delete_message(message.chat.id, message.message_id - 1)
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
            UPDATE data_shop
            SET number_delivery = ?
            WHERE id = ?
        '''
        cursor.execute(sql_query, (number, id))
        conn.commit()
        conn.close()
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'edit_edit_end_{number}_{month}_{day}')
            ],
            [
                InlineKeyboardButton(text="Выйти в меню", callback_data='admin_return_')
            ]
        ])
        await bot.send_message(message.chat.id, f"Новый номер {number}", reply_markup=key_admin)
        await bot.delete_message(message.chat.id, message.message_id)

    except Exception as e:
        print(e)


async def edit_address_center(call: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        address = call.data.split('_')[3]
        number_delivery = call.data.split('_')[4]
        month = call.data.split('_')[5]
        day = call.data.split('_')[6]
        id = call.data.split('_')[7]
        await state.update_data(id=id)
        await state.update_data(month=month)
        await state.update_data(day=day)
        await state.update_data(number=number_delivery)
        user_id = call.message.chat.id
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'edit_edit_end_{number_delivery}_{month}_{day}')
            ]
        ])
        await bot.send_message(user_id, f"Старый адрес заказа {address}\n"
                                        f"Введите новый:", reply_markup=key_admin)
        await state.set_state(Edit_deliver.adress_delivery)

        await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def edit_address_end(message: Message, bot: Bot, state: FSMContext):
    try:
        address = message.text
        context_data = await state.get_data()
        id = context_data.get('id')
        month = context_data.get('month')
        day = context_data.get('day')
        number = context_data.get('number')
        await bot.delete_message(message.chat.id, message.message_id - 1)
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
            UPDATE data_shop
            SET adress_delivery = ?
            WHERE id = ?
        '''
        cursor.execute(sql_query, (address, id))
        conn.commit()
        conn.close()
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'edit_edit_end_{number}_{month}_{day}')
            ],
            [
                InlineKeyboardButton(text="Выйти в меню", callback_data='admin_return_')
            ]
        ])
        await bot.send_message(message.chat.id, f"Новый адрес {address}", reply_markup=key_admin)
        await bot.delete_message(message.chat.id, message.message_id)

    except Exception as e:
        print(e)


async def edit_coll_tovar_center(call: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        coll_tovar = call.data.split('_')[4]
        number_delivery = call.data.split('_')[5]
        month = call.data.split('_')[6]
        day = call.data.split('_')[7]
        id = call.data.split('_')[8]
        await state.update_data(id=id)
        await state.update_data(month=month)
        await state.update_data(day=day)
        await state.update_data(number=number_delivery)
        user_id = call.message.chat.id
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'edit_edit_end_{number_delivery}_{month}_{day}')
            ]
        ])
        await bot.send_message(user_id, f"Старое Количество товара {coll_tovar}\n"
                                        f"Введите новое:", reply_markup=key_admin)
        await state.set_state(Edit_deliver.coll_tovar)

        await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def edit_coll_tovar_end(message: Message, bot: Bot, state: FSMContext):
    try:
        coll_tovar = message.text
        context_data = await state.get_data()
        id = context_data.get('id')
        month = context_data.get('month')
        day = context_data.get('day')
        number = context_data.get('number')
        await bot.delete_message(message.chat.id, message.message_id - 1)
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
            UPDATE data_shop
            SET coll_tovar = ?
            WHERE id = ?
        '''
        cursor.execute(sql_query, (coll_tovar, id))
        conn.commit()
        conn.close()
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'edit_edit_end_{number}_{month}_{day}')
            ],
            [
                InlineKeyboardButton(text="Выйти в меню", callback_data='admin_return_')
            ]
        ])
        await bot.send_message(message.chat.id, f"Новое кол-во товара {coll_tovar}", reply_markup=key_admin)
        await bot.delete_message(message.chat.id, message.message_id)

    except Exception as e:
        print(e)


async def edit_name_tovar_center(call: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        name_tovar = call.data.split('_')[4]
        number_delivery = call.data.split('_')[5]
        month = call.data.split('_')[6]
        day = call.data.split('_')[7]
        id = call.data.split('_')[8]
        await state.update_data(id=id)
        await state.update_data(month=month)
        await state.update_data(day=day)
        await state.update_data(number=number_delivery)
        user_id = call.message.chat.id
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'edit_edit_end_{number_delivery}_{month}_{day}')
            ]
        ])
        await bot.send_message(user_id, f"Старая имя товара {name_tovar}\n"
                                        f"Введите новое:", reply_markup=key_admin)
        await state.set_state(Edit_deliver.name_tovar)

        await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def edit_name_tovar_end(message: Message, bot: Bot, state: FSMContext):
    try:
        name_tovar = message.text
        context_data = await state.get_data()
        id = context_data.get('id')
        month = context_data.get('month')
        day = context_data.get('day')
        number = context_data.get('number')
        await bot.delete_message(message.chat.id, message.message_id - 1)
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
            UPDATE data_shop
            SET name_tovar = ?
            WHERE id = ?
        '''
        cursor.execute(sql_query, (name_tovar, id))
        conn.commit()
        conn.close()
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'edit_edit_end_{number}_{month}_{day}')
            ],
            [
                InlineKeyboardButton(text="Выйти в меню", callback_data='admin_return_')
            ]
        ])
        await bot.send_message(message.chat.id, f"Новое имя товара {name_tovar}", reply_markup=key_admin)
        await bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        print(e)


async def edit_price_shop_center(call: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        price_shop = call.data.split('_')[4]
        number_delivery = call.data.split('_')[5]
        month = call.data.split('_')[6]
        day = call.data.split('_')[7]
        id = call.data.split('_')[8]
        await state.update_data(id=id)
        await state.update_data(month=month)
        await state.update_data(day=day)
        await state.update_data(number=number_delivery)
        user_id = call.message.chat.id
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'edit_edit_end_{number_delivery}_{month}_{day}')
            ]
        ])
        await bot.send_message(user_id, f"Старая Цена заказа {price_shop}\n"
                                        f"Введите новую:", reply_markup=key_admin)
        await state.set_state(Edit_deliver.price_shop)

        await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def edit_price_shop_end(message: Message, bot: Bot, state: FSMContext):
    try:
        price_shop = message.text
        context_data = await state.get_data()
        id = context_data.get('id')
        month = context_data.get('month')
        day = context_data.get('day')
        number = context_data.get('number')
        await bot.delete_message(message.chat.id, message.message_id - 1)
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
            UPDATE data_shop
            SET price_shop = ?
            WHERE id = ?
        '''
        cursor.execute(sql_query, (price_shop, id))
        conn.commit()
        conn.close()
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'edit_edit_end_{number}_{month}_{day}')
            ],
            [
                InlineKeyboardButton(text="Выйти в меню", callback_data='admin_return_')
            ]
        ])
        await bot.send_message(message.chat.id, f"Новая Цена заказа {price_shop}", reply_markup=key_admin)
        await bot.delete_message(message.chat.id, message.message_id)

    except Exception as e:
        print(e)


async def edit_price_deliver_center(call: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        price_deliver = call.data.split('_')[4]
        number_delivery = call.data.split('_')[5]
        month = call.data.split('_')[6]
        day = call.data.split('_')[7]
        id = call.data.split('_')[8]
        await state.update_data(id=id)
        await state.update_data(month=month)
        await state.update_data(day=day)
        await state.update_data(number=number_delivery)
        user_id = call.message.chat.id
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'edit_edit_end_{number_delivery}_{month}_{day}')
            ]
        ])
        await bot.send_message(user_id, f"Старая Цена доставки {price_deliver}\n"
                                        f"Введите новое:", reply_markup=key_admin)
        await state.set_state(Edit_deliver.price_deliver)

        await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def edit_price_deliver_end(message: Message, bot: Bot, state: FSMContext):
    try:
        price_deliver = message.text
        context_data = await state.get_data()
        id = context_data.get('id')
        month = context_data.get('month')
        day = context_data.get('day')
        number = context_data.get('number')
        await bot.delete_message(message.chat.id, message.message_id - 1)
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
            UPDATE data_shop
            SET price_deliver = ?
            WHERE id = ?
        '''
        cursor.execute(sql_query, (price_deliver, id))
        conn.commit()
        conn.close()
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'edit_edit_end_{number}_{month}_{day}')
            ],
            [
                InlineKeyboardButton(text="Выйти в меню", callback_data='admin_return_')
            ]
        ])
        await bot.send_message(message.chat.id, f"Новая Цена доставки  {price_deliver}", reply_markup=key_admin)
        await bot.delete_message(message.chat.id, message.message_id)

    except Exception as e:
        print(e)


async def edit_cash_card_center(call: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        cash_card = call.data.split('_')[4]
        number_delivery = call.data.split('_')[5]
        month = call.data.split('_')[6]
        day = call.data.split('_')[7]
        id = call.data.split('_')[8]
        await state.update_data(id=id)
        await state.update_data(month=month)
        await state.update_data(day=day)
        await state.update_data(number=number_delivery)
        user_id = call.message.chat.id
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'edit_edit_end_{number_delivery}_{month}_{day}')
            ]
        ])
        await bot.send_message(user_id, f"Старый способ оплаты {cash_card}\n"
                                        f"Введите новый:", reply_markup=key_admin)
        await state.set_state(Edit_deliver.cash_card)

        await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def edit_cash_card_end(message: Message, bot: Bot, state: FSMContext):
    try:
        cash_card = message.text
        context_data = await state.get_data()
        id = context_data.get('id')
        month = context_data.get('month')
        day = context_data.get('day')
        number = context_data.get('number')
        await bot.delete_message(message.chat.id, message.message_id - 1)
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
            UPDATE data_shop
            SET cash_card = ?
            WHERE id = ?
        '''
        cursor.execute(sql_query, (cash_card, id))
        conn.commit()
        conn.close()
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'edit_edit_end_{number}_{month}_{day}')
            ],
            [
                InlineKeyboardButton(text="Выйти в меню", callback_data='admin_return_')
            ]
        ])
        await bot.send_message(message.chat.id, f"Новый способ оплаты {cash_card}", reply_markup=key_admin)
        await bot.delete_message(message.chat.id, message.message_id)

    except Exception as e:
        print(e)


async def edit_cura_set(call: CallbackQuery, bot: Bot):
    try:
        name_cura = call.data.split('_')[4]
        number_delivery = call.data.split('_')[5]
        month = call.data.split('_')[6]
        day = call.data.split('_')[7]
        id = call.data.split('_')[8]
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name_admin FROM cura")
        admin_names = cursor.fetchall()
        conn.close()

        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=admin_name[0], callback_data=f'edit_cura_end_{admin_name[0]}_{number_delivery}_{month}_{day}_{id}') for admin_name in
                admin_names
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ]

        ])

        await bot.send_message(call.message.chat.id, f"Старый курьер {name_cura}\n"
                                                     "Выберите нового Курьера:", reply_markup=key_admin)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        print(e)


async def edit_name_cura_end(call: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        name_cura = call.data.split('_')[3]
        number_delivery = call.data.split('_')[4]
        month = call.data.split('_')[5]
        day = call.data.split('_')[6]
        id = call.data.split('_')[7]
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        # Выполняем SQL-запрос для выборки столбца external_admin по значению name_admin
        sql_query = '''
            SELECT external_admin
            FROM cura
            WHERE name_admin = ?
        '''
        cursor.execute(sql_query, (name_cura,))
        results = cursor.fetchall()
        conn.close()
        id_cura = results[0][0]

        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        sql_query = '''
            UPDATE data_shop
            SET external_id = ?
            WHERE id = ?
        '''
        cursor.execute(sql_query, (id_cura, id))
        conn.commit()
        conn.close()
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data=f'edit_edit_end_{number_delivery}_{month}_{day}')
            ],
            [
                InlineKeyboardButton(text="Выйти в меню", callback_data='admin_return_')
            ]
        ])
        await bot.send_message(call.message.chat.id, f"Новый курьер {name_cura}", reply_markup=key_admin)
        await bot.delete_message(call.message.chat.id, call.message.message_id)

    except Exception as e:
        print(e)
