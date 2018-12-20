from aiogram.dispatcher import Dispatcher
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils import markdown as md
import keyboards as kb
import pattern_message as pm
from config import token, State
import os
import pickle
import json
import logging

bot = Bot(token=token, parse_mode=types.ParseMode.MARKDOWN)
dp = Dispatcher(bot)
# logging.basicConfig(level=logging.INFO)

# users = dict() #словарь всех юзеров
with open('user_id_logs.txt', 'r', encoding='utf-8') as f:
    about_user = json.load(f)
# about_user = dict() # словарь логов по конкретному юзеру


def add_prj_value(user_id, date, State, about_user):
    user_id = str(user_id)
    if user_id in about_user.keys():
        about_user[user_id]['dt'] = str(date)
        about_user[user_id]['st'] = str(State)

    else:
        about_user[user_id] = {}
        about_user[user_id]['dt'] = str(date)
        about_user[user_id]['st'] = str(State)

    #     if date in users[about_user]:
    #
    #     about_user[user_id].append(str(date))
    #     about_user[user_id].append(State)
    #     print(about_user)
    #
    # else:
    #
    #     user_id[user_id] = str(date)
    #     user_id[user_id].append(State)



    # about_user[user_id] = str(date)

    json.dump(about_user,  open('user_id_logs.txt', 'wt', encoding='utf-8'))


# def add_prj_value(prj_value, project):
#     if prj_value[2] in project.keys():
#         if prj_value[0] in project[prj_value[2]]:
#             # append the new number to the existing array at this slot
#             if prj_value[1] not in project[prj_value[2]][prj_value[0]]:
#                 project[prj_value[2]][prj_value[0]].append(prj_value[1])
#         else:
#             # create a new array in this slot
#             project[prj_value[2]][prj_value[0]] = [prj_value[1]]
#     else:
#         project[prj_value[2]] = {}
#         project[prj_value[2]][prj_value[0]] = [prj_value[1]]








@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await bot.send_message(message.from_user.id, pm.privetstvie, reply_markup=kb.job_conditions)
    # await message.reply('Привет', reply_markup=kb.sostojanie)

    add_prj_value(message.from_user.id, message.date, State.S_VAKANCIJA.value, about_user)

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await bot.send_message(message.from_user.id, pm.help, reply_markup=kb.vopros)
    add_prj_value(message.from_user.id, message.date, State, about_user)


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
        add_prj_value(callback_query.from_user.id, callback_query.message.date, State.S_ANKETA.value, about_user)

    # j = callback_query.as_json()
    # sdfg


    # add_prj_value(callback_query.from_user.id, callback_query.message.date, State.S_VAKANCIJA.value, about_user)


    print(about_user)



if __name__ == '__main__':
    executor.start_polling(dp)

    os.chdir(os.path.dirname(__file__))
