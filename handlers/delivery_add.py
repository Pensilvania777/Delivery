import asyncio
import logging
import sys
import re
import sqlite3
from datetime import datetime
import traceback
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import (Message,
                           InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery)
from config.config import TOKEN
from aiogram.fsm.context import FSMContext
from utils.state import Delivery_add
from aiogram import F


async def dev_menu(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        key_city = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Добавление ", callback_data='dev_true_')
            ],
            [
                InlineKeyboardButton(text="Добавление с датой", callback_data='delivery_data_')
            ]

        ])
        await bot.send_message(call.message.chat.id, "Выберите вариант добавления :", reply_markup=key_city)
        await bot.delete_message(user_id, call.message.message_id)


    except:
        pass


async def delivery_add(call: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        user_id = call.message.chat.id
        key_city = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад 🔙", callback_data='menu_return_')
            ]

        ])
        await bot.send_message(user_id, "Отправьте сообщение доставки:", reply_markup=key_city)
        await state.set_state(Delivery_add.delivery_text)

        await bot.delete_message(user_id, call.message.message_id)


    except Exception as e:
        print(e)


async def delivery_add_end(message: Message, bot: Bot, state: FSMContext):
    try:
        user_id = message.chat.id
        mess = ""
        if message.text is not None:
            mess = message.text.lower()
        elif message.caption is not None:
            mess = message.caption.lower()
        data_blocks = mess.strip().split('\n\n')
        await bot.delete_message(user_id, message.message_id - 1)
        for block in data_blocks:
            lines = block.strip().split('\n')
            print(lines)
            if len(lines) == 5:
                number_delivery = lines[0].strip()
                address_delivery = lines[1].strip()
                price_line = ""
                cash_card = ""

                if len(lines) >= 4:
                    price_line = lines[3].strip()
                    cash_card = lines[4].strip()

                for line in lines[2:]:
                    data = re.match(r'(\d+)\s+(.+)', line)
                    if data:
                        coll_tovar, name_price = data.groups()
                        name_tovar, price_data = name_price.rsplit(' ', 1) if ' ' in name_price else (name_price, '')

                        match = re.match(r'(\d+)\((\d+)\)', price_line)
                        if match:
                            price_shop, price_deliver = match.groups()
                        else:
                            price_shop = price_data.strip()
                            price_deliver = ''

                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''SELECT id, external_cura, name_item, coll_tovar 
                                              FROM cura_tovar 
                                              WHERE external_cura = ? AND name_item = ?''',
                                       (user_id, name_tovar))
                        results = cursor.fetchall()
                        conn.close()

                        new_coll_tovar = 0
                        tovar = int(coll_tovar)
                        id_tovar = 0

                        for row in results:
                            id_tovar = row[0]
                            new_coll_tovar = int(row[3])

                        if new_coll_tovar >= tovar:
                            summ_tovar = new_coll_tovar - tovar

                            conn = sqlite3.connect('shop.db')
                            cursor = conn.cursor()
                            cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                           (summ_tovar, id_tovar))
                            conn.commit()
                            conn.close()

                            summ = int(price_shop) - int(price_deliver)

                            current_datetime = datetime.now()
                            current_month = current_datetime.month
                            current_day = current_datetime.day

                            conn = sqlite3.connect('shop.db')
                            cursor = conn.cursor()
                            cursor.execute('''INSERT INTO data_shop
                                                  (number_delivery, adress_delivery, coll_tovar, name_tovar, 
                                                  price_shop, price_deliver, data_create, data_day, cash_card, external_id)
                                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                           (number_delivery, address_delivery, coll_tovar, name_tovar,
                                            summ, price_deliver, current_month, current_day, cash_card, user_id))
                            conn.commit()
                            conn.close()

                            key_city = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="Добавить еще ✅", callback_data='dev_true_')],
                                [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                            ])
                            await bot.send_message(user_id, "Данные успешно добавлены.", reply_markup=key_city)
                            await bot.delete_message(user_id, message.message_id)
                        else:
                            key_city = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                            ])
                            await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                            await bot.delete_message(user_id, message.message_id)
            elif len(lines) == 6:
                number_delivery = lines[0].strip()
                address_delivery = lines[1].strip()
                price_line = ""
                cash_card = ""
                print("ZAEBIS")
                tovar = 0
                new_coll_tovar = 0
                summ = 0
                price_deliver = 0
                coll_tovar1 = 0
                name_tovar1 = ""

                if len(lines) >= 5:
                    price_line = lines[4].strip()
                    cash_card = lines[5].strip()

                data1 = re.match(r'(\d+)\s+(.+)', lines[2])
                if data1:
                    coll_tovar1, name_price = data1.groups()
                    name_tovar1, price_data = name_price.rsplit(' ', 1) if ' ' in name_price else (
                    name_price, '')

                    match1 = re.match(r'(\d+)\((\d+)\)', price_line)
                    if match1:
                        price_shop, price_deliver = match1.groups()
                    else:
                        price_shop = price_data.strip()
                        price_deliver = ''
                    summ = int(price_shop) - int(price_deliver)
                    conn = sqlite3.connect('shop.db')
                    cursor = conn.cursor()
                    cursor.execute('''SELECT id, external_cura, name_item, coll_tovar 
                                                                                      FROM cura_tovar 
                                                                                      WHERE external_cura = ? AND name_item = ?''',
                                   (user_id, name_tovar1))
                    results = cursor.fetchall()
                    conn.close()
                    new_coll_tovar = 0
                    tovar = int(coll_tovar1)
                    id_tovar = 0

                    for row in results:
                        id_tovar = row[0]
                        new_coll_tovar = int(row[3])
                    if tovar <= new_coll_tovar:
                        summ_tovar = new_coll_tovar - tovar
                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                       (summ_tovar, id_tovar))
                        conn.commit()
                        conn.close()
                    else:
                        key_city = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                        ])
                        await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                        await bot.delete_message(user_id, message.message_id)


                data2 = re.match(r'(\d+)\s+(.+)', lines[3])
                name_tovar2 = ""
                if data2:
                    coll_tovar2, name_price2 = data2.groups()
                    name_tovar2, price_data2 = name_price2.rsplit(' ', 1) if ' ' in name_price2 else (
                    name_price2, '')

                    print(name_tovar2, coll_tovar2)
                    conn = sqlite3.connect('shop.db')
                    cursor = conn.cursor()
                    cursor.execute('''SELECT id, external_cura, name_item, coll_tovar 
                                                                  FROM cura_tovar 
                                                                  WHERE external_cura = ? AND name_item = ?''',
                                   (user_id, name_tovar2))
                    results = cursor.fetchall()
                    conn.close()

                    new_coll_tovar2 = 0
                    tovar2 = int(coll_tovar2)
                    id_tovar2 = 0

                    for row in results:
                        id_tovar2 = row[0]
                        new_coll_tovar2 = int(row[3])
                    if tovar2 <= new_coll_tovar2 and tovar <= new_coll_tovar:
                        summ_tovar2 = new_coll_tovar2 - tovar2
                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                       (summ_tovar2, id_tovar2))
                        conn.commit()
                        conn.close()
                        current_datetime = datetime.now()
                        current_month = current_datetime.month
                        current_day = current_datetime.day

                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''INSERT INTO data_shop
                                                                  (number_delivery, adress_delivery, 
                                                                  coll_tovar, name_tovar, coll_tovar_tho, name_tovar_tho,
                                                                  price_shop, price_deliver, data_create, data_day, 
                                                                  cash_card, external_id)
                                                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                       (number_delivery, address_delivery, coll_tovar1, name_tovar1,
                                        coll_tovar2, name_tovar2,
                                        summ, price_deliver, current_month, current_day, cash_card, user_id))
                        conn.commit()
                        conn.close()
                        key_city = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="Добавить еще ✅", callback_data='dev_true_')],
                            [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                        ])
                        await bot.send_message(user_id, "Данные успешно добавлены.", reply_markup=key_city)
                        await bot.delete_message(user_id, message.message_id)
                    else:
                        key_city = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                        ])
                        await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                        await bot.delete_message(user_id, message.message_id)
                else:
                    key_city = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                    ])
                    await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                    await bot.delete_message(user_id, message.message_id)

            elif len(lines) == 7:
                    number_delivery = lines[0].strip()
                    address_delivery = lines[1].strip()
                    price_line = ""
                    cash_card = ""
                    print("ZAEBIS")
                    tovar1 = 0
                    new_coll_tovar1 = 0
                    summ = 0
                    price_deliver1 = 0
                    coll_tovar1 = 0
                    name_tovar1 = ""


                    tovar2 = 0
                    new_coll_tovar2 = 0
                    price_deliver2 = 0
                    coll_tovar2 = 0
                    name_tovar2 = ""

                    tovar3 = 0
                    new_coll_tovar3 = 0
                    price_deliver3 = 0
                    coll_tovar3 = 0
                    name_tovar3 = ""
                    summ_tovar1 = 0
                    if len(lines) >= 5:
                        price_line = lines[5].strip()
                        cash_card = lines[6].strip()

                    # Обработка первого товара
                    data1 = re.match(r'(\d+)\s+(.+)', lines[2])
                    if data1:
                        coll_tovar1, name_price1 = data1.groups()
                        name_tovar1, price_data1 = name_price1.rsplit(' ', 1) if ' ' in name_price1 else (
                        name_price1, '')
                        match1 = re.match(r'(\d+)\((\d+)\)', price_line)
                        if match1:
                            price_shop1, price_deliver1 = match1.groups()
                        else:
                            price_shop1 = price_data1.strip()
                            price_deliver1 = ''
                        print(price_shop1, price_deliver1)
                        summ = int(price_shop1) - int(price_deliver1)
                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''SELECT id, external_cura, name_item, coll_tovar 
                                              FROM cura_tovar 
                                              WHERE external_cura = ? AND name_item = ?''',
                                       (user_id, name_tovar1))
                        results = cursor.fetchall()
                        conn.close()
                        new_coll_tovar1 = 0
                        tovar1 = int(coll_tovar1)
                        id_tovar1 = 0

                        for row in results:
                            id_tovar1 = row[0]
                            new_coll_tovar1 = int(row[3])

                        if tovar1 <= new_coll_tovar1:
                            summ_tovar1 = new_coll_tovar1 - tovar1
                            conn = sqlite3.connect('shop.db')
                            cursor = conn.cursor()
                            cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                           (summ_tovar1, id_tovar1))
                            conn.commit()
                            conn.close()
                        else:
                            key_city = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                            ])
                            await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                            await bot.delete_message(user_id, message.message_id)
                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                       (summ_tovar1, id_tovar1))
                        conn.commit()
                        conn.close()

                    # Обработка второго товара
                    data2 = re.match(r'(\d+)\s+(.+)', lines[3])
                    if data2:
                        coll_tovar2, name_price2 = data2.groups()
                        name_tovar2, price_data2 = name_price2.rsplit(' ', 1) if ' ' in name_price2 else (
                        name_price2, '')

                        match2 = re.match(r'(\d+)\((\d+)\)', price_line)
                        if match2:
                            price_shop2, price_deliver2 = match2.groups()
                        else:
                            price_shop2 = price_data2.strip()
                            price_deliver2 = ''

                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''SELECT id, external_cura, name_item, coll_tovar 
                                              FROM cura_tovar 
                                              WHERE external_cura = ? AND name_item = ?''',
                                       (user_id, name_tovar2))
                        results = cursor.fetchall()
                        conn.close()
                        new_coll_tovar2 = 0
                        tovar2 = int(coll_tovar2)
                        id_tovar2 = 0

                        for row in results:
                            id_tovar2 = row[0]
                            new_coll_tovar2 = int(row[3])

                        if tovar2 <= new_coll_tovar2:
                            summ_tovar2 = new_coll_tovar2 - tovar2
                            conn = sqlite3.connect('shop.db')
                            cursor = conn.cursor()
                            cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                           (summ_tovar2, id_tovar2))
                            conn.commit()
                            conn.close()
                        else:
                            key_city = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                            ])
                            await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                            await bot.delete_message(user_id, message.message_id)
                    data3 = re.match(r'(\d+)\s+(.+)', lines[4])
                    if data3:
                        coll_tovar3, name_price3 = data3.groups()
                        name_tovar3, price_data3 = name_price3.rsplit(' ', 1) if ' ' in name_price3 else (
                        name_price3, '')

                        match3 = re.match(r'(\d+)\((\d+)\)', price_line)
                        if match3:
                            price_shop3, price_deliver3 = match3.groups()
                        else:
                            price_shop3 = price_data3.strip()
                            price_deliver3 = ''

                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''SELECT id, external_cura, name_item, coll_tovar 
                                              FROM cura_tovar 
                                              WHERE external_cura = ? AND name_item = ?''',
                                       (user_id, name_tovar3))
                        results = cursor.fetchall()
                        conn.close()
                        new_coll_tovar3 = 0
                        tovar3 = int(coll_tovar3)
                        id_tovar3 = 0

                        for row in results:
                            id_tovar3 = row[0]
                            new_coll_tovar3 = int(row[3])

                        if tovar3 <= new_coll_tovar3 and tovar2 <= new_coll_tovar2 and tovar1 <= new_coll_tovar1:
                            summ_tovar3 = new_coll_tovar3 - tovar3
                            conn = sqlite3.connect('shop.db')
                            cursor = conn.cursor()
                            cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                           (summ_tovar3, id_tovar3))
                            conn.commit()
                            conn.close()
                            current_datetime = datetime.now()
                            current_month = current_datetime.month
                            current_day = current_datetime.day

                            conn = sqlite3.connect('shop.db')
                            cursor = conn.cursor()
                            cursor.execute('''INSERT INTO data_shop
                                                                                              (number_delivery, adress_delivery, 
                                                                                              coll_tovar, name_tovar, coll_tovar_tho, name_tovar_tho,
                                                                                              coll_tovar_three, name_tovar_three, 
                                                                                              price_shop, price_deliver, data_create, data_day, 
                                                                                              cash_card, external_id)
                                                                                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                           (number_delivery, address_delivery, coll_tovar1, name_tovar1,
                                            coll_tovar2, name_tovar2, coll_tovar3, name_tovar3,
                                            summ, price_deliver1, current_month, current_day, cash_card, user_id))
                            conn.commit()
                            conn.close()
                            key_city = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="Добавить еще ✅", callback_data='dev_true_')],
                                [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                            ])
                            await bot.send_message(user_id, "Данные успешно добавлены.", reply_markup=key_city)
                            await bot.delete_message(user_id, message.message_id)
                        else:
                            key_city = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                            ])
                            await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                            await bot.delete_message(user_id, message.message_id)

                    else:
                        key_city = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                        ])
                        await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                        await bot.delete_message(user_id, message.message_id)
            elif len(lines) == 8:
                    number_delivery = lines[0].strip()
                    address_delivery = lines[1].strip()
                    price_line = ""
                    cash_card = ""
                    print("ZAEBIS")
                    tovar1 = 0
                    new_coll_tovar1 = 0
                    summ = 0
                    price_deliver1 = 0
                    coll_tovar1 = 0
                    name_tovar1 = ""

                    tovar2 = 0
                    new_coll_tovar2 = 0
                    price_deliver2 = 0
                    coll_tovar2 = 0
                    name_tovar2 = ""

                    tovar3 = 0
                    new_coll_tovar3 = 0
                    price_deliver3 = 0
                    coll_tovar3 = 0
                    name_tovar3 = ""

                    if len(lines) >= 5:
                        price_line = lines[6].strip()
                        cash_card = lines[7].strip()

                    data1 = re.match(r'(\d+)\s+(.+)', lines[2])
                    if data1:
                        coll_tovar1, name_price1 = data1.groups()
                        name_tovar1, price_data1 = name_price1.rsplit(' ', 1) if ' ' in name_price1 else (
                        name_price1, '')
                        match1 = re.match(r'(\d+)\((\d+)\)', price_line)
                        if match1:
                            price_shop1, price_deliver1 = match1.groups()
                        else:
                            price_shop1 = price_data1.strip()
                            price_deliver1 = ''
                        print(price_shop1, price_deliver1)
                        summ = int(price_shop1) - int(price_deliver1)
                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''SELECT id, external_cura, name_item, coll_tovar 
                                              FROM cura_tovar 
                                              WHERE external_cura = ? AND name_item = ?''',
                                       (user_id, name_tovar1))
                        results = cursor.fetchall()
                        conn.close()
                        new_coll_tovar1 = 0
                        tovar1 = int(coll_tovar1)
                        id_tovar1 = 0

                        for row in results:
                            id_tovar1 = row[0]
                            new_coll_tovar1 = int(row[3])

                        if tovar1 <= new_coll_tovar1:
                            summ_tovar1 = new_coll_tovar1 - tovar1
                            conn = sqlite3.connect('shop.db')
                            cursor = conn.cursor()
                            cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                           (summ_tovar1, id_tovar1))
                            conn.commit()
                            conn.close()
                        else:
                            key_city = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                            ])
                            await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                            await bot.delete_message(user_id, message.message_id)




                    # Обработка второго товара
                    data2 = re.match(r'(\d+)\s+(.+)', lines[3])
                    if data2:
                        coll_tovar2, name_price2 = data2.groups()
                        name_tovar2, price_data2 = name_price2.rsplit(' ', 1) if ' ' in name_price2 else (
                        name_price2, '')

                        match2 = re.match(r'(\d+)\((\d+)\)', price_line)
                        if match2:
                            price_shop2, price_deliver2 = match2.groups()
                        else:
                            price_shop2 = price_data2.strip()
                            price_deliver2 = ''

                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''SELECT id, external_cura, name_item, coll_tovar 
                                              FROM cura_tovar 
                                              WHERE external_cura = ? AND name_item = ?''',
                                       (user_id, name_tovar2))
                        results = cursor.fetchall()
                        conn.close()
                        new_coll_tovar2 = 0
                        tovar2 = int(coll_tovar2)
                        id_tovar2 = 0

                        for row in results:
                            id_tovar2 = row[0]
                            new_coll_tovar2 = int(row[3])
                        if tovar2 <= new_coll_tovar2:
                            summ_tovar2 = new_coll_tovar2 - tovar2
                            conn = sqlite3.connect('shop.db')
                            cursor = conn.cursor()
                            cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                           (summ_tovar2, id_tovar2))
                            conn.commit()
                            conn.close()
                        else:
                            key_city = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                            ])
                            await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                            await bot.delete_message(user_id, message.message_id)

                    data3 = re.match(r'(\d+)\s+(.+)', lines[4])
                    if data3:
                        coll_tovar3, name_price3 = data3.groups()
                        name_tovar3, price_data3 = name_price3.rsplit(' ', 1) if ' ' in name_price3 else (
                        name_price3, '')

                        match3 = re.match(r'(\d+)\((\d+)\)', price_line)
                        if match3:
                            price_shop3, price_deliver3 = match3.groups()
                        else:
                            price_shop3 = price_data3.strip()
                            price_deliver3 = ''

                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''SELECT id, external_cura, name_item, coll_tovar 
                                              FROM cura_tovar 
                                              WHERE external_cura = ? AND name_item = ?''',
                                       (user_id, name_tovar3))
                        results = cursor.fetchall()
                        conn.close()
                        new_coll_tovar3 = 0
                        tovar3 = int(coll_tovar3)
                        id_tovar3 = 0

                        for row in results:
                            id_tovar3 = row[0]
                            new_coll_tovar3 = int(row[3])

                        if tovar3 <= new_coll_tovar3:
                            summ_tovar3 = new_coll_tovar3 - tovar3
                            conn = sqlite3.connect('shop.db')
                            cursor = conn.cursor()
                            cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                           (summ_tovar3, id_tovar3))
                            conn.commit()
                            conn.close()
                        else:
                            key_city = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                            ])
                            await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                            await bot.delete_message(user_id, message.message_id)



                    data4 = re.match(r'(\d+)\s+(.+)', lines[5])

                    if data4:
                        coll_tovar4, name_price4 = data4.groups()
                        name_tovar4, price_data4 = name_price4.rsplit(' ', 1) if ' ' in name_price4 else (
                            name_price4, '')

                        match4 = re.match(r'(\d+)\((\d+)\)', price_line)
                        if match4:
                            price_shop4, price_deliver4 = match4.groups()
                        else:
                            price_shop4 = price_data4.strip()
                            price_deliver3 = ''

                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''SELECT id, external_cura, name_item, coll_tovar 
                                                                      FROM cura_tovar 
                                                                      WHERE external_cura = ? AND name_item = ?''',
                                       (user_id, name_tovar4))
                        results = cursor.fetchall()
                        conn.close()
                        new_coll_tovar4 = 0
                        tovar4 = int(coll_tovar4)
                        id_tovar4 = 0

                        for row in results:
                            id_tovar4 = row[0]
                            new_coll_tovar4 = int(row[3])
                        summ_tovar4 = 0
                        if (tovar3 <= new_coll_tovar3 and tovar2 <= new_coll_tovar2 and tovar1 <= new_coll_tovar1 and
                                tovar4 <= new_coll_tovar4):
                            summ_tovar4 = new_coll_tovar4 - tovar4
                            conn = sqlite3.connect('shop.db')
                            cursor = conn.cursor()
                            cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                           (summ_tovar4, id_tovar4))
                            conn.commit()
                            conn.close()
                            current_datetime = datetime.now()
                            current_month = current_datetime.month
                            current_day = current_datetime.day

                            conn = sqlite3.connect('shop.db')
                            cursor = conn.cursor()
                            cursor.execute('''INSERT INTO data_shop
                                                                                              (number_delivery, adress_delivery, 
                                                                                              coll_tovar, name_tovar, coll_tovar_tho, name_tovar_tho,
                                                                                              coll_tovar_three, name_tovar_three,
                                                                                              coll_tovar_four, name_tovar_four,
                                                                                              price_shop, price_deliver, data_create, data_day, 
                                                                                              cash_card, external_id)
                                                                                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                           (number_delivery, address_delivery, coll_tovar1, name_tovar1,
                                            coll_tovar2, name_tovar2, coll_tovar3, name_tovar3,coll_tovar4, name_tovar4,
                                            summ, price_deliver1, current_month, current_day, cash_card, user_id))
                            conn.commit()
                            conn.close()
                            key_city = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="Добавить еще ✅", callback_data='dev_true_')],
                                [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                            ])
                            await bot.send_message(user_id, "Данные успешно добавлены.", reply_markup=key_city)
                            await bot.delete_message(user_id, message.message_id)
                        else:
                            key_city = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                            ])
                            await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                            await bot.delete_message(user_id, message.message_id)
    except Exception as e:
        print(f"Ошибка: {e}")
        traceback.print_exc()


async def delivery_add_month(call: CallbackQuery, bot: Bot):
    try:
        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        sql_query = '''
            SELECT DISTINCT data_create
            FROM data_shop
            WHERE external_id = ?;
        '''
        cursor.execute(sql_query, (user_id,))
        results = cursor.fetchall()
        conn.close()

        if len(results) == 0:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='menu_return_')
                ]

            ])

            await bot.send_message(user_id, "Нет дат для добавления.", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
        else:
            key_city = InlineKeyboardMarkup(inline_keyboard=[])

            for i in range(0, len(results), 2):
                row = []
                # Добавляем две кнопки в строку, если есть два города
                if i < len(results) - 1:
                    row.append(
                        InlineKeyboardButton(text=results[i][0], callback_data=f'delivery_month_{results[i][0]}'))
                    row.append(
                        InlineKeyboardButton(text=results[i + 1][0],
                                             callback_data=f'delivery_month_{results[i + 1][0]}'))
                # Если остался один город, добавляем его в отдельную кнопку
                else:
                    row.append(
                        InlineKeyboardButton(text=results[i][0], callback_data=f'delivery_month_{results[i][0]}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='menu_return_')
            ])
            await bot.send_message(user_id, "Выберите месяц:", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)


async def delivery_add_day(call: CallbackQuery, bot: Bot):
    try:
        month = call.data.split('_')[2]

        user_id = call.message.chat.id
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()

        sql_query = '''
                    SELECT DISTINCT data_day
                    FROM data_shop
                    WHERE external_id = ?;
                '''
        cursor.execute(sql_query, (user_id,))

        # Получение результатов запроса
        results = cursor.fetchall()
        conn.close()

        if len(results) == 0:
            key_city = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад", callback_data='menu_return_')
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
                        InlineKeyboardButton(text=results[i][0], callback_data=f'delivery_day_{results[i][0]}_{month}'))
                    row.append(
                        InlineKeyboardButton(text=results[i + 1][0],
                                             callback_data=f'delivery_day_{results[i + 1][0]}_{month}'))
                # Если остался один город, добавляем его в отдельную кнопку
                else:
                    row.append(
                        InlineKeyboardButton(text=results[i][0], callback_data=f'delivery_day_{results[i][0]}_{month}'))
                key_city.inline_keyboard.append(row)

            key_city.inline_keyboard.append([
                InlineKeyboardButton(text="Назад", callback_data='menu_return_')
            ])
            await bot.send_message(user_id, f"Выберите день для месяца {month}:", reply_markup=key_city)
            await bot.delete_message(user_id, call.message.message_id)
    except Exception as e:
        print(e)

async def delivery_add_sms_end(call: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        month = call.data.split('_')[3]
        day = call.data.split('_')[2]
        await state.update_data(month=month)
        await state.update_data(day=day)

        user_id = call.message.chat.id
        key_city = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад 🔙", callback_data='menu_return_')
            ]

        ])
        await bot.send_message(user_id, "Отправьте сообщение доставки:", reply_markup=key_city)
        await state.set_state(Delivery_add.delivery_day)

        await bot.delete_message(user_id, call.message.message_id)

    except Exception as e:
        print(e)

async def delivery_add_day_end(message: Message, bot: Bot, state: FSMContext):
    try:
        context_data = await state.get_data()

        month = context_data.get('month')
        day = context_data.get('day')
        print(day, month)
        user_id = message.chat.id
        mess = ""
        if message.text is not None:
            mess = message.text.lower()
        elif message.caption is not None:
            mess = message.caption.lower()
        data_blocks = mess.strip().split('\n\n')
        await bot.delete_message(user_id, message.message_id - 1)

        for block in data_blocks:
            # Разделение блока данных на строки
            lines = block.strip().split('\n')
            if len(lines) == 5:
                number_delivery = lines[0].strip()
                address_delivery = lines[1].strip()
                price_line = ""
                cash_card = ""

                if len(lines) >= 4:
                    price_line = lines[3].strip()
                    cash_card = lines[4].strip()

                for line in lines[2:]:
                    data = re.match(r'(\d+)\s+(.+)', line)
                    if data:
                        coll_tovar, name_price = data.groups()
                        name_tovar, price_data = name_price.rsplit(' ', 1) if ' ' in name_price else (name_price, '')

                        match = re.match(r'(\d+)\((\d+)\)', price_line)
                        if match:
                            price_shop, price_deliver = match.groups()
                        else:
                            price_shop = price_data.strip()
                            price_deliver = ''

                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''SELECT id, external_cura, name_item, coll_tovar 
                                              FROM cura_tovar 
                                              WHERE external_cura = ? AND name_item = ?''',
                                       (user_id, name_tovar))
                        results = cursor.fetchall()
                        conn.close()

                        new_coll_tovar = 0
                        tovar = int(coll_tovar)
                        id_tovar = 0

                        for row in results:
                            id_tovar = row[0]
                            new_coll_tovar = int(row[3])

                        if new_coll_tovar >= tovar:
                            summ_tovar = new_coll_tovar - tovar

                            conn = sqlite3.connect('shop.db')
                            cursor = conn.cursor()
                            cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                           (summ_tovar, id_tovar))
                            conn.commit()
                            conn.close()

                            summ = int(price_shop) - int(price_deliver)

                            current_datetime = datetime.now()
                            current_month = current_datetime.month
                            current_day = current_datetime.day

                            conn = sqlite3.connect('shop.db')
                            cursor = conn.cursor()
                            cursor.execute('''INSERT INTO data_shop
                                                  (number_delivery, adress_delivery, coll_tovar, name_tovar, 
                                                  price_shop, price_deliver, data_create, data_day, cash_card, external_id)
                                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                           (number_delivery, address_delivery, coll_tovar, name_tovar,
                                            summ, price_deliver, current_month, current_day, cash_card, user_id))
                            conn.commit()
                            conn.close()

                            key_city = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="Добавить еще ✅", callback_data='dev_true_')],
                                [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                            ])
                            await bot.send_message(user_id, "Данные успешно добавлены.", reply_markup=key_city)
                            await bot.delete_message(user_id, message.message_id)
                        else:
                            key_city = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                            ])
                            await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                            await bot.delete_message(user_id, message.message_id)
            elif len(lines) == 6:
                number_delivery = lines[0].strip()
                address_delivery = lines[1].strip()
                price_line = ""
                cash_card = ""
                print("ZAEBIS")
                tovar = 0
                new_coll_tovar = 0
                summ = 0
                price_deliver = 0
                coll_tovar1 = 0
                name_tovar1 = ""

                if len(lines) >= 5:
                    price_line = lines[4].strip()
                    cash_card = lines[5].strip()

                data1 = re.match(r'(\d+)\s+(.+)', lines[2])
                if data1:
                    coll_tovar1, name_price = data1.groups()
                    name_tovar1, price_data = name_price.rsplit(' ', 1) if ' ' in name_price else (
                        name_price, '')

                    match1 = re.match(r'(\d+)\((\d+)\)', price_line)
                    if match1:
                        price_shop, price_deliver = match1.groups()
                    else:
                        price_shop = price_data.strip()
                        price_deliver = ''
                    summ = int(price_shop) - int(price_deliver)
                    conn = sqlite3.connect('shop.db')
                    cursor = conn.cursor()
                    cursor.execute('''SELECT id, external_cura, name_item, coll_tovar 
                                                                                      FROM cura_tovar 
                                                                                      WHERE external_cura = ? AND name_item = ?''',
                                   (user_id, name_tovar1))
                    results = cursor.fetchall()
                    conn.close()
                    new_coll_tovar = 0
                    tovar = int(coll_tovar1)
                    id_tovar = 0

                    for row in results:
                        id_tovar = row[0]
                        new_coll_tovar = int(row[3])
                    if tovar <= new_coll_tovar:
                        summ_tovar = new_coll_tovar - tovar
                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                       (summ_tovar, id_tovar))
                        conn.commit()
                        conn.close()
                    else:
                        key_city = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                        ])
                        await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                        await bot.delete_message(user_id, message.message_id)

                data2 = re.match(r'(\d+)\s+(.+)', lines[3])
                name_tovar2 = ""
                if data2:
                    coll_tovar2, name_price2 = data2.groups()
                    name_tovar2, price_data2 = name_price2.rsplit(' ', 1) if ' ' in name_price2 else (
                        name_price2, '')

                    print(name_tovar2, coll_tovar2)
                    conn = sqlite3.connect('shop.db')
                    cursor = conn.cursor()
                    cursor.execute('''SELECT id, external_cura, name_item, coll_tovar 
                                                                  FROM cura_tovar 
                                                                  WHERE external_cura = ? AND name_item = ?''',
                                   (user_id, name_tovar2))
                    results = cursor.fetchall()
                    conn.close()

                    new_coll_tovar2 = 0
                    tovar2 = int(coll_tovar2)
                    id_tovar2 = 0

                    for row in results:
                        id_tovar2 = row[0]
                        new_coll_tovar2 = int(row[3])
                    if tovar2 <= new_coll_tovar2 and tovar <= new_coll_tovar:
                        summ_tovar2 = new_coll_tovar2 - tovar2
                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                       (summ_tovar2, id_tovar2))
                        conn.commit()
                        conn.close()
                        current_datetime = datetime.now()
                        current_month = current_datetime.month
                        current_day = current_datetime.day

                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''INSERT INTO data_shop
                                                                  (number_delivery, adress_delivery, 
                                                                  coll_tovar, name_tovar, coll_tovar_tho, name_tovar_tho,
                                                                  price_shop, price_deliver, data_create, data_day, 
                                                                  cash_card, external_id)
                                                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                       (number_delivery, address_delivery, coll_tovar1, name_tovar1,
                                        coll_tovar2, name_tovar2,
                                        summ, price_deliver, current_month, current_day, cash_card, user_id))
                        conn.commit()
                        conn.close()
                        key_city = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="Добавить еще ✅", callback_data='dev_true_')],
                            [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                        ])
                        await bot.send_message(user_id, "Данные успешно добавлены.", reply_markup=key_city)
                        await bot.delete_message(user_id, message.message_id)
                    else:
                        key_city = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                        ])
                        await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                        await bot.delete_message(user_id, message.message_id)
                else:
                    key_city = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                    ])
                    await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                    await bot.delete_message(user_id, message.message_id)

            elif len(lines) == 7:
                number_delivery = lines[0].strip()
                address_delivery = lines[1].strip()
                price_line = ""
                cash_card = ""
                print("ZAEBIS")
                tovar1 = 0
                new_coll_tovar1 = 0
                summ = 0
                price_deliver1 = 0
                coll_tovar1 = 0
                name_tovar1 = ""

                tovar2 = 0
                new_coll_tovar2 = 0
                price_deliver2 = 0
                coll_tovar2 = 0
                name_tovar2 = ""

                tovar3 = 0
                new_coll_tovar3 = 0
                price_deliver3 = 0
                coll_tovar3 = 0
                name_tovar3 = ""
                summ_tovar1 = 0
                if len(lines) >= 5:
                    price_line = lines[5].strip()
                    cash_card = lines[6].strip()

                # Обработка первого товара
                data1 = re.match(r'(\d+)\s+(.+)', lines[2])
                if data1:
                    coll_tovar1, name_price1 = data1.groups()
                    name_tovar1, price_data1 = name_price1.rsplit(' ', 1) if ' ' in name_price1 else (
                        name_price1, '')
                    match1 = re.match(r'(\d+)\((\d+)\)', price_line)
                    if match1:
                        price_shop1, price_deliver1 = match1.groups()
                    else:
                        price_shop1 = price_data1.strip()
                        price_deliver1 = ''
                    print(price_shop1, price_deliver1)
                    summ = int(price_shop1) - int(price_deliver1)
                    conn = sqlite3.connect('shop.db')
                    cursor = conn.cursor()
                    cursor.execute('''SELECT id, external_cura, name_item, coll_tovar 
                                              FROM cura_tovar 
                                              WHERE external_cura = ? AND name_item = ?''',
                                   (user_id, name_tovar1))
                    results = cursor.fetchall()
                    conn.close()
                    new_coll_tovar1 = 0
                    tovar1 = int(coll_tovar1)
                    id_tovar1 = 0

                    for row in results:
                        id_tovar1 = row[0]
                        new_coll_tovar1 = int(row[3])

                    if tovar1 <= new_coll_tovar1:
                        summ_tovar1 = new_coll_tovar1 - tovar1
                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                       (summ_tovar1, id_tovar1))
                        conn.commit()
                        conn.close()
                    else:
                        key_city = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                        ])
                        await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                        await bot.delete_message(user_id, message.message_id)
                    conn = sqlite3.connect('shop.db')
                    cursor = conn.cursor()
                    cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                   (summ_tovar1, id_tovar1))
                    conn.commit()
                    conn.close()

                # Обработка второго товара
                data2 = re.match(r'(\d+)\s+(.+)', lines[3])
                if data2:
                    coll_tovar2, name_price2 = data2.groups()
                    name_tovar2, price_data2 = name_price2.rsplit(' ', 1) if ' ' in name_price2 else (
                        name_price2, '')

                    match2 = re.match(r'(\d+)\((\d+)\)', price_line)
                    if match2:
                        price_shop2, price_deliver2 = match2.groups()
                    else:
                        price_shop2 = price_data2.strip()
                        price_deliver2 = ''

                    conn = sqlite3.connect('shop.db')
                    cursor = conn.cursor()
                    cursor.execute('''SELECT id, external_cura, name_item, coll_tovar 
                                              FROM cura_tovar 
                                              WHERE external_cura = ? AND name_item = ?''',
                                   (user_id, name_tovar2))
                    results = cursor.fetchall()
                    conn.close()
                    new_coll_tovar2 = 0
                    tovar2 = int(coll_tovar2)
                    id_tovar2 = 0

                    for row in results:
                        id_tovar2 = row[0]
                        new_coll_tovar2 = int(row[3])

                    if tovar2 <= new_coll_tovar2:
                        summ_tovar2 = new_coll_tovar2 - tovar2
                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                       (summ_tovar2, id_tovar2))
                        conn.commit()
                        conn.close()
                    else:
                        key_city = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                        ])
                        await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                        await bot.delete_message(user_id, message.message_id)
                data3 = re.match(r'(\d+)\s+(.+)', lines[4])
                if data3:
                    coll_tovar3, name_price3 = data3.groups()
                    name_tovar3, price_data3 = name_price3.rsplit(' ', 1) if ' ' in name_price3 else (
                        name_price3, '')

                    match3 = re.match(r'(\d+)\((\d+)\)', price_line)
                    if match3:
                        price_shop3, price_deliver3 = match3.groups()
                    else:
                        price_shop3 = price_data3.strip()
                        price_deliver3 = ''

                    conn = sqlite3.connect('shop.db')
                    cursor = conn.cursor()
                    cursor.execute('''SELECT id, external_cura, name_item, coll_tovar 
                                              FROM cura_tovar 
                                              WHERE external_cura = ? AND name_item = ?''',
                                   (user_id, name_tovar3))
                    results = cursor.fetchall()
                    conn.close()
                    new_coll_tovar3 = 0
                    tovar3 = int(coll_tovar3)
                    id_tovar3 = 0

                    for row in results:
                        id_tovar3 = row[0]
                        new_coll_tovar3 = int(row[3])

                    if tovar3 <= new_coll_tovar3 and tovar2 <= new_coll_tovar2 and tovar1 <= new_coll_tovar1:
                        summ_tovar3 = new_coll_tovar3 - tovar3
                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                       (summ_tovar3, id_tovar3))
                        conn.commit()
                        conn.close()
                        current_datetime = datetime.now()
                        current_month = current_datetime.month
                        current_day = current_datetime.day

                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''INSERT INTO data_shop
                                                                                              (number_delivery, adress_delivery, 
                                                                                              coll_tovar, name_tovar, coll_tovar_tho, name_tovar_tho,
                                                                                              coll_tovar_three, name_tovar_three, 
                                                                                              price_shop, price_deliver, data_create, data_day, 
                                                                                              cash_card, external_id)
                                                                                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                       (number_delivery, address_delivery, coll_tovar1, name_tovar1,
                                        coll_tovar2, name_tovar2, coll_tovar3, name_tovar3,
                                        summ, price_deliver1, current_month, current_day, cash_card, user_id))
                        conn.commit()
                        conn.close()
                        key_city = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="Добавить еще ✅", callback_data='dev_true_')],
                            [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                        ])
                        await bot.send_message(user_id, "Данные успешно добавлены.", reply_markup=key_city)
                        await bot.delete_message(user_id, message.message_id)
                    else:
                        key_city = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                        ])
                        await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                        await bot.delete_message(user_id, message.message_id)

                else:
                    key_city = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                    ])
                    await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                    await bot.delete_message(user_id, message.message_id)
            elif len(lines) == 8:
                number_delivery = lines[0].strip()
                address_delivery = lines[1].strip()
                price_line = ""
                cash_card = ""
                print("ZAEBIS")
                tovar1 = 0
                new_coll_tovar1 = 0
                summ = 0
                price_deliver1 = 0
                coll_tovar1 = 0
                name_tovar1 = ""

                tovar2 = 0
                new_coll_tovar2 = 0
                price_deliver2 = 0
                coll_tovar2 = 0
                name_tovar2 = ""

                tovar3 = 0
                new_coll_tovar3 = 0
                price_deliver3 = 0
                coll_tovar3 = 0
                name_tovar3 = ""

                if len(lines) >= 5:
                    price_line = lines[6].strip()
                    cash_card = lines[7].strip()

                data1 = re.match(r'(\d+)\s+(.+)', lines[2])
                if data1:
                    coll_tovar1, name_price1 = data1.groups()
                    name_tovar1, price_data1 = name_price1.rsplit(' ', 1) if ' ' in name_price1 else (
                        name_price1, '')
                    match1 = re.match(r'(\d+)\((\d+)\)', price_line)
                    if match1:
                        price_shop1, price_deliver1 = match1.groups()
                    else:
                        price_shop1 = price_data1.strip()
                        price_deliver1 = ''
                    print(price_shop1, price_deliver1)
                    summ = int(price_shop1) - int(price_deliver1)
                    conn = sqlite3.connect('shop.db')
                    cursor = conn.cursor()
                    cursor.execute('''SELECT id, external_cura, name_item, coll_tovar 
                                              FROM cura_tovar 
                                              WHERE external_cura = ? AND name_item = ?''',
                                   (user_id, name_tovar1))
                    results = cursor.fetchall()
                    conn.close()
                    new_coll_tovar1 = 0
                    tovar1 = int(coll_tovar1)
                    id_tovar1 = 0

                    for row in results:
                        id_tovar1 = row[0]
                        new_coll_tovar1 = int(row[3])

                    if tovar1 <= new_coll_tovar1:
                        summ_tovar1 = new_coll_tovar1 - tovar1
                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                       (summ_tovar1, id_tovar1))
                        conn.commit()
                        conn.close()
                    else:
                        key_city = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                        ])
                        await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                        await bot.delete_message(user_id, message.message_id)

                # Обработка второго товара
                data2 = re.match(r'(\d+)\s+(.+)', lines[3])
                if data2:
                    coll_tovar2, name_price2 = data2.groups()
                    name_tovar2, price_data2 = name_price2.rsplit(' ', 1) if ' ' in name_price2 else (
                        name_price2, '')

                    match2 = re.match(r'(\d+)\((\d+)\)', price_line)
                    if match2:
                        price_shop2, price_deliver2 = match2.groups()
                    else:
                        price_shop2 = price_data2.strip()
                        price_deliver2 = ''

                    conn = sqlite3.connect('shop.db')
                    cursor = conn.cursor()
                    cursor.execute('''SELECT id, external_cura, name_item, coll_tovar 
                                              FROM cura_tovar 
                                              WHERE external_cura = ? AND name_item = ?''',
                                   (user_id, name_tovar2))
                    results = cursor.fetchall()
                    conn.close()
                    new_coll_tovar2 = 0
                    tovar2 = int(coll_tovar2)
                    id_tovar2 = 0

                    for row in results:
                        id_tovar2 = row[0]
                        new_coll_tovar2 = int(row[3])
                    if tovar2 <= new_coll_tovar2:
                        summ_tovar2 = new_coll_tovar2 - tovar2
                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                       (summ_tovar2, id_tovar2))
                        conn.commit()
                        conn.close()
                    else:
                        key_city = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                        ])
                        await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                        await bot.delete_message(user_id, message.message_id)

                data3 = re.match(r'(\d+)\s+(.+)', lines[4])
                if data3:
                    coll_tovar3, name_price3 = data3.groups()
                    name_tovar3, price_data3 = name_price3.rsplit(' ', 1) if ' ' in name_price3 else (
                        name_price3, '')

                    match3 = re.match(r'(\d+)\((\d+)\)', price_line)
                    if match3:
                        price_shop3, price_deliver3 = match3.groups()
                    else:
                        price_shop3 = price_data3.strip()
                        price_deliver3 = ''

                    conn = sqlite3.connect('shop.db')
                    cursor = conn.cursor()
                    cursor.execute('''SELECT id, external_cura, name_item, coll_tovar 
                                              FROM cura_tovar 
                                              WHERE external_cura = ? AND name_item = ?''',
                                   (user_id, name_tovar3))
                    results = cursor.fetchall()
                    conn.close()
                    new_coll_tovar3 = 0
                    tovar3 = int(coll_tovar3)
                    id_tovar3 = 0

                    for row in results:
                        id_tovar3 = row[0]
                        new_coll_tovar3 = int(row[3])

                    if tovar3 <= new_coll_tovar3:
                        summ_tovar3 = new_coll_tovar3 - tovar3
                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                       (summ_tovar3, id_tovar3))
                        conn.commit()
                        conn.close()
                    else:
                        key_city = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                        ])
                        await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                        await bot.delete_message(user_id, message.message_id)

                data4 = re.match(r'(\d+)\s+(.+)', lines[5])

                if data4:
                    coll_tovar4, name_price4 = data4.groups()
                    name_tovar4, price_data4 = name_price4.rsplit(' ', 1) if ' ' in name_price4 else (
                        name_price4, '')

                    match4 = re.match(r'(\d+)\((\d+)\)', price_line)
                    if match4:
                        price_shop4, price_deliver4 = match4.groups()
                    else:
                        price_shop4 = price_data4.strip()
                        price_deliver3 = ''

                    conn = sqlite3.connect('shop.db')
                    cursor = conn.cursor()
                    cursor.execute('''SELECT id, external_cura, name_item, coll_tovar 
                                                                      FROM cura_tovar 
                                                                      WHERE external_cura = ? AND name_item = ?''',
                                   (user_id, name_tovar4))
                    results = cursor.fetchall()
                    conn.close()
                    new_coll_tovar4 = 0
                    tovar4 = int(coll_tovar4)
                    id_tovar4 = 0

                    for row in results:
                        id_tovar4 = row[0]
                        new_coll_tovar4 = int(row[3])
                    summ_tovar4 = 0
                    if (tovar3 <= new_coll_tovar3 and tovar2 <= new_coll_tovar2 and tovar1 <= new_coll_tovar1 and
                            tovar4 <= new_coll_tovar4):
                        summ_tovar4 = new_coll_tovar4 - tovar4
                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''UPDATE cura_tovar SET coll_tovar = ? WHERE id = ?''',
                                       (summ_tovar4, id_tovar4))
                        conn.commit()
                        conn.close()
                        current_datetime = datetime.now()
                        current_month = current_datetime.month
                        current_day = current_datetime.day

                        conn = sqlite3.connect('shop.db')
                        cursor = conn.cursor()
                        cursor.execute('''INSERT INTO data_shop
                                                                                              (number_delivery, adress_delivery, 
                                                                                              coll_tovar, name_tovar, coll_tovar_tho, name_tovar_tho,
                                                                                              coll_tovar_three, name_tovar_three,
                                                                                              coll_tovar_four, name_tovar_four,
                                                                                              price_shop, price_deliver, data_create, data_day, 
                                                                                              cash_card, external_id)
                                                                                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                       (number_delivery, address_delivery, coll_tovar1, name_tovar1,
                                        coll_tovar2, name_tovar2, coll_tovar3, name_tovar3, coll_tovar4, name_tovar4,
                                        summ, price_deliver1, current_month, current_day, cash_card, user_id))
                        conn.commit()
                        conn.close()
                        key_city = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="Добавить еще ✅", callback_data='dev_true_')],
                            [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                        ])
                        await bot.send_message(user_id, "Данные успешно добавлены.", reply_markup=key_city)
                        await bot.delete_message(user_id, message.message_id)
                    else:
                        key_city = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="Выйти в меню ❌", callback_data='menu_return_')]
                        ])
                        await bot.send_message(user_id, "У вас недостаточно товара.", reply_markup=key_city)
                        await bot.delete_message(user_id, message.message_id)
    except Exception as e:
        print(e)
