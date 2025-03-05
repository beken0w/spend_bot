import os
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import Bot, F, Router
from dotenv import load_dotenv
from FSM.Category_class import Category
from FSM.Spend_class import Spend
from aiogram.fsm.context import FSMContext


obj_cat = Category()
obj_spd = Spend()

from keyboards.inline_kb import welcome_kb, delete_message_kb

router1 = Router()

load_dotenv()

MY_ID = os.getenv("MY_ID")

async def start_bot(bot: Bot):
    await bot.send_message(MY_ID, "Bot is running",
                           reply_markup=delete_message_kb())

async def stop_bot(bot: Bot):
    await bot.send_message(MY_ID, "Bot stopped",
                           reply_markup=delete_message_kb())

@router1.message(CommandStart())
async def welcome0(message: Message):
    await message.delete()
    user_id = message.from_user.id
    try: is_exist = obj_cat.is_exist_by_title({"user_id": user_id, "title" : 'Unallocated'})
    except: pass

    if is_exist == -1:
        try: obj_cat.insert_category({"user_id": user_id, "title" : 'Unallocated'})
        except: pass
    await message.answer(f"Hi, {message.from_user.first_name}",
                         reply_markup=welcome_kb())

  
@router1.callback_query(F.data == "main_menu")
async def welcome_2(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    chat_id = callback.message.chat.id
    try: await bot.delete_messages(chat_id=chat_id, message_ids=data['msg_list'][:-1])
    except: pass
    await callback.answer()
    await state.clear()
    await callback.message.edit_text('[ Main menu ]', reply_markup=welcome_kb())
    

@router1.message(Command("menu"))
async def welcome1(message: Message, state: FSMContext, bot: Bot):
    await message.delete()
    data = await state.get_data()
    chat_id = message.chat.id
    try: await bot.delete_messages(chat_id=chat_id, message_ids=data['msg_list'][:-1])
    except: pass
    await state.clear()
    await message.answer(f"[ Main menu ]", reply_markup=welcome_kb())


@router1.message(Command("admstatusers"))
async def welcome1(message: Message):
    await message.delete()
    res = obj_spd.admstatusers()
    if message.from_user.id == int(MY_ID):
        await message.answer(f"```---------------------\n{res}```", 
                            parse_mode="MarkdownV2",
                            reply_markup=delete_message_kb())
