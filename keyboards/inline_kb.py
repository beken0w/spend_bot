from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def add_cat(arr, is_change = None):
    btns = []
    txt = 'chge_cat_spd_' if is_change else 'add_cat|'
    for i in arr:
        btns.append([InlineKeyboardButton(text=i[2], callback_data=f"{txt}{i[0]}")])
    btns.append([InlineKeyboardButton(text='Cancel -> Menu', callback_data=f"main_menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=btns)
    return kb

def cat_list(arr, is_report = False):
    btns = []
    msg = 'cat_list_' if not is_report else 'rpt_cat_'
    for i in arr:
        btns.append([InlineKeyboardButton(text=i[2], callback_data=f"{msg}{i[0]}")])
    if not is_report:
        btns.append([InlineKeyboardButton(text='➕ New category', callback_data=f"new_cat")])
    btns.append([InlineKeyboardButton(text='Cancel -> Menu', callback_data=f"main_menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=btns)
    return kb

def welcome_kb():
    btns = [
        [InlineKeyboardButton(text="Categories",         callback_data='main_cat')],
        [InlineKeyboardButton(text="Reports",            callback_data='main_rpt')],
        [InlineKeyboardButton(text="5 last spendings",  callback_data='last_5_spend')],
        [InlineKeyboardButton(text="+ spend",         callback_data='new_spend')]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=btns)
    return kb


def cancel_kb(new_spend = None, title = None, after_new = None):
    if not title:
        title = 'Cancel -> Menu'
    else:
        title = 'Main menu'
    btns = [[InlineKeyboardButton(text=title, callback_data='main_menu')]]
    if new_spend:
        btns.append([InlineKeyboardButton(text='Edit category', callback_data='new_spend')])
    if after_new:
        btns.append([InlineKeyboardButton(text='+ spend', callback_data='new_spend')])
    kb = InlineKeyboardMarkup(inline_keyboard=btns)
    return kb


def delete_change_kb(kind, id):
    btns = [
        [InlineKeyboardButton(text="Delete",callback_data=f'del|{kind}|{id}'),
         InlineKeyboardButton(text="Edit",  callback_data=f'chge|{kind}|{id}')]
    ]
    if kind == 'cat':
        btns.append([InlineKeyboardButton(text='Cancel -> Menu', callback_data='main_menu')])
    kb = InlineKeyboardMarkup(inline_keyboard=btns)
    return kb

def main_report_kb():
    btns = [
        [InlineKeyboardButton(text="By period",          callback_data='rpt_prd')],
        [InlineKeyboardButton(text="By category",        callback_data='rpt_cat')],
        [InlineKeyboardButton(text='Cancel -> Menu',     callback_data='main_menu')]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=btns)
    return kb


def rpt_period_kb():
    btns = [
        [InlineKeyboardButton(text="All time",           callback_data='rpt_prd_9999')],
        [InlineKeyboardButton(text="90 days",            callback_data='rpt_prd_90')],
        [InlineKeyboardButton(text="30 days",            callback_data='rpt_prd_30')],
        [InlineKeyboardButton(text="7 days",             callback_data='rpt_prd_7')],

        [InlineKeyboardButton(text="3 months ago",       callback_data='rpt_period_3m')],
        [InlineKeyboardButton(text="2 months ago",       callback_data='rpt_period_2m')],
        [InlineKeyboardButton(text="Last month",         callback_data='rpt_period_1m')],
        [InlineKeyboardButton(text="Current_month",      callback_data='rpt_period_curr')],
        [InlineKeyboardButton(text="Today",              callback_data='rpt_prd_1')],
        [InlineKeyboardButton(text='Cancel -> Menu',     callback_data='main_menu')]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=btns)
    return kb

def delete_message_kb():
    btns = [
        [InlineKeyboardButton(text="Remove message",         callback_data='remove_msg')]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=btns)
    return kb