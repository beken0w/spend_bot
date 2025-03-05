from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from FSM.states import New_Category, Upd_Category

from keyboards.inline_kb import  delete_change_kb, cancel_kb, cat_list
from FSM.Category_class import Category
from FSM.Spend_class import Spend

router_cat = Router()
obj_cat = Category()
obj_spd = Spend()


@router_cat.callback_query(F.data == "main_cat")
async def main_categories(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    try: categories = obj_cat.select_categories(user_id)
    except: pass
    await callback.message.edit_text('⬇️ Select category to change', 
                                     reply_markup=cat_list(categories))


@router_cat.callback_query(F.data.startswith("cat_list_"))
async def cat_list_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    id = str(callback.data).replace('cat_list_', '')
    try: title = obj_cat.get_title({'user_id':user_id, 'id': id})
    except: pass
    if title == 'Unallocated':
        await callback.message.edit_text('❗ Unallocated category cannot be changed',
                                         reply_markup=cancel_kb(title=True)) 
    else:
        await callback.message.edit_text(title, 
                                        reply_markup=delete_change_kb('cat', id))


@router_cat.callback_query(F.data == "new_cat")
async def new_cat_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await state.set_state(New_Category.cat_title)
    msg = await callback.message.edit_text('❗ Max length is 30 symbols\n'\
                                            '⬇️ Enter title of category', 
                                    reply_markup=cancel_kb())
    await state.update_data(msg_id=msg.message_id)


@router_cat.message(New_Category.cat_title)
async def new_cat_2(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    user_id=message.from_user.id
    await message.bot.delete_message(chat_id=user_id, 
                                     message_id=data['msg_id'])
    new_title = message.text
    if len(new_title) > 30:
        await message.answer('❗ Max length is 30 symbols\n⬇️ Enter title of category', 
                             reply_markup=cancel_kb()) 
        await state.set_state(New_Category.cat_title)
        return
    try: is_exist = obj_cat.is_exist_by_title({'user_id':user_id, 'title':new_title}) 
    except: pass

    if is_exist != -1:
        await message.answer('❗ Such a category already exists. \n⬇️ Enter title of category:', 
                             reply_markup=cancel_kb()) 
        await state.set_state(New_Category.cat_title)
        return 
    
    try: obj_cat.insert_category({'user_id':user_id, 'title':new_title})
    except: pass
    await message.answer(f'✅ Category {new_title} created successfully', 
                            reply_markup=cancel_kb(title=True))
    await state.clear()


@router_cat.callback_query(F.data.startswith("del|cat|"))
async def del_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    id = str(callback.data).replace('del|cat|', '')
    user_id = callback.from_user.id
    try: is_exist = obj_cat.is_exist_by_id({'user_id':user_id, 'id': id})
    except: pass
    if is_exist == -1:
        await callback.message.edit_text('❗ This category doesn`t exist')
    else:
        try: is_exist_by_id = obj_spd.is_exist_by_category_id(id)
        except: pass
        if is_exist_by_id == -1:
            try: obj_cat.delete_category({'user_id':user_id, 'id': id})
            except: pass
            await callback.message.edit_text('✅ Category removed successfully',
                                             reply_markup=cancel_kb(title=True))
        else:
            try: unallocated_id = obj_cat.is_exist_by_title(
                {"user_id": user_id, "title" : 'Unallocated'})
            except: pass
            try:
                obj_spd.update_category(unallocated_id, id) # new_id | old_id
                obj_cat.delete_category({'user_id':user_id, 'id': id})
            except: pass
            await callback.message.edit_text(
                "✅ Category removed successfully.\n"\
                "✅ Existing transaction categories have been moved to Unallocated",
                reply_markup=cancel_kb(title=True))
    await state.clear()


@router_cat.callback_query(F.data.startswith("chge|cat|"))
async def chge_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    id = str(callback.data).replace('chge|cat|', '')
    user_id = callback.from_user.id
    await state.update_data(id=id, user_id=user_id)
    try: is_exist = obj_cat.is_exist_by_id({'user_id':user_id, 'id': id})
    except: pass
    if  is_exist == -1:
        await callback.message.edit_text('❗ Such a category doesn`t exist',
                                         reply_markup=cancel_kb(title=True))
    else:
        try: old_title = obj_cat.get_title({'user_id':user_id, 'id': id})
        except: pass
        await state.update_data(old_title=old_title)
        await state.set_state(Upd_Category.new_title)
        msg = await callback.message.edit_text(f'⬇️ Change title of category \n"{old_title}" to', 
                                        reply_markup=cancel_kb())
        await state.update_data(msg_id = msg.message_id)


@router_cat.message(Upd_Category.new_title)
async def chge_2(message: Message, state: FSMContext):
    await message.delete()
    new_title = message.text
    user_id = message.from_user.id
    data = await state.get_data()
    await message.bot.delete_message(chat_id=user_id, 
                                     message_id=data['msg_id'])
    try: is_exist = obj_cat.is_exist_by_title({"user_id": user_id, "title" : new_title})
    except: pass
    if is_exist != -1:
        await message.answer('❗ Such a category already exists. \n⬇️ Enter title of category:', 
                             reply_markup=cancel_kb(title=True)) 
        await state.set_state(Upd_Category.new_title)
        return 
    try: obj_cat.update_category({"new_title":new_title, "user_id":user_id, "id":data["id"]})
    except: pass
    await message.answer(f'✅ Category {data["old_title"]} successfully renamed to {new_title}', 
                         reply_markup=cancel_kb(title=True))
    await state.clear()
