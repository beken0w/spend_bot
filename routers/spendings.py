from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext

from keyboards.inline_kb import delete_change_kb, cancel_kb, add_cat
from FSM.Spend_class import Spend
from FSM.Category_class import Category
from FSM.states import New_spend, Upd_spend

router_spd = Router()
obj_spend = Spend()
obj_cat   = Category()


@router_spd.callback_query(F.data == "last_5_spend")
async def last_5_spend(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    await state.set_state(New_spend.category)
    try: spendings = obj_spend.select_last_5_spend({"user_id":user_id})
    except: pass
    if spendings != -1:
        await callback.answer()
        await callback.message.delete()
        msg_list = []
        for rec in spendings:
            msg = await callback.message.answer(
                    rec[1], 
                    reply_markup=delete_change_kb('spd', rec[0]))
            msg_list.append(msg.message_id)
        msg = await callback.message.answer('🔝 Spendings', 
                                        reply_markup=cancel_kb())
        msg_list.append(msg.message_id) 
        await state.update_data(msg_list=msg_list)
    else:
        await callback.answer("❗ No records", cache_time=5)


@router_spd.callback_query(F.data == "new_spend")
async def new_spd_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.delete()
    user_id = callback.from_user.id
    await state.update_data(user_id=user_id)
    await state.set_state(New_spend.category)
    try: categories = obj_cat.select_categories(user_id)
    except: pass
    msg = await callback.message.answer('⬇️ Choose category', 
                                            reply_markup=add_cat(categories))
    await state.update_data(msg_id=msg.message_id)


@router_spd.callback_query(F.data.startswith("add_cat|"))
async def new_spd_2(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    category_id = str(callback.data).replace('add_cat|', '')
    data = await state.get_data()
    user_id = callback.from_user.id
    try: title = obj_cat.get_title({"user_id":user_id, "id":category_id})
    except: pass
    await state.update_data(title=title)    
    await state.update_data(category_id=category_id)
    await state.set_state(New_spend.amount)
    await callback.message.edit_text(f'✔️ Category: {title}\n\n⬇️ Add amount', 
                                     reply_markup=cancel_kb(True))

@router_spd.message(New_spend.amount)
async def new_spd_3(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    user_id = message.from_user.id
    await message.bot.delete_message(chat_id=user_id, 
                                     message_id=data['msg_id'])
    amt = message.text
    try: amt = int(amt) 
    except: amt = -1

    if amt < 0:
        await state.set_state(New_spend.amount)
        msg = await message.answer(f"✔️ Category: {data['title']} \n\n"\
                                    "⬇️ Incorrect amount, please repeat"
                                    , reply_markup=cancel_kb(True))
        await state.update_data(msg_id=msg.message_id)
    else:
        await state.update_data(amount=amt)
        await state.set_state(New_spend.desc)
        msg = await message.answer(f"✔️ Category: {data['title']}\n"+
                                   f"✔️ Amount: {amt}\n"+
                                    "☐ Description: \n\n"+
                                    "⬇️ Enter new Description"
                                  ,reply_markup=cancel_kb(True))
        await state.update_data(msg_id=msg.message_id)


@router_spd.message(New_spend.desc)
async def new_spd_4(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(descs=message.text)
    user_id = message.from_user.id
    data = await state.get_data()
    try: obj_spend.insert_spend(data)
    except: pass
    await message.bot.delete_message(chat_id=user_id, 
                                     message_id=data['msg_id'])
    await message.answer(f"✔️ Category: {data['title']}\n"+
                         f"✔️ Amount: {data['amount']}\n"+
                         f"✔️ Description: {data['descs']}\n\n"+
                         "✅ Record created successfully",
                        reply_markup=cancel_kb(title=True, after_new=True))
    await state.clear()

@router_spd.callback_query(F.data.startswith("del|spd|"))
async def del_spd_1(callback: CallbackQuery):
    id = str(callback.data).replace('del|spd|', '')
    user_id = callback.from_user.id
    try: is_exist = obj_spend.is_exist_by_id({'user_id':user_id, 'id': id})
    except: pass
    if is_exist == -1:
        await callback.answer('❗ This record doesn`t exist', cache_time=5)
    else:
        try: obj_spend.delete_spend({'user_id':user_id, 'id': id})
        except: pass
        await callback.answer('✅ Record removed successfully', cache_time=5) 
    await callback.message.delete()

@router_spd.callback_query(F.data.startswith("chge|spd|"))
async def chge_spd_1(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user_id = callback.from_user.id
    try:
        await bot.delete_messages(chat_id=user_id, 
                                  message_ids=data['msg_list'])
    except:
        pass
    await state.clear()
    
    id = str(callback.data).replace('chge|spd|', '')
    try: is_exist = obj_spend.is_exist_by_id({'user_id':user_id, 'id': id})
    except: pass
    if is_exist == -1:
        await callback.message.delete()
        await callback.answer('❗ This record doesn`t exist', cache_time=5)
    else:        
        await callback.answer()
        try: info = obj_spend.select_spend_by_id(id)
        except: pass
        await state.update_data(id=id, amount=info[1], descs=info[2],
                                category_id=info[0])
        try: title_cat = obj_cat.get_title({"user_id":user_id, "id":info[0]})
        except: pass
        await state.update_data(title_cat=title_cat)
        try: categories = obj_cat.select_categories(user_id)
        except: pass
        await callback.message.answer(
            f"☐ Category: {title_cat}\n"+
            f"☐ Amount: {info[1]}\n"+
            f"☐ Description: {info[2]}\n\n"+
            f"⬇️ Choose new category",
            reply_markup=add_cat(categories, True))

@router_spd.callback_query(F.data.startswith("chge_cat_spd_"))
async def chge_spd_2(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    category_id = str(callback.data).replace('chge_cat_spd_', '')
    user_id = callback.from_user.id
    try: title_cat = obj_cat.get_title({'user_id':user_id, 'id':int(category_id)})
    except: pass
    await state.update_data(title_cat=title_cat, category_id=int(category_id))
    msg = await callback.message.edit_text(
            f"✔️ Category: {title_cat}\n"+
            f"☐ Amount: {data['amount']}\n"+
            f"☐ Description: {data['descs']}\n\n"+
            f"⬇️ Enter new amount",
            reply_markup=cancel_kb())
    await state.update_data(msg_id=msg.message_id)
    await state.set_state(Upd_spend.amount)

@router_spd.message(Upd_spend.amount)
async def chge_spd_3(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    user_id = message.from_user.id
    await message.bot.delete_message(chat_id=user_id, 
                                     message_id=data['msg_id'])
    try: amt = int(message.text) 
    except: amt = -1

    if amt < 0:
        await message.answer(
            f"✔️ Category: {data['title_cat']}\n"+
            f"☐ Amount: {data['amount']}\n"+
            f"☐ Description: {data['descs']}\n\n"+
            "⬇️ Incorrect amount value. Please repeat")
        await state.set_state(Upd_spend.amount)
    else:
        await state.update_data(amount=amt)
        msg = await message.answer(
            f"✔️ Category: {data['title_cat']}\n"+
            f"✔️ Amount: {amt}\n"+
            f"☐ Description: {data['descs']}\n\n"+
            f"⬇️ Enter new Description",
            reply_markup=cancel_kb())
        await state.update_data(msg_id=msg.message_id)
        await state.set_state(Upd_spend.desc)

@router_spd.message(Upd_spend.desc)
async def chge_spd_4(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    user_id = message.from_user.id
    await message.bot.delete_message(chat_id=user_id, 
                                     message_id=data['msg_id'])
    
    await state.update_data(descs=message.text)
    data = await state.get_data()
    try: obj_spend.change_spend(data)
    except: pass
    await message.answer(
            f"✔️ Category: {data['title_cat']}\n"+
            f"✔️ Amount: {data['amount']}\n"+
            f"✔️ Description: {data['descs']}\n\n"+
            "✅ Record successfully changed", reply_markup=cancel_kb(title=True))
    await state.clear()