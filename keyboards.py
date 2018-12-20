from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, types


# sostojanie = ReplyKeyboardMarkup()
sostojanie = InlineKeyboardMarkup(row_width=2)
vse_ok = InlineKeyboardButton('Все понятно', callback_data='vse_ok')
# vse_ok = KeyboardButton('Все понятно')
# zadat_vopros = KeyboardButton('Задать вопрос')

zadat_vopros = types.InlineKeyboardButton(text='Задать вопрос', url='https://t.me/meoweff')
sostojanie.add(vse_ok, zadat_vopros)



#Задать вопрос
vopros = InlineKeyboardMarkup(row_width=1)
vopros.add(zadat_vopros)


#Условия работы
job_conditions = InlineKeyboardMarkup(row_width=1)
read_conditions = InlineKeyboardButton('Ознакомиться с условиями', callback_data='read_conditions')
job_conditions.add(read_conditions, zadat_vopros)

jc_sostojanie = InlineKeyboardMarkup(row_width=1)
jc_vse_ok = InlineKeyboardButton('Все понятно', callback_data='jc_vse_ok')
#zadat_vopros = InlineKeyboardButton('Задать вопрос', callback_data='zadat_vopros')
jc_sostojanie.add(jc_vse_ok, zadat_vopros)

jc1_sostojanie = InlineKeyboardMarkup(row_width=1)
jc1_vse_ok = InlineKeyboardButton('Да, времени будет достаточно', callback_data='jc1_vse_ok')
jc1_ne_ok = InlineKeyboardButton('К сожалению, времени будет не достаточно', callback_data='jc1_ne_ok')
#zadat_vopros = InlineKeyboardButton('Задать вопрос', callback_data='zadat_vopros')
jc1_sostojanie.add(jc1_vse_ok, jc1_ne_ok, zadat_vopros)

jc2_sostojanie = InlineKeyboardMarkup(row_width=1)
anketa = InlineKeyboardButton('Пройти анкетирование', callback_data='anketa')
jc2_ne_interesno = InlineKeyboardButton('Мне не интересна эта работа', callback_data='jc1_ne_ok')
#zadat_vopros = InlineKeyboardButton('Задать вопрос', callback_data='zadat_vopros')
jc2_sostojanie.add(anketa, jc2_ne_interesno, zadat_vopros)





