


from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
USERS = env.list("USERS")
IP = env.str("ip")

# Запустить SD при старте бота
launch_sd_at_bot_started = False

# Проверка запуска SD
# False - Проверить и выйти если не запущена SD,
# True - Проверять через каждые time_the_next_check_s секунд.
is_wait_sd_launch = False
time_the_next_check_s = 1

sd_path = """C:\SD2_0\stable-diffusion-webui-master"""

# Отправить фото без сжатия
send_photo_without_compression = True