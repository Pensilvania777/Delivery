from aiogram import Bot
from aiogram.types import (Message,
                           InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery)
import sqlite3
import re
from utils.state import Admin
import logging
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta




async def admin_set_menu(call: CallbackQuery, bot: Bot):
    try:
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Добавить админа", callback_data='add_admin_set_'),
                InlineKeyboardButton(text="Удалить админа", callback_data='del_admin_set_')
            ],
            [
                InlineKeyboardButton(text="Просмотр админов", callback_data='show_admin_set_'),
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ]
        ])
        await bot.send_message(call.message.chat.id, "Выберите действие.", reply_markup=key_admin)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        print(e)



async def admin_show_set(call: CallbackQuery, bot: Bot):
    try:
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        # Выполняем SQL-запрос для получения всех админов
        cursor.execute('SELECT id, name_admin, external_admin FROM admin')
        admins = cursor.fetchall()

        # Закрываем соединение с базой данных
        conn.close()
        key_city = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Выйти в меню", callback_data='admin_return_')
            ]
        ])
        if admins:
            message_text = "Список админов:\n"
            for admin in admins:
                admin_id, name_admin, external_admin = admin
                message_text += f"ID: {admin_id}\n"
                message_text += f"Имя: {name_admin}\n"
                message_text += f"External ID: {external_admin}\n\n"

            await bot.send_message(call.message.chat.id, message_text, reply_markup=key_city)
            await bot.delete_message(call.message.chat.id, call.message.message_id)

        else:
            await bot.send_message(call.message.chat.id, "Нет зарегистрированных админов.", reply_markup=key_city)
            await bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass


async def del_admin_set(call: CallbackQuery, bot: Bot):
    try:
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        cursor.execute("SELECT name_admin FROM admin")

        admin_names = cursor.fetchall()

        # Закрытие соединения с базой данных
        conn.close()

        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=admin_name[0], callback_data=f'_admin_del_{admin_name[0]}') for admin_name in
                admin_names
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data='admin_return_')
            ]

        ])

        await bot.send_message(call.message.chat.id, "Выберите администратора:", reply_markup=key_admin)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass


async def del_admin_end(call: CallbackQuery, bot: Bot):
    try:
        admin_name = call.data.split('_')[3]
        print(admin_name)
        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')  # баз данных
        cursor = conn.cursor()

        cursor.execute("DELETE FROM admin WHERE name_admin = ?", (admin_name,))

        # Сохраняем изменения
        conn.commit()

        # Закрываем соединение с базой данных
        conn.close()
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Выйти в меню", callback_data='admin_return_')
            ]
        ])
        await bot.send_message(user_id, f"Вы успешно удалили Админа : {admin_name}", reply_markup=key_admin)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        print(e)


async def admin_set_add_name(call: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        user_id = call.message.chat.id
        await bot.send_message(user_id, "Введите Имя для добавление в админы:")
        await state.set_state(Admin.admin_name)

        await bot.delete_message(user_id, call.message.message_id)
    except:
        pass


async def admin_set_add_external(message: Message, state: FSMContext, bot: Bot):
    try:
        await state.update_data(admin_name=message.text)
        user_id = message.chat.id
        await bot.delete_message(user_id, message.message_id - 1)

        await bot.send_message(user_id, "Введите external_id для добавление в админы:")
        await state.set_state(Admin.admin_id)

        await bot.delete_message(user_id, message.message_id)
    except:
        pass


async def admin_set_add_end(message: Message, state: FSMContext, bot: Bot):
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
        cursor.execute('INSERT INTO admin (name_admin, external_admin) VALUES (?, ?)', (admin_nm, admin_i))

        conn.commit()

        # Закрываем соединение с базой данных
        conn.close()
        key_admin = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Выйти в меню", callback_data='admin_return_')
            ]

        ])
        await bot.send_message(user_id, f"Админ {admin_nm} добавлен в базу.", reply_markup=key_admin)
        await bot.delete_message(message.chat.id, message.message_id)
    except:
        pass