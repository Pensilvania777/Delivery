from aiogram import Bot
from aiogram.types import (Message,
                           InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery)
import sqlite3
import re
from utils.state import Cura_add
import logging
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta


async def cura_set_menu(call: CallbackQuery, bot: Bot):
    try:
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Добавить курьера", callback_data='add_cura_set_'),
                InlineKeyboardButton(text="Удалить курьера", callback_data='del_cura_set_')
            ],
            [
                InlineKeyboardButton(text="Просмотр курьеров", callback_data='show_cura_set_'),
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ]
        ])
        await bot.send_message(call.message.chat.id, "Выберите действие.", reply_markup=key_admin)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        print(e)



async def cura_show_set(call: CallbackQuery, bot: Bot):
    try:
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        # Выполняем SQL-запрос для получения всех админов
        cursor.execute('SELECT id, name_admin, external_admin FROM cura')
        admins = cursor.fetchall()

        # Закрываем соединение с базой данных
        conn.close()
        key_city = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Выйти в меню", callback_data='admin_return_')
            ]
        ])
        if admins:
            message_text = "Список курьеров:\n"
            for admin in admins:
                admin_id, name_admin, external_admin = admin
                message_text += f"ID: {admin_id}\n"
                message_text += f"Имя: {name_admin}\n"
                message_text += f"External ID: {external_admin}\n\n"

            await bot.send_message(call.message.chat.id, message_text, reply_markup=key_city)
            await bot.delete_message(call.message.chat.id, call.message.message_id)

        else:
            await bot.send_message(call.message.chat.id, "Нет зарегистрированных курьеров.", reply_markup=key_city)
            await bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass


async def del_cura_set(call: CallbackQuery, bot: Bot):
    try:
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        cursor.execute("SELECT name_admin FROM cura")

        admin_names = cursor.fetchall()

        conn.close()

        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=admin_name[0], callback_data=f'_cura_del_{admin_name[0]}') for admin_name in
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


async def del_cura_end(call: CallbackQuery, bot: Bot):
    try:
        admin_name = call.data.split('_')[3]
        print(admin_name)
        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')  # баз данных
        cursor = conn.cursor()

        cursor.execute("DELETE FROM cura WHERE name_admin = ?", (admin_name,))

        # Сохраняем изменения
        conn.commit()

        # Закрываем соединение с базой данных
        conn.close()
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Выйти в меню", callback_data='admin_return_')
            ]
        ])
        await bot.send_message(user_id, f"Вы успешно удалили Курьера : {admin_name}", reply_markup=key_admin)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        print(e)


async def cura_set_add_name(call: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        user_id = call.message.chat.id
        await bot.send_message(user_id, "Введите Имя для добавление в курьеры:")
        await state.set_state(Cura_add.cura_name)

        await bot.delete_message(user_id, call.message.message_id)
    except:
        pass


async def cura_set_add_external(message: Message, state: FSMContext, bot: Bot):
    try:
        await state.update_data(admin_name=message.text)
        user_id = message.chat.id
        await bot.delete_message(user_id, message.message_id - 1)

        await bot.send_message(user_id, "Введите external_id для добавление в курьеры:")
        await state.set_state(Cura_add.cura_external)

        await bot.delete_message(user_id, message.message_id)
    except:
        pass


async def cura_set_add_end(message: Message, state: FSMContext, bot: Bot):
    try:
        await state.update_data(admin_id=message.text)
        user_id = message.chat.id
        context_data = await state.get_data()

        admin_name = context_data.get('admin_name')
        admin_id = context_data.get('admin_id')
        admin_nm = str(admin_name)
        admin_i = str(admin_id)
        await bot.delete_message(user_id, message.message_id - 1)

        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO cura (name_admin, external_admin) VALUES (?, ?)', (admin_nm, admin_i))

        conn.commit()

        # Закрываем соединение с базой данных
        conn.close()
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Выйти в меню", callback_data='admin_return_')
            ]

        ])
        await bot.send_message(user_id, f"Курьер {admin_nm} добавлен в базу.", reply_markup=key_admin)
        await bot.delete_message(message.chat.id, message.message_id)
    except:
        pass