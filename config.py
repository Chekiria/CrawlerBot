from enum import Enum

token = '714252269:AAGvSijDbZryw3MP3ZkfwYgbBOP0e8WtIh4'


class State(Enum):
    '''этапы прохождения юзером бота (в последующем залить в БД'''
# State = {
    S_VAKANCIJA = '0'
    S_ANKETA = '1'
    S_NAME = '2'
    S_SURNAME = '3'
    S_EMAIL = '3'
