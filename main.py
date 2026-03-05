import asyncio
import random
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

games = {}


def check_winner(board):
    wins = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]
    for combo in wins:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != " ":
            return board[combo[0]]
    if " " not in board:
        return "draw"
    return None


def get_keyboard(board):
    buttons = []
    for i in range(0, 9, 3):
        row = []
        for j in range(3):
            index = i + j
            text = board[index] if board[index] != " " else "⬜"
            row.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"move:{index}"
                )
            )
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def bot_move(board):
    empty = [i for i, v in enumerate(board) if v == " "]
    if empty:
        return random.choice(empty)
    return None


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "❌⭕ X O o'yini (Botga qarshi)\n"
        "Siz: ❌\nBot: ⭕\n\n"
        "Boshlash: /game"
    )


@dp.message(Command("game"))
async def game(message: Message):
    games[message.from_user.id] = [" "] * 9
    await message.answer(
        "O'yin boshlandi! Siz boshlaysiz ❌",
        reply_markup=get_keyboard(games[message.from_user.id])
    )


@dp.callback_query(F.data.startswith("move"))
async def move(callback: CallbackQuery):
    user_id = callback.from_user.id

    if user_id not in games:
        await callback.answer("Avval /game bosing!", show_alert=True)
        return

    index = int(callback.data.split(":")[1])
    board = games[user_id]

    if board[index] != " ":
        await callback.answer("Bu joy band!", show_alert=True)
        return

    # Foydalanuvchi yurishi
    board[index] = "X"

    winner = check_winner(board)
    if winner:
        await finish_game(callback, board, winner, user_id)
        return

    # Bot yurishi
    bot_index = bot_move(board)
    if bot_index is not None:
        board[bot_index] = "O"

    winner = check_winner(board)
    if winner:
        await finish_game(callback, board, winner, user_id)
        return

    await callback.message.edit_reply_markup(
        reply_markup=get_keyboard(board)
    )
    await callback.answer()


async def finish_game(callback, board, winner, user_id):
    if winner == "draw":
        text = "🤝 Durrang!"
    elif winner == "X":
        text = "🎉 Siz yutdingiz!"
    else:
        text = "🤖 Bot yutdi!"

    await callback.message.edit_text(
        text,
        reply_markup=get_keyboard(board)
    )
    del games[user_id]
    await callback.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

print('fdsfdsfds')