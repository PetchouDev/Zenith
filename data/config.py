from discord import Client, TextChannel, CategoryChannel, Guild, Role

CONFIG = {
    "guild": 1263821633181978666,
    "ticket_category": 1263836915631919165,
    "ticket_channel": 1263823050277650626,
    "admin_role": 1263823272764637194,
    "moderator_role": 1263823407611641866,
    "user_role": 1263823826320621608,
    "rules_channel": 1263821634792456254,
    "notification_channel": 1263824162259206275,
    "welcome_channel": 1263821634297397291,
    "level_up_channel": 1264562333079048246,
}

async def load_config(bot: Client) -> dict:
    """Load the configuration from the bot"""

    CONFIG['guild']: Guild = await bot.fetch_guild(CONFIG['guild'])
    CONFIG['ticket_category']: CategoryChannel = await bot.fetch_channel(CONFIG['ticket_category'])
    CONFIG['ticket_channel']: TextChannel = await bot.fetch_channel(CONFIG['ticket_channel'])
    CONFIG['admin_role']: Role = CONFIG['guild'].get_role(CONFIG['admin_role'])
    CONFIG['moderator_role']: Role = CONFIG['guild'].get_role(CONFIG['moderator_role'])
    CONFIG['user_role']: Role = CONFIG['guild'].get_role(CONFIG['user_role'])
    CONFIG['rules_channel']: TextChannel = await bot.fetch_channel(CONFIG['rules_channel'])
    CONFIG['notification_channel']: TextChannel = await bot.fetch_channel(CONFIG['notification_channel'])
    CONFIG['welcome_channel']: TextChannel = await bot.fetch_channel(CONFIG['welcome_channel'])
    CONFIG['level_up_channel']: TextChannel = await bot.fetch_channel(CONFIG['level_up_channel'])
    return CONFIG
