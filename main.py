import asyncio
import logging
import sys
import sqlite3
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.types import (Message,
                           InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery)
from config.config import TOKEN
from handlers.menu_delivery import menu_delivery_return, menu_delivery
from handlers.delivery_add import (delivery_add, delivery_add_end, dev_menu,delivery_add_day,delivery_add_month
                                   , delivery_add_day_end, delivery_add_sms_end)
from aiogram import F
from utils.state import Delivery_add, Admin, Cura_add, Cura_tovar, Admin_cura, Edit_deliver, Tovar_cura
from handlers.check_tovar import check_and_send_messages, delete_users, delete_message
from handlers_admin.admin_cura import (cura_set_menu, cura_show_set, cura_set_add_end, cura_set_add_name,
                                       cura_set_add_external, del_cura_end, del_cura_set )
from handlers_admin.admin_oper_stats import (stats_oper_weeks_in_month, stats_oper_month_month, stats_oper_delivery_week,
                                             stats_oper_day_end, stats_oper_day_day, stats_oper_day_month,
                                             stats_oper_month_end,stats_oper_week_end,stats_oper_week_month,
                                             stats_admin_oper)
from handlers_admin.admin_edit_delivery import (edit_cura_set,edit_name_cura_end, edit_price_deliver_end,edit_price_deliver_center,
                                                edit_day_end, edit_address_end, edit_address_center, edit_number_end,
                                                edit_month_end, edit_month_center, edit_number_center, edit_day_center,
                                                edit_coll_tovar_end, edit_name_tovar_end, edit_name_tovar_center,
                                                edit_cash_card_end, edit_cash_card_center, edit_price_shop_end,
                                                edit_coll_tovar_center, edit_price_shop_center)
from handlers_admin.menu_admin import admin_menu, admin_menu_return
from handlers_admin.admin_stats import (stats_admin_menu, stats_admin_shop, stats_shop_day_day, stats_shop_day_end,
                                        stats_shop_day_month, stats_weeks_in_month, stats_shop_week_month ,
                                        stats_delivery_week, stats_delivery_week_end, stats_shop_month_end,
                                        stats_shop_month_month, stats_admin_cura,
                                        )
from handlers_admin.admin_cura_stats import (stats_cura_name_day,  delivery_analys_month,
                                        delivery_analys_end, delivery_analys_day, delivery_week,
                                        stats_cura_name_week,delivery_week_end, delivery_analys_month_week,
                                        stats_analys_month, stats_cura_month_end, stats_cura_name_month)
from handlers_admin.admin_delivery import (add_delivery_name_cura, dev_admin_menu, del_delivery_name_cura,
                                           del_delivery_day, del_delivery_center, del_delivery_month,
                                           del_delivery_end, del_delivery_mid, show_delivery_end, show_delivery_day
                                           , show_delivery_mid, show_delivery_month,
                                           edit_delivery_day, edit_delivery_mid
                                           ,edit_delivery_month, edit_delivery_center,show_delivery_name_cura)
from handlers_admin.admin_set import (admin_set_menu, admin_show_set, admin_set_add_end, admin_set_add_external,
                                      admin_set_add_name, del_admin_set, del_admin_end)

from handlers_admin.tovar_cura import (cura_tovar_menu, cura_tovar_add, cura_tovar_add_end, cura_name_add,
                                       cura_show_tovar, cura_show_tovar_end, cura_del_tovar_end, cura_del_tovar
                                       , cura_del_name, cura_name_edit, cura_tovar_edit, cura_end_edit, cura_mid_edit)

logging.basicConfig(level=logging.INFO)

conn = sqlite3.connect('shop.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS data_shop(
                           id INTEGER PRIMARY KEY,
                           number_delivery TEXT,
                           adress_delivery TEXT,
                           coll_tovar TEXT DEFAULT 0,
                           name_tovar TEXT,
                           coll_tovar_tho TEXT DEFAULT 0,
                           name_tovar_tho TEXT,
                           coll_tovar_three TEXT DEFAULT 0,
                           name_tovar_three TEXT,
                           coll_tovar_four TEXT DEFAULT 0,
                           name_tovar_four TEXT,
                           price_shop TEXT,
                           price_deliver TEXT,
                           data_create TEXT,
                           data_day TEXT,
                           cash_card TEXT,
                           external_id TEXT
                       )''')
conn.commit()
conn.close()

conn = sqlite3.connect('shop.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS admin(
                           id INTEGER PRIMARY KEY,
                           name_admin TEXT,
                           external_admin TEXT
                       )''')
conn.commit()
conn.close()

conn = sqlite3.connect('shop.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS cura(
                           id INTEGER PRIMARY KEY,
                           name_admin TEXT,
                           external_admin TEXT
                       )''')
conn.commit()
conn.close()

conn = sqlite3.connect('shop.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS cura_tovar(
                           id INTEGER PRIMARY KEY,
                           external_cura TEXT,
                           name_item TEXT,
                           coll_tovar TEXT
                       )''')
conn.commit()
conn.close()


async def start():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.add_job(check_and_send_messages, trigger='interval', seconds=1600,
                      kwargs=({'bot': bot}))
    scheduler.start()
    dp.message.register(menu_delivery, CommandStart())
    dp.message.register(admin_menu, Command("admin"))

    dp.callback_query.register(dev_menu, F.data.startswith("dev_add"))

    dp.callback_query.register(menu_delivery_return, F.data.startswith("menu_return_"))
    dp.callback_query.register(delivery_add, F.data.startswith("dev_true_"))

    dp.message.register(delivery_add_end, Delivery_add.delivery_text)

    dp.callback_query.register(admin_set_add_name, F.data.startswith("add_admin_set_"))
    dp.callback_query.register(del_admin_set, F.data.startswith("del_admin_set_"))
    dp.callback_query.register(del_admin_end, F.data.startswith("_admin_del_"))

    dp.callback_query.register(admin_show_set, F.data.startswith("show_admin_set_"))
    dp.message.register(admin_set_add_external, Admin.admin_name)
    dp.message.register(admin_set_add_end, Admin.admin_id)
    dp.callback_query.register(admin_menu_return, F.data.startswith("admin_return_"))
    dp.callback_query.register(admin_set_menu, F.data.startswith("admin_set_"))

    dp.callback_query.register(cura_set_add_name, F.data.startswith("add_cura_set_"))
    dp.callback_query.register(del_cura_set, F.data.startswith("del_cura_set_"))
    dp.callback_query.register(del_cura_end, F.data.startswith("_cura_del_"))
    dp.callback_query.register(cura_show_set, F.data.startswith("show_cura_set_"))
    dp.message.register(cura_set_add_external, Cura_add.cura_name)
    dp.message.register(cura_set_add_end, Cura_add.cura_external)
    dp.callback_query.register(cura_set_menu, F.data.startswith("cura_set_"))

    dp.callback_query.register(delivery_add_month, F.data.startswith("delivery_data_"))
    dp.callback_query.register(delivery_add_day, F.data.startswith("delivery_month_"))
    dp.callback_query.register(delivery_add_sms_end, F.data.startswith("delivery_day_"))
    dp.message.register(delivery_add_day_end, Delivery_add.delivery_day)
    dp.callback_query.register(delivery_analys_month_week, F.data.startswith("week_cura_"))
    dp.callback_query.register(delivery_week, F.data.startswith("week_delivery_"))
    dp.callback_query.register(delivery_week_end, F.data.startswith("week_end_"))
    dp.callback_query.register(delivery_analys_month, F.data.startswith("ex_cura_"))
    dp.callback_query.register(delivery_analys_day, F.data.startswith("month_delivery_"))
    dp.callback_query.register(delivery_analys_end, F.data.startswith("day_delivery_"))

    dp.callback_query.register(cura_tovar_menu, F.data.startswith("tovar_set"))
    dp.callback_query.register(cura_name_add, F.data.startswith("add_tovar_cura_"))
    dp.callback_query.register(cura_tovar_add, F.data.startswith("cura_name_"))
    dp.message.register(cura_tovar_add_end, Cura_tovar.name_tovar)

    dp.callback_query.register(cura_show_tovar, F.data.startswith("show_tovar_cura_"))
    dp.callback_query.register(cura_show_tovar_end, F.data.startswith("cura_showtovar_"))

    dp.callback_query.register(cura_del_name, F.data.startswith("del_tovar_cura_"))
    dp.callback_query.register(cura_del_tovar, F.data.startswith("cura_del_"))
    dp.callback_query.register(cura_del_tovar_end, F.data.startswith("tovar_del_"))


    dp.callback_query.register(dev_admin_menu, F.data.startswith("delivery_set"))
    dp.callback_query.register(add_delivery_name_cura, F.data.startswith("add_admin_delivery_"))

    dp.callback_query.register(del_delivery_name_cura, F.data.startswith("del_admin_delivery_"))
    dp.callback_query.register(del_delivery_month, F.data.startswith("_del_namecura_"))
    dp.callback_query.register(del_delivery_day, F.data.startswith("month_set_"))
    dp.callback_query.register(del_delivery_mid, F.data.startswith("day_set_"))
    dp.callback_query.register(del_delivery_center, F.data.startswith("del_dev_end_"))
    dp.callback_query.register(del_delivery_end, F.data.startswith("del_dev_yes_"))

    dp.callback_query.register(show_delivery_name_cura, F.data.startswith("show_admin_delivery_"))
    dp.callback_query.register(show_delivery_month, F.data.startswith("_show_namecura_"))
    dp.callback_query.register(show_delivery_day, F.data.startswith("month_show_"))
    dp.callback_query.register(show_delivery_mid, F.data.startswith("day_show_"))
    dp.callback_query.register(show_delivery_end, F.data.startswith("show_dev_end_"))

    dp.callback_query.register(stats_admin_menu, F.data.startswith("admin_stats"))
    dp.callback_query.register(stats_admin_shop, F.data.startswith("stats_shop_menu"))
    dp.callback_query.register(stats_shop_day_month, F.data.startswith("stats_shop_day"))
    dp.callback_query.register(stats_shop_day_day, F.data.startswith("month_shop_"))
    dp.callback_query.register(stats_shop_day_end, F.data.startswith("day_shop_"))

    dp.callback_query.register(stats_shop_week_month, F.data.startswith("stats_shop_week"))
    dp.callback_query.register(stats_delivery_week, F.data.startswith("month_week_"))
    dp.callback_query.register(stats_delivery_week_end, F.data.startswith("statsweek_end_"))

    dp.callback_query.register(stats_shop_month_month, F.data.startswith("stats_shop_month"))
    dp.callback_query.register(stats_shop_month_end, F.data.startswith("month_month_"))


    dp.callback_query.register(stats_cura_name_day, F.data.startswith("stats_cura_day"))
    dp.callback_query.register(stats_admin_cura, F.data.startswith("stats_cura_menu"))

    dp.callback_query.register(stats_cura_name_week, F.data.startswith("stats_cura_week"))

    dp.callback_query.register(stats_cura_name_month, F.data.startswith("stats_cura_month"))
    dp.callback_query.register(stats_analys_month, F.data.startswith("month_cura_"))
    dp.callback_query.register(stats_cura_month_end, F.data.startswith("ends_delivery_"))


    dp.callback_query.register(stats_oper_day_month, F.data.startswith("stats_oper_day"))
    dp.callback_query.register(stats_oper_day_day, F.data.startswith("month_oper_"))
    dp.callback_query.register(stats_oper_day_end, F.data.startswith("day_oper_"))

    dp.callback_query.register(stats_oper_week_month, F.data.startswith("stats_oper_week"))
    dp.callback_query.register(stats_oper_delivery_week, F.data.startswith("oper_week_"))
    dp.callback_query.register(stats_oper_week_end, F.data.startswith("statsoper_end_"))

    dp.callback_query.register(stats_oper_month_month, F.data.startswith("stats_oper_month"))
    dp.callback_query.register(stats_oper_month_end, F.data.startswith("oper_month_"))

    dp.callback_query.register(stats_admin_oper, F.data.startswith("stats_oper_menu"))

    dp.callback_query.register(edit_delivery_month, F.data.startswith("edit_admin_delivery_"))
    dp.callback_query.register(edit_delivery_day, F.data.startswith("edit_dev_"))
    dp.callback_query.register(edit_delivery_mid, F.data.startswith("day_edit_"))
    dp.callback_query.register(edit_delivery_center, F.data.startswith("edit_edit_end_"))

    dp.callback_query.register(edit_month_center, F.data.startswith("edit_month_end_"))
    dp.message.register(edit_month_end, Edit_deliver.month)
    dp.callback_query.register(edit_day_center, F.data.startswith("edit_day_end_"))
    dp.message.register(edit_day_end, Edit_deliver.day)
    dp.callback_query.register(edit_number_center, F.data.startswith("edit_number_end_"))
    dp.message.register(edit_number_end, Edit_deliver.number_delivery)
    dp.callback_query.register(edit_address_center, F.data.startswith("edit_address_end_"))
    dp.message.register(edit_address_end, Edit_deliver.adress_delivery)
    dp.callback_query.register(edit_coll_tovar_center, F.data.startswith("edit_coll_tovar_end_"))
    dp.message.register(edit_coll_tovar_end, Edit_deliver.coll_tovar)
    dp.callback_query.register(edit_name_tovar_center, F.data.startswith("edit_name_tovar_end_"))
    dp.message.register(edit_name_tovar_end, Edit_deliver.name_tovar)
    dp.callback_query.register(edit_price_shop_center, F.data.startswith("edit_price_shop_end_"))
    dp.message.register(edit_price_shop_end, Edit_deliver.price_shop)
    dp.callback_query.register(edit_price_deliver_center, F.data.startswith("edit_price_deliver_end_"))
    dp.message.register(edit_price_deliver_end, Edit_deliver.price_deliver)
    dp.callback_query.register(edit_cash_card_center, F.data.startswith("edit_cash_card_end_"))
    dp.message.register(edit_cash_card_end, Edit_deliver.cash_card)
    dp.callback_query.register(edit_cura_set, F.data.startswith("edit_name_cura_end_"))
    dp.callback_query.register(edit_name_cura_end, F.data.startswith("edit_cura_end_"))
    dp.callback_query.register(delete_message, F.data.startswith("delete_message"))
    dp.callback_query.register(delete_users, F.data.startswith("delete_users_"))

    dp.callback_query.register(cura_name_edit, F.data.startswith("redit_tovar_cura_"))
    dp.callback_query.register(cura_tovar_edit, F.data.startswith("cura_edit_edit_"))
    dp.callback_query.register(cura_mid_edit, F.data.startswith("cura_tovar_edit_"))
    dp.message.register(cura_end_edit, Tovar_cura.tovar_cura)




















    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
