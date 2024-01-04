from .loader import bot, bot_meta, stadium_sts, user_sts, auth_sts, manage_sts, booking_sts, settings_sts

from . import users
from . import superusers


async def user_register_handlers():
    bot.register_message_handler(users.backs.back_to_main, regexp="🔙Bosh sahifa", state="*", is_admin=False)
    bot.register_message_handler(users.backs.back, regexp="🔙Orqaga", state="*", is_admin=False)
    bot.register_message_handler(users.add_stadiums.my_stadium_handler, regexp="🏟️Stadionlarim")
    bot.register_message_handler(users.add_stadiums.add_stadium_handler, regexp="🌐Stadion qo'shish",
                                 state=stadium_sts.init)
    bot.register_callback_query_handler(users.add_stadiums.proceed_yes_no,
                                        func=lambda call: "proceed" in call.data.split("|"),
                                        is_admin=False)
    bot.register_message_handler(users.add_stadiums.stadium_name_handler, content_types=["text"],
                                 state=stadium_sts.name)
    bot.register_message_handler(users.add_stadiums.stadium_desc_handler, content_types=["text"],
                                 state=stadium_sts.description)

    bot.register_message_handler(users.add_stadiums.stadium_image_handler, content_types=["photo", "text"],
                                 state=stadium_sts.image)
    bot.register_message_handler(users.add_stadiums.stadium_price_handler, content_types=["text"],
                                 state=stadium_sts.price)
    bot.register_callback_query_handler(users.add_stadiums.stadium_open_time_handler,
                                        func=lambda call: "s_time" in call.data.split("|"),
                                        state=stadium_sts.open_time)
    bot.register_callback_query_handler(users.add_stadiums.stadium_close_time_handler,
                                        func=lambda call: "c_time" in call.data.split("|"),
                                        state=stadium_sts.close_time)
    bot.register_callback_query_handler(users.add_stadiums.stadium_region_handler,
                                        func=lambda call: "add_region" in call.data.split('|'),
                                        state=stadium_sts.region)
    bot.register_callback_query_handler(users.add_stadiums.district_choose,
                                        func=lambda call: "add_district" in call.data.split('|'),
                                        state=stadium_sts.district)

    bot.register_message_handler(users.add_stadiums.stadium_location_handler, content_types=["location"],
                                 state=stadium_sts.location)
    bot.register_callback_query_handler(users.add_stadiums.stadium_confirmation_handler,
                                        func=lambda call: call.data in ("confirm", "reject"), state=stadium_sts.confirm,
                                        is_admin=False)
    # users/auth

    bot.register_message_handler(users.auth.signup_handler, regexp="Ro'yxatdan o'tish🗒", state=auth_sts.init)
    bot.register_message_handler(users.auth.name_handler, content_types=["text"], state=auth_sts.name)
    bot.register_message_handler(users.auth.number_handler, content_types=["text", "contact"], state=auth_sts.number)
    bot.register_message_handler(users.auth.password_handler, content_types=["text"], state=auth_sts.password)
    bot.register_callback_query_handler(users.auth.confirmation_inline, func=lambda x: True, state=auth_sts.confirm)
    bot.register_message_handler(users.auth.login_handler, regexp="Kirish↙️", state=auth_sts.init)
    bot.register_message_handler(users.auth.login_username, content_types=["text"], state=auth_sts.username)
    bot.register_message_handler(users.auth._login_password, content_types=["text"], state=auth_sts.login_password,
                                 is_admin=False)
    bot.register_message_handler(users.auth.logout_handler, commands=["logout"], state='*')

    # users/booking

    bot.register_message_handler(users.booking.book_stadium, regexp="📆Bron qilish")
    bot.register_callback_query_handler(users.booking.region_choose, func=lambda call: "region" in call.data.split('|'))
    bot.register_callback_query_handler(users.booking.district_choose,
                                        func=lambda call: "district" in call.data.split('|'))
    bot.register_callback_query_handler(users.booking.date_choose, func=lambda call: "date" in call.data.split("|"))
    bot.register_callback_query_handler(users.booking.start_time_choose,
                                        func=lambda call: "start_time" in call.data.split('|'))
    bot.register_callback_query_handler(users.booking.hour_choose, func=lambda call: "hour" in call.data.split('|'),
                                        is_admin=False)
    bot.register_callback_query_handler(users.booking.stadium_preview, func=lambda call: "book" in call.data.split("|"))
    bot.register_callback_query_handler(users.booking.location_book,
                                        func=lambda call: call.data in ["book_now", "send_location"],
                                        is_admin=False)
    # users/help
    bot.register_message_handler(users.help.help_handler, commands=['help'])
    bot.register_message_handler(users.help.help_handler, regexp="ℹ️Yordam")
    # users/manage_stadiums

    bot.register_message_handler(users.manage_stadiums.manage_stadium_handler, regexp="🛠️Stadionlarimni boshqarish",
                                 state=stadium_sts.init)
    bot.register_callback_query_handler(users.manage_stadiums.stadium_to_manage,
                                        func=lambda call: "stadium" in call.data.split("|"),
                                        state=manage_sts.choose_stadium)
    bot.register_callback_query_handler(users.manage_stadiums.delete_stadium, func=lambda call: True,
                                        state=manage_sts.edit)
    bot.register_callback_query_handler(users.manage_stadiums.refresh_stadium, func=lambda call: True,
                                        state=manage_sts.edit)
    bot.register_callback_query_handler(users.manage_stadiums.edit_stadium_data,
                                        func=lambda call: call.data.split("|")[1] in ["name", "desc", "image_urls",
                                                                                      "price", "otime", "ctime", "reg",
                                                                                      "disc", "location"],
                                        state=manage_sts.edit)

    bot.register_message_handler(users.manage_stadiums.stadium_edit_name_handler, content_types=["text"],
                                 state=manage_sts.name)
    bot.register_message_handler(users.manage_stadiums.stadium_desc_edit_handler, content_types=["text"],
                                 state=manage_sts.description)
    bot.register_message_handler(users.manage_stadiums.stadium_edit_location_handler, content_types=["location"],
                                 state=manage_sts.location)
    bot.register_message_handler(users.manage_stadiums.stadium_edit_image_handler, content_types=["photo", "text"],
                                 state=manage_sts.image)
    bot.register_message_handler(users.manage_stadiums.stadium_edit_price_handler, content_types=["text"],
                                 state=manage_sts.price)
    bot.register_callback_query_handler(users.manage_stadiums.stadium_edit_open_time_handler,
                                        func=lambda call: "s_time" in call.data.split("|"),
                                        state=manage_sts.open_time)
    bot.register_callback_query_handler(users.manage_stadiums.stadium_edit_close_time_handler,
                                        func=lambda call: "c_time" in call.data.split("|"),
                                        state=manage_sts.close_time)
    bot.register_callback_query_handler(users.manage_stadiums.stadium_edit_region_handler,
                                        func=lambda call: "add_region" in call.data.split('|'),
                                        state=manage_sts.region)
    bot.register_callback_query_handler(users.manage_stadiums.edit_district_choose,
                                        func=lambda call: "add_district" in call.data.split('|'),
                                        state=manage_sts.district)

    # users/my_orders
    bot.register_message_handler(users.my_orders.my_booking_stadium, regexp="📅 Buyurtmalarni Ko'rish")
    bot.register_message_handler(users.my_orders.upcoming_bookings, regexp="🔜 Kelayotgan buyurtmalar",
                                 state=booking_sts.init)
    bot.register_message_handler(users.my_orders.booking_history, regexp="📆 Buyurtmalar tarixi", state=booking_sts.init)

    # users/settings
    bot.register_message_handler(users.settings.settings_handler, regexp="⚙️Sozlanmalar")
    bot.register_message_handler(users.settings.settings_username, regexp="✏️Username", state=settings_sts.init)
    bot.register_message_handler(users.settings.settings_set_username, content_types=["text"],
                                 state=settings_sts.username)
    bot.register_message_handler(users.settings.settings_password, regexp="✏️Password", state=settings_sts.init)
    bot.register_message_handler(users.settings.settings_old_password, content_types=["text"],
                                 state=settings_sts.old_password)
    bot.register_message_handler(users.settings.settings_new_password, content_types=["text"],
                                 state=settings_sts.new_password)

    bot.register_message_handler(users.start.greeting, commands=["start"], is_admin=False)
    bot.register_callback_query_handler(users.start.choose_account_handler,
                                        func=lambda call: "account" in call.data.split("|"), state=auth_sts.account)


async def superuser_register_handlers():
    # admin menu
    bot.register_message_handler(superusers.admin_menu.admin_menu_, regexp="👨‍💻Admin", is_admin=True)
    bot.register_message_handler(superusers.admin_menu.admin_menu_users, regexp="Foydalanuvchilar👥")
    bot.register_message_handler(superusers.admin_menu.admin_menu_stadiums, regexp="Stadionlar🏟")
    bot.register_message_handler(superusers.admin_menu.admin_menu_orders, regexp="Buyurtmalar🗒")

    bot.register_message_handler(superusers.backs.back_to_main, regexp="🔙Bosh sahifa", state="*", is_admin=True)
    bot.register_message_handler(superusers.backs.back, regexp="🔙Orqaga", state="*", is_admin=True)
    bot.register_message_handler(superusers.start.greeting_admin, commands=["start"], is_admin=True)
    bot.register_callback_query_handler(superusers.start.choose_account_handler,
                                        func=lambda call: "account" in call.data.split("|"), is_admin=True)
    bot.register_message_handler(superusers.start.admin_login_password, content_types=["text"],
                                 state=auth_sts.login_password, is_admin=True)

    bot.register_callback_query_handler(superusers.start.ad_stadium_confirmation_handler,
                                        func=lambda call: call.data in ("confirm", "reject"), state=stadium_sts.confirm,
                                        is_admin=True)

    bot.register_callback_query_handler(superusers.start.admin_proceed_yes_no,
                                        func=lambda call: "proceed" in call.data.split("|"), is_admin=True)
    bot.register_callback_query_handler(superusers.start.admin_hour_choose,
                                        func=lambda call: "hour" in call.data.split('|'), is_admin=True)
    bot.register_callback_query_handler(superusers.start.admin_location_book,
                                        func=lambda call: call.data in ["book_now", "send_location"], is_admin=True)
