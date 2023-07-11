import aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup
import json
from aiogram.contrib.fsm_storage.memory import MemoryStorage


class ConvertStates(StatesGroup):
    ENTER_AMOUNT = State()  
    SELECT_FROM = State()  
    SELECT_TO = State() 


currency_rates = {
    'USD': {'EUR': 0.85, 'GBP': 0.75, 'JPY': 110.28, 'UAH': 26.90},
    'EUR': {'USD': 1.18, 'GBP': 0.88, 'JPY': 129.92, 'UAH': 31.91},
    'GBP': {'USD': 1.34, 'EUR': 1.14, 'JPY': 146.74, 'UAH': 36.61},
    'JPY': {'USD': 0.0091, 'EUR': 0.0077, 'GBP': 0.0068, 'UAH': 0.25},
    'UAH': {'USD': 0.037, 'EUR': 0.031, 'GBP': 0.027, 'JPY': 3.97}
}

def get_bot_token():
    with open('config.json', 'r') as file:
        data = json.load(file)
        return data.get('bot_token')


bot_token = get_bot_token()
bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
gif_path_on_end = '98mU.gif'
gif_path_on_start = '9co1.gif'
@dp.message_handler(Command('start'))
async def start(message: types.Message):
    await send_gif(message,gif_path_on_start)
    await message.reply('🇺🇦Привіт! Введи суму для конвертації,🇺🇸Hello! enter your sum for converting')
    await ConvertStates.ENTER_AMOUNT.set()
    
async def send_gif(message,gif_path):
    with open(gif_path, 'rb') as gif_file: 
       await bot.send_animation(message.chat.id, animation=gif_file)




@dp.message_handler(lambda message: str(message.text).replace(',', "").isdigit(),state=ConvertStates.ENTER_AMOUNT)
async def enter_amount(message: types.Message, state: FSMContext):
    amount = float(message.text.replace(',', "."))
    await state.update_data(amount=amount)
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(*currency_rates.keys())  
    await message.reply('🇺🇦Вибери початкову валюту,🇺🇸Choose initial currency:', reply_markup=markup)
    await ConvertStates.SELECT_FROM.set()

@dp.message_handler(lambda message: message.text in currency_rates.keys(), state=ConvertStates.SELECT_FROM)
async def select_from(message: types.Message, state: FSMContext):
    from_currency = message.text
    await state.update_data(from_currency=from_currency)
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(*currency_rates.keys())  
    await message.reply('🇺🇦Вибери цільову валюту,🇺🇸Choose target currency :', reply_markup=markup)
    await ConvertStates.SELECT_TO.set()


@dp.message_handler(lambda message: message.text in currency_rates.keys(), state=ConvertStates.SELECT_TO)
async def select_to(message: types.Message, state: FSMContext):
    to_currency = message.text
    await state.update_data(to_currency=to_currency)
    data = await state.get_data()
    amount = data['amount']
    from_currency = data['from_currency']
    to_currency = data['to_currency']
    result = convert_currency(amount, from_currency, to_currency)
    await message.reply(f'🇺🇦Результат,🇺🇸Result: {result} {to_currency}')
    await send_gif(message,gif_path_on_end)
    await message.reply('🇺🇦Введи нову суму або натисни /cancel, щоб завершити,🇺🇸Enter the new amount or press cancel to finish ', reply_markup=types.ReplyKeyboardRemove())
    

    await ConvertStates.ENTER_AMOUNT.set()


@dp.message_handler(Command('cancel'), state='*')
async def cancel_operation(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply('Операція скасована.')

def convert_currency(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return amount
    if from_currency in currency_rates and to_currency in currency_rates[from_currency]:
        rate = currency_rates[from_currency][to_currency]
        return round(amount * rate, 2)
    return None  


if __name__ == '__main__':
    aiogram.executor.start_polling(dp)





