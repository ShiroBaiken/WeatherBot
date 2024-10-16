from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class LocationsId(CallbackData, prefix="p_id"):
    id: str


def generate_locations_reply_keyboard(locations: list[tuple]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for name, id in locations:
        builder.button(text=name, callback_data=LocationsId(id=id).pack())
    builder.adjust(3)
    return builder.as_markup()
