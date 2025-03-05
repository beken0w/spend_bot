from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from keyboards.inline_kb import delete_message_kb, rpt_period_kb, main_report_kb, cat_list
from FSM.Spend_class import Spend
from FSM.Category_class import Category

router_rpt = Router()
obj_spend = Spend()
obj_cat   = Category()


@router_rpt.callback_query(F.data == "main_rpt")
async def main_rpt(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.delete()
    await callback.message.answer('⬇️ Choose type', reply_markup=main_report_kb())

# ------------------------------------------------------------------------------------

@router_rpt.callback_query(F.data == "rpt_prd")
async def rpt_by_period(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.delete()
    await callback.message.answer('⬇️ Choose period', reply_markup=rpt_period_kb())


@router_rpt.callback_query(F.data.startswith("rpt_prd_"))
async def rpt_by_period_2(callback: CallbackQuery):
    period = int(str(callback.data).replace('rpt_prd_', ''))
    user_id = callback.from_user.id
    try: output = obj_spend.select_spend_by_period({"user_id":user_id, "period":period})
    except: pass
    if output == -1:
        await callback.answer("❗ No data for this period", cache_time=5)
    else:
        await callback.answer()
        await callback.message.answer(f"```{output}```", 
                                      parse_mode="MarkdownV2",
                                      reply_markup=delete_message_kb())


@router_rpt.callback_query(F.data.startswith("rpt_period_"))
async def rpt_by_period_2(callback: CallbackQuery):
    period = str(callback.data).replace('rpt_period_', '')
    user_id = callback.from_user.id
    try: output = obj_spend.select_spend_by_period_curr_1m_2m_3m(
        {"user_id":user_id, "period":period})
    except: pass
    if output == -1:
        await callback.answer("❗ No data for this period", cache_time=5)
    else:
        await callback.answer()
        await callback.message.answer(f"```{output}```", 
                                      parse_mode="MarkdownV2",
                                      reply_markup=delete_message_kb())

# ------------------------------------------------------------------------------------
        
@router_rpt.callback_query(F.data == "rpt_cat")
async def rpt_by_cat(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.delete()
    user_id = callback.from_user.id
    try: categories = obj_cat.select_categories(user_id)
    except: pass
    await callback.message.answer('⬇️ Choose category', 
                                     reply_markup=cat_list(categories, True))  

@router_rpt.callback_query(F.data.startswith("rpt_cat_"))
async def rpt_by_cat2(callback: CallbackQuery):
    category_id = str(callback.data).replace('rpt_cat_', '')
    user_id = callback.from_user.id
    try: spendings = obj_spend.select_spend_by_category(
        {"user_id":user_id, "category_id":category_id})
    except: pass
    if spendings == -1:
        await callback.answer("❗ No data for this category", cache_time=5)
    else:
        await callback.answer()
        await callback.message.answer(f"```{spendings}```", 
                                      parse_mode="MarkdownV2",
                                      reply_markup=delete_message_kb())

# ------------------------------------------------------------------------------------

@router_rpt.callback_query(F.data == "remove_msg")
async def remove_msg(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.answer('✅ Message removed', cache_time=5)

