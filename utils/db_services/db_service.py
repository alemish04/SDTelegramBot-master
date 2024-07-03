


import logging
import sqlite3

import aiosqlite

from settings.sd_config import get_default_params


async def db_create_table():
    async with aiosqlite.connect('users_sd_settings.db') as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS users(
           tg_id INT PRIMARY KEY,
           sd_model TEXT,
           sd_style TEXT,
           sd_lora TEXT,
           sd_n_prompt TEXT,
           sd_sampler TEXT,
           sd_steps INT,
           sd_width_height TEXT,
           sd_cfg_scale REAL,
           sd_batch_count INT,
           sd_hr_on_off INT,
           sd_hr_upscaler TEXT,
           sd_hr_steps INT,
           sd_hr_denoising_strength REAL,
           sd_hr_upscale_by INT, 
           user_last_prompt TEXT);
        """)
        await db.commit()


async def db_get_sd_settings(tg_id: int):
    async with aiosqlite.connect('users_sd_settings.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(f"SELECT * FROM users WHERE tg_id={tg_id};") as cursor:
            return await cursor.fetchone()


async def db_get_sd_setting(tg_id: int, param: str):
    async with aiosqlite.connect('users_sd_settings.db') as db:
        async with db.execute(f"SELECT {param} FROM users WHERE tg_id={tg_id};") as cursor:
            async for row in cursor:
                return row[0]



async def db_get_all_tg_id():
    async with aiosqlite.connect('users_sd_settings.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(f"SELECT tg_id FROM users;") as cursor:
            return await cursor.fetchall()


async def db_delete_user(tg_id):
    async with aiosqlite.connect('users_sd_settings.db') as db:
        async with db.execute(f"DELETE FROM users WHERE tg_id={tg_id};"):
            await db.commit()


async def db_set_sd_settings(tg_id, setting, value):
    async with aiosqlite.connect('users_sd_settings.db') as db:
        await db.execute(f"""UPDATE users SET {setting}="{value}" WHERE tg_id={tg_id};""")
        await db.commit()


async def db_create_new_user_settings(tg_id: int):
    params = list(get_default_params(tg_id).values())
    params.append("")

    async with aiosqlite.connect('users_sd_settings.db') as db:
        await db.execute(f"""INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", params)
        await db.commit()


async def db_update_default_settings(tg_id: int):
    params = list(get_default_params(tg_id).values())





    params.append("")



    settings = ['tg_id', 'sd_model', 'sd_style', 'sd_lora', 'sd_n_prompt', 'sd_sampler', 'sd_steps', 'sd_width_height',
                'sd_cfg_scale', 'sd_batch_count', 'sd_hr_on_off', 'sd_hr_upscaler', 'sd_hr_steps',
                'sd_hr_denoising_strength', 'sd_hr_upscale_by', 'user_last_prompt']

    for i in range(len(settings)):
        await db_set_sd_settings(tg_id, settings[i], params[i])


async def user_verification(admins, users):
    db_users = list(x['tg_id'] for x in await db_get_all_tg_id())
    for db_user in db_users:
        if str(db_user) not in admins and str(db_user) not in users:
            logging.warning(f"Delete user: {db_user}")
            await db_delete_user(db_user)


async def admins_and_users_initialization_in_db():
    from settings.bot_config import ADMINS
    from settings.bot_config import USERS
    await user_verification(ADMINS, USERS)
    for admin in ADMINS:
        try:
            await db_create_new_user_settings(admin)
            logging.info(f"Create new admin: {admin}")
        except sqlite3.IntegrityError:
            continue

    for user in USERS:
        try:
            await db_create_new_user_settings(user)
            logging.info(f"Create new user: {user}")
        except sqlite3.IntegrityError:
            continue
async def queue_create():
    async with aiosqlite.connect('users_sd_settings.db') as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS queue(
                   user_id INT,
                   prompt TEXT,
                   time_time DATETIME);
                """)
        await db.commit()

# async def queue_add():
#     async with aiosqlite.connect('users_sd_settings.db') as db:
#         await db.execute("""
#         """