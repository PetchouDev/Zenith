from typing import Optional
from datetime import datetime

from discord import Interaction, User, TextChannel, Webhook, File
from discord.app_commands import command

from easy_pil import Editor, Font, load_image_async

from core.client import CLIENT


@command(name="ping", description="Renvoie la latence du bot")
async def ping(ctx: Interaction):
    bot = ctx.client
    await ctx.response.send_message(f"Pong! in {bot.latency * 1000 :.2f}ms")

@command(name="echo", description="Envoie un message anonyme à un utilisateur (loggé pour la modération)")
async def echo(ctx: Interaction, message: str, user: Optional[User] = None):
    if user is None:
        await ctx.response.send_message(message)
        open('data/logs', 'a').write(f"{datetime.now()} - {ctx.user.display_name} ({ctx.user.id}) echoed '{message}'\n")
        return
    
    await user.send(f"{message}")
    await ctx.response.send_message(f"J'ai envoyé '{message}' à {user.display_name} !", ephemeral=True)
    open('data/logs', 'a').write(f"{datetime.now()} - {ctx.user.display_name} ({ctx.user.id}) echoed '{message}' to {user.display_name} ({user.id})\n")

async def send_xp_banner(user: User, message: str, channel: TextChannel | Webhook):
    # Define the colors
    MAIN_COLOR = "white"
    ACCENT_COLOR = (114, 124, 161)
    ALT_COLOR = (5, 7, 45)

    # Get the user's level and xp
    level, xp, xp_to_next = CLIENT.get_user_level(user.id)

    # calculate the percentage
    percentage = int(xp / xp_to_next * 100)

    # Create the banner
    banner = Editor("data/bg.png")

    # Get the profile picture of the user
    profile_pic = await load_image_async(user.display_avatar.url)
    profile_pic = Editor(profile_pic).resize((200, 200)).circle_image()
    banner.paste(profile_pic, (50, 50))

    font = Font("data/Roboto-Bold.ttf", 40)
    font_small = Font("data/Roboto-Bold.ttf", 20)

    # Draw the name
    banner.text((300, 50), user.display_name, font=font, color=MAIN_COLOR)

    # Underline the name
    banner.rectangle((300, 90), width=200, height=2, fill=ACCENT_COLOR)

    # Draw the level and xp
    banner.text((300, 100), f"Niveau {level}, {xp}/{xp_to_next}XP ({percentage}%)", font=font_small, color=MAIN_COLOR)

    # Add a progress bar
    banner.rectangle(
        (300, 210),
        width=400,
        height=30,
        fill=MAIN_COLOR,
        radius=15,
        outline=ALT_COLOR,
        stroke_width=4,
    )
    banner.bar(
        (304, 214),
        max_width=392,
        height=22,
        percentage=int(min(100, max(22*100/392, percentage))),
        fill=ACCENT_COLOR,
        radius=11,
    )

    # Add Zenith's profile picture to the bottom right corner
    zenith = Editor("data/Zenith_pp.png")
    zenith = zenith.resize((200, 200))
    banner.paste(zenith, (700, 100))

    attachment = File(banner.image_bytes, filename="level_card.png")
    await channel.send(message, file=attachment)

@command(name="niveau", description="Affiche le niveau de l'utilisateur")
async def niveau(ctx: Interaction, user: Optional[User] = None):
    # dodge the timeout
    await ctx.response.defer(thinking=True, ephemeral=True)

    # if no user is provided, use the author of the command
    if not user:
        user = ctx.user

    # Send the banner
    await send_xp_banner(user, f"Niveau de {user.mention}", ctx.followup)
