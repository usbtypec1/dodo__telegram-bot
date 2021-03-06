from typing import TypeAlias, TypedDict

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

__all__ = (
    'Response',
    'ResponseDict',
    'ReplyMarkup',
)

ReplyMarkup: TypeAlias = InlineKeyboardMarkup | ReplyKeyboardMarkup


class ResponseDict(TypedDict):
    text: str | None
    reply_markup: ReplyMarkup | None


class Response:

    def get_text(self) -> str | None:
        pass

    def get_reply_markup(self) -> ReplyMarkup | None:
        pass

    def as_dict(self) -> ResponseDict:
        return {
            'text': self.get_text(),
            'reply_markup': self.get_reply_markup(),
        }
