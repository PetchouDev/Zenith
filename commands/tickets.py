from typing import Optional

from discord import Interaction, ButtonStyle, Embed, TextChannel, CategoryChannel, TextStyle
from discord.app_commands import command
from discord.app_commands.checks import has_role, has_any_role
from discord.ui import Button, View, Modal, TextInput

from core.client import CLIENT

# Modal class to ask the reason for opening a ticket
class TicketModal(Modal, title="Raison du ticket"):
    reason = TextInput(label="Raison", placeholder="Raison du ticket", max_length=200, style=TextStyle.paragraph)

    async def on_submit(self, ctx: Interaction) -> None:
        # Créer un salon de ticket
        category: CategoryChannel = CLIENT.config['ticket_category']
        await ctx.response.defer()
        try:
            ticket_channel = await category.create_text_channel(f"ticket-{ctx.user.display_name}-{ctx.user.id}")
            await ticket_channel.set_permissions(ctx.user, read_messages=True, send_messages=True)

            msg = Embed(title="Ticket", description="Bonjour, comment pouvons-nous vous aider ?", color=0x00ff00)
            msg.add_field(name="**Motif du ticket**", value=self.reason.value)
            msg.set_footer(text="Un modérateur peut fermer le ticket via la commande /close")

            await ticket_channel.send(embed=msg)

            await ctx.followup.send(f"Ticket ouvert dans {ticket_channel.mention} !", ephemeral=True)
        except Exception as e:
            await ctx.followup.send(f"Erreur: {e}\nVous avez certainement déjà un ticket ouvert.\nSi ce n'est pas le cas, contacte <@636217706210656276> en DM.", ephemeral=True)


    async def on_cancel(self, ctx: Interaction) -> None:
        await ctx.response.send_message("Ticket annulé", ephemeral=True)


@command(name="ticket", description="Crée un ticket pour demander de l'aide")
@has_role(CLIENT.config['admin_role'].id)
async def ticket(ctx: Interaction):
        try:
            channel: TextChannel = CLIENT.config['ticket_channel']
            
            msg = Embed(title="Ticket", description="Cliquez sur le bouton ci-dessous pour ouvrir un ticket.\nMerci d'éviter les abus.", color=0x00ff00)
            button = Button(style=ButtonStyle.success, label="🗃️ Ouvrir un ticket", custom_id='open_ticket')

            view = View()
            view.add_item(button)

            await channel.send(embed=msg, view=view)

            await ctx.response.send_message("Ticket créé avec succès !", ephemeral=True)

        except Exception as e:
            await ctx.response.send_message(f"Erreur: {e}", ephemeral=True)

@ticket.error
async def ticket_error(ctx: Interaction, error: Exception):
    await ctx.response.send_message(f"Erreur: {error}\nTu ne ne sembles pas avoir les permissions nécessaires pour ça...", ephemeral=True)

@command(name="close", description="Ferme un ticket")
@has_any_role(CLIENT.config['admin_role'].id, CLIENT.config['moderator_role'].id)
async def close(ctx: Interaction, message: Optional[str] = "Ticket fermé"):
    if ctx.channel.category.name == CLIENT.config['ticket_category'].name:
        await ctx.response.defer()

        user_id = int(ctx.channel.name.split('-')[-1])
        user = await ctx.guild.fetch_member(user_id)
        
        await ctx.channel.delete()
        await user.send(f"Votre ticket a été fermé par {ctx.user.display_name}.\nMessage: {message}")

# handle failure on role check
@close.error
async def close_error(ctx: Interaction, error: Exception):
    await ctx.response.send_message(f"Erreur: {error}\nTu ne ne sembles pas avoir les permissions nécessaires pour ça...", ephemeral=True)

async def handle_ticket_creation(ctx: Interaction):
    # Open a modal to ask the reason for opening a ticket
    await ctx.response.send_modal(TicketModal())
