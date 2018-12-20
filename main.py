from aiogram.dispatcher import Dispatcher
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils import markdown as md
import keyboards as kb
import pattern_message as pm
from config import token
import os
import pickle
import json


bot = Bot(token=token, parse_mode=types.ParseMode.MARKDOWN)
dp = Dispatcher(bot)

about_user = dict()

def add_prj_value(user_id, date, about_user):



    about_user[user_id] = str(date)
    # with open('user_id_logs.txt', 'at', encoding='utf-8'):
    #     json.dump(about_user)
    #
    # with open('data.txt', 'w', encoding='utf-8') as dt:
    #     pickle.dump(about_user, dt)
    # print(about_user)
    json.dump(about_user,  open('user_id_logs.txt', 'at', encoding='utf-8'))





@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await bot.send_message(message.from_user.id, pm.privetstvie, reply_markup=kb.job_conditions)

    add_prj_value(message.from_user.id, message.date, about_user)

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await bot.send_message(message.from_user.id, pm.help, reply_markup=kb.vopros)
    add_prj_value(message.from_user.id, message.date, about_user)


@dp.callback_query_handler(lambda c: c.data)
async def j_conditions(callback_query: types.CallbackQuery):

    code = callback_query.data[0:]
    if code == 'read_conditions':
        await bot.send_message(callback_query.from_user.id, pm.vac_infa_jooble)
        await bot.send_message(callback_query.from_user.id, pm.vac_infa_jooble1, reply_markup=kb.jc_sostojanie)

    if code == 'jc_vse_ok':
        await bot.send_message(callback_query.from_user.id, pm.vac_infa_jooble2, reply_markup=kb.jc1_sostojanie)

    if code == 'jc1_vse_ok':
        await bot.send_message(callback_query.from_user.id, pm.vac_infa_jooble3)
        await bot.send_message(callback_query.from_user.id, pm.vac_infa_jooble4, reply_markup=kb.jc2_sostojanie)


    if code == 'jc1_ne_ok':
        await bot.send_message(callback_query.from_user.id, pm.yslovie_ne_ok)

    if code == 'zadat_vopros':
        await bot.send_message(callback_query.from_user.id, pm.vac_infa_jooble3)
        await bot.send_message(callback_query.from_user.id, pm.vac_infa_jooble4, reply_markup=kb.jc2_sostojanie)

    if code == 'anketa':
        await bot.send_message(callback_query.from_user.id, pm.anketa)

    # j = callback_query.as_json()
    # sdfg


    add_prj_value(callback_query.from_user.id, callback_query.message.date, about_user)


    print(about_user)



if __name__ == '__main__':
    executor.start_polling(dp)

    os.chdir(os.path.dirname(__file__))
