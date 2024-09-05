from asyncio import sleep

from discord import Interaction, ButtonStyle, TextChannel, Message
from discord.app_commands import command
from discord.app_commands.checks import has_role, has_any_role
from discord.ui import Button, View

from core.client import CLIENT

@command(name="rules", description="Met à jour les règles du serveur")
@has_role(CLIENT.config['admin_role'].id)
async def rules(ctx: Interaction):
    try:
        # Get the rules channel
        channel: TextChannel = CLIENT.config['rules_channel']

        # Load the rules
        with open('data/rules.md', 'r', encoding='utf-8') as f:
            rules_src = f.read().split('\n')

        # Split the rules into blocks of 2000 characters, and make sure the blocks end with a newline
        rules = []
        while rules_src:
            rule = rules_src.pop(0)
            while rules_src and len(rule) + len(rules_src[0]) < 2000:
                rule += '\n' + rules_src.pop(0)
            rules.append(rule)

        # Create a view with a button to accept the rules
        view = View()
        button = Button(style=ButtonStyle.success, label="✅ Accepter les règles", custom_id="accept_rules")
        view.add_item(button)

        # Send the rules
        for block in rules:
            await channel.send(block)

        # Send the view
        await channel.send(view=view)
        await ctx.response.send_message("Les règles ont été mises à jour avec succès !", ephemeral=True)
    except Exception as e:
        await ctx.response.send_message(f"Erreur: {e}", ephemeral=True)

# handle failure on role check
@rules.error
async def rules_error(ctx: Interaction, error: Exception):
    await ctx.response.send_message(f"Erreur: {error}\nTu ne ne sembles pas avoir les permissions nécessaires pour ça...", ephemeral=True)


@command(name="notification", description="Envoie une notification à tous les membres")
@has_any_role(CLIENT.config['admin_role'].id, CLIENT.config['moderator_role'].id)
async def notification(ctx: Interaction):
    # put the bot in thinking mode
    await ctx.response.defer()
    try:
        # wait for the user response message
        prompt = await ctx.followup.send("Veuillez entrer le message à envoyer.", ephemeral=True)
        response = await CLIENT.wait_for('message', timeout=300, check=lambda m: m.author.id == ctx.user.id and m.channel.id == ctx.channel.id)

        # Get the text of the message
        message = response.content

        # Check if the message is empty
        if not message:
            await ctx.followup.send("Le message ne peut pas être vide.", ephemeral=True)
            return
        
        # Split the message into blocks of 2000 characters, and make sure the blocks end with a newline
        messages = []
        message = message.split('\n')
        while message:
            block = message.pop(0)
            while message and len(block) + len(message[0]) < 2000:
                block += '\n' + message.pop(0)
            messages.append(block)

        # Delete the prompt and the response
        await prompt.delete()
        await response.delete()

        # Get the notification channel
        channel: TextChannel = CLIENT.config['notification_channel']

        # Send the notification
        for block in messages:
            await channel.send(block)
        
        # Send a confirmation message
        await ctx.followup.send("Notification envoyée avec succès !", ephemeral=True)

    # handle timeout
    except Exception as e:
        await ctx.followup.send(f"Erreur: {e}", ephemeral=True)

# handle failure on role check
@notification.error
async def notification_error(ctx: Interaction, error: Exception):
    await ctx.response.send_message(f"Erreur: {error}\nTu ne ne sembles pas avoir les permissions nécessaires pour ça...", ephemeral=True)

async def accept_rules(ctx: Interaction):
    # Get the member
    member = ctx.guild.get_member(ctx.user.id)

    # Get the rules role
    role = CLIENT.config['user_role']

    # Add the role to the member
    await member.add_roles(role)

    # Send a message
    await ctx.response.send_message(f"Bienvenue {member.mention} ! Tu as maintenant accès à tout le serveur, profites-en pour aller de présenter dans <#1264202256882864211>", ephemeral=True)

# delete an amount of messages in a channel
@command(name="rm", description="Supprime un nombre de messages dans un salon")
@has_any_role(CLIENT.config['admin_role'].id, CLIENT.config['moderator_role'].id)
async def remove(ctx: Interaction, amount:str):
    await ctx.response.defer()
    try:
        # Get the amount of messages to delete
        amount = 100 if amount in ['all', '*'] else int(amount)

        # Delete the messages
        await ctx.channel.purge(limit=amount)
        msg: Message = await ctx.channel.send(f"{amount} messages supprimés avec succès !")
        await sleep(1)
        await msg.delete()

    except Exception as e:
        msg = await ctx.channel.send(f"Erreur: {e}\nArgument invalide.", ephemeral=True)
        await sleep(1)
        await msg.delete()

# handle failure on role check
@remove.error
async def remove_error(ctx: Interaction, error: Exception):
    await ctx.channel.send(f"Erreur: {error}\nTu ne ne sembles pas avoir les permissions nécessaires pour ça...", ephemeral=True)
