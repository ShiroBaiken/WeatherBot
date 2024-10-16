from __future__ import annotations

import os
import re
from typing import Any

import goslate
import asyncio

from aiogram import Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram import F

from weather_bot import Weather
from reply_keyboard import LocationsId, generate_locations_reply_keyboard

wbot = Weather(bot_key=os.environ['BOT_TOKEN'], weather_api_key=os.environ['WEATHER_TOKEN'], parse_mode='html')
dp = Dispatcher(disable_fsm=True)
rt = Router()
gs = goslate.Goslate()


def has_cyrillic(text: str) -> bool:
    return bool(re.search('[\u0400-\u04FF]', text))


def translate(message: str) -> tuple[str | Any, str]:
    city_name = ''
    is_successful = 'success'
    try:
        if has_cyrillic(message) is True:
            city_name = gs.translate(message, target_language='en')
        else:
            city_name = message
    except Exception as e:
        is_successful = e.__repr__()
    return city_name, is_successful


@rt.message(CommandStart())
async def greeting(message: Message):
    await message.answer("Hello this is simple forecast bot. \nEnter your city name below")


@rt.message()
async def weather_for_city(message: Message):
    city_name, result = translate(message.text)
    if result != 'success':
        await message.answer('Translation service temporaly unavailible \n'
                             'Try again later or type city name in english')
    data, flag = wbot.get_weather_for_city(city_name.lower())
    if flag == 'weather':
        current = data['current']
        await message.answer(f'Weather in city: {message.text} \n'
                             f'Temperature: {current["temperature"]} *C \n'
                             f'Wind: {current["wind"]["dir"]} {current["wind"]["speed"]} m/s \n'
                             f'{current["icon"]}')

    elif flag == 'locations' and type(data) == 'list':
        locations_names = [(x['name'], x['place_id']) for x in data]
        locations_keyboard = generate_locations_reply_keyboard(locations_names)
        await message.answer(f"We cannot find exact location you entered. Did you mentioned one from list below?",
                             reply_markup=locations_keyboard)
    elif not message or type(data) != list or not data:
        await message.answer("Weather forecast is not available for your city, did you enter name correct?")


@rt.callback_query(LocationsId.filter(F.id))
async def chosen_location_reply(callback: CallbackQuery):
    id = LocationsId.unpack(callback.data).id
    data, _ = wbot.get_weather_for_city(location=id)
    current = data['current']
    await wbot.send_message(chat_id=callback.from_user.id, text=f'Weather in city: {id} \n'
                                                                f'Temperature: {current["temperature"]} *C \n'
                                                                f'Wind: {current["wind"]["dir"]} {current["wind"]["speed"]} m/s \n'
                                                                f'{current["icon"]}')


async def main():
    dp.include_router(rt)

    await dp.start_polling(wbot)


if __name__ == '__main__':
    asyncio.run(main())
