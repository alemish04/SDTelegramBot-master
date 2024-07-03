


from aiogram.dispatcher.filters.state import StatesGroup, State


class SDStates(StatesGroup):
    waiting_for_authorization = State()
    enter_prompt = State()

    settings = State()
    gen_settings = State()
    settings_set_model = State()
    settings_set_style = State()
    settings_set_lora = State()
    settings_set_n_prompt = State()
    settings_set_sampler = State()
    settings_set_steps = State()
    settings_set_wh = State()
    settings_set_cfg_scale = State()
    settings_set_restore_face = State()
    settings_set_batch_count = State()

    hr_settings = State()
    hr_set_on_off = State()
    hr_change_upscaler = State()
    hr_set_steps = State()
    hr_set_denoising_strength = State()
    hr_set_upscale_by = State()

    restart_sd = State()


