from discord import Interaction, InteractionType, User, Embed, Message

from core.client import CLIENT

from .tickets import handle_ticket_creation
from .moderation import accept_rules
from .private_rooms import handle_room_deletion, handle_room_creation
from .general import send_xp_banner

@CLIENT.event
async def on_interaction(ctx: Interaction):
    # if the interaction is a component interaction, then dispatch the event to the right handler
    if ctx.type == InteractionType.component:
        match ctx.data['custom_id']:

            case 'open_ticket':
                await handle_ticket_creation(ctx)

            case 'accept_rules':
                await accept_rules(ctx)

            case 'close_room':
                await handle_room_deletion(ctx)

            case 'create_room':
                await handle_room_creation(ctx)

            case _:
                return
            
@CLIENT.event
async def on_member_join(member: User):
    # Send a private message to the user who joins the server
    await member.send("Bienvenue sur le serveur de la promo TCA 2024/2027 !\nMerci de lire les <#1263821634792456254> pour obtenir ton accès complet.")
    
    # Build an embed message to welcome the user in the welcome channel
    msg = Embed(title="Nouveau membre", description=f"**Bienvenue {member.mention} !**\nHeureux de te compter parmis nous.", color=0x00ff00)
    msg.set_thumbnail(url=member.display_avatar.url)


    # Send the message in the welcome channel
    await CLIENT.config['welcome_channel'].send(embed=msg)


# Quand un membre envoie un message, lmui ajouter de l'xp
@CLIENT.event
async def on_message(message: Message):
    if message.author == CLIENT.user:
        return

    print(f"Message from {message.author.display_name}: {message.content}")
    print(f"XP: {CLIENT.xp.get(message.author.id)}")
    level_up = CLIENT.add_xp(message.author.id, min(len(message.content) // 10, 100))

    if level_up:
        await send_xp_banner(message.author, f"{message.author.mention} a atteint le niveau supérieur !", CLIENT.config['level_up_channel'])
    
    # await CLIENT.process_commands(message) # This is not needed anymore since we are using the new interaction system