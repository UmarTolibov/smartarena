import json

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def confirmation():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Tasdiqlash✅", callback_data="confirm"))
    markup.add(InlineKeyboardButton("O\'zgartirish✏️", callback_data="reject"))
    return markup


def regions_inline(for_add=0):
    markup = InlineKeyboardMarkup(row_width=2)
    with open("bot/users/markups/regions.json", "r", encoding="utf-8") as data:
        regions = json.load(data)["regions"]
    for i in range(0, len(regions), 2):
        row_buttons = []
        for j in range(2):
            if i + j < len(regions):
                region = regions[i + j]
                region_id = region["id"]
                region_name = region["name"]
                if for_add == 0:
                    row_buttons.append(InlineKeyboardButton(region_name, callback_data=f"region|{region_id}"))
                elif for_add == 1:
                    row_buttons.append(InlineKeyboardButton(region_name, callback_data=f"add_region|{region_id}"))

        markup.row(*row_buttons)
    return markup


def district_inline(region_id, for_add=0):
    markup = InlineKeyboardMarkup(row_width=2)

    with open("bot/users/markups/regions.json", "r", encoding="utf-8") as data:
        districts = json.load(data)["districts"]

    row_buttons = []
    for district in districts:
        if district["region_id"] == region_id:
            district_id = district["id"]
            district_name = district["name"]
            if for_add == 0:
                row_buttons.append(InlineKeyboardButton(district_name, callback_data=f"district|{district_id}"))
            else:
                row_buttons.append(InlineKeyboardButton(district_name, callback_data=f"add_district|{district_id}"))

            if len(row_buttons) == 2:
                markup.row(*row_buttons)
                row_buttons = []

    if row_buttons:  # Add the remaining buttons if any
        markup.row(*row_buttons)

    return markup


def start_time_inline(for_add=0):
    markup = InlineKeyboardMarkup(row_width=3)

    # Define a list of day times
    day_times = ["8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00",
                 "19:00", "20:00", "21:00", "22:00", "23:00", "00:00"]

    row_buttons = []
    for time in day_times:
        if for_add == 0:
            row_buttons.append(InlineKeyboardButton(time, callback_data=f"start_time|{time}"))
        elif for_add == 1:
            row_buttons.append(InlineKeyboardButton(time, callback_data=f"s_time|{time}"))
        else:
            row_buttons.append(InlineKeyboardButton(time, callback_data=f"c_time|{time}"))

        if len(row_buttons) == 3:
            markup.row(*row_buttons)
            row_buttons = []

    if row_buttons:  # Add the remaining buttons if any
        markup.row(*row_buttons)

    return markup


def hours_inline():
    markup = InlineKeyboardMarkup(row_width=3)
    markup.row(InlineKeyboardButton("1", callback_data="hour|1"), InlineKeyboardButton("2", callback_data="hour|2"),
               InlineKeyboardButton("3", callback_data="hour|3"))
    return markup


def stadiums_inline(stadiums):
    markup = InlineKeyboardMarkup(row_width=1)
    for stadium in stadiums:
        button_text = stadium.name
        callback_data = f"stadium|{stadium.id}"

        button = InlineKeyboardButton(button_text, callback_data=callback_data)
        markup.add(button)

    return markup


def accounts_inline(accounts):
    markup = InlineKeyboardMarkup()
    row_buttons = []
    for username, user_id in accounts:
        row_buttons.append(InlineKeyboardButton(username, callback_data=f"account|{user_id}"))
        if len(row_buttons) == 2:
            markup.row(*row_buttons)
            row_buttons = []
    return markup


def yes_no_inline():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("Ha✅", callback_data="proceed|1"),
               InlineKeyboardButton("Yo'q❌", callback_data="proceed|0"))
    return markup


def stadiums_choose(stadiums):
    markup = InlineKeyboardMarkup(row_width=2)
    row_buttons = []
    for stadium in stadiums:
        markup.add(InlineKeyboardButton(stadium[0], callback_data=f"stadium|{stadium[1]}"))
    return markup


def manage_stadium():
    markup = InlineKeyboardMarkup()
    name = InlineKeyboardButton("Nom✏️", callback_data="manage|name")
    desc = InlineKeyboardButton("Ma'lumot✏️", callback_data="manage|description")
    image = InlineKeyboardButton("Rasmlar✏️", callback_data="manage|image")
    price = InlineKeyboardButton("Narx✏️", callback_data="manage|price")
    opening = InlineKeyboardButton("Ochilish vaqti✏️", callback_data="manage|opening_time")
    closing = InlineKeyboardButton("Yopilish vaqti✏️", callback_data="manage|closing_time")
    region = InlineKeyboardButton("Viloyat✏️", callback_data="manage|region")
    district = InlineKeyboardButton("Tuman✏️", callback_data="manage|district")
    location = InlineKeyboardButton("Lokatsiya✏️", callback_data="manage|location")
    delete = InlineKeyboardButton("Stadionni o'chirish❌", callback_data="manage|delete")
    markup.row(name, desc)
    markup.row(image, price)
    markup.row(opening, closing)
    markup.row(region, district)
    markup.row(location)
    markup.row(delete)
    return markup
