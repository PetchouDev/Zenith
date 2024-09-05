from discord import Interaction, ButtonStyle, Embed, TextStyle
from discord.app_commands import command
from discord.app_commands.checks import has_any_role
from discord.ui import Button, View, Modal, TextInput

from core.client import CLIENT

class RoomName(Modal, title="Nom de la catégorie privée"):
    name = TextInput(label="Nom", placeholder="Nom de la catégorie", max_length=50, style=TextStyle.short)

    async def on_submit(self, ctx: Interaction) -> None:
        # Créer une catégorie de salon privé
        await ctx.response.defer()
        try:
            # create the category
            category = await ctx.guild.create_category(self.name.value)


            # Make the category private (hide it from @eevryone and @user)
            await category.set_permissions(ctx.guild.default_role, view_channel=False)
            await category.set_permissions(CLIENT.config['user_role'], view_channel=False)
            
            # Overriding the permissions to allow the user to create channels and add members to his room
            await category.set_permissions(
                ctx.user, 
                view_channel=True, 
                manage_channels=True, 
                manage_roles=True,
            )
            # create a channel with the close button to delete the category that is visible only to the user (no matter if he has added other people in the room) and where he can't send messages
            delete_channel = await category.create_text_channel("〈❌〉close")
            await delete_channel.set_permissions(ctx.user, read_messages=True, send_messages=False, manage_channels=False, manage_permissions=False)
            await delete_channel.set_permissions(ctx.guild.default_role, view_channel=False)
            await delete_channel.set_permissions(CLIENT.config['user_role'], view_channel=False)

            # Send an embed message with the close button in the delete channel
            msg = Embed(title="Catégorie privée - " + self.name.value, description="Cliquez sur le bouton ci-dessous pour fermer la catégorie privée.\nCette action est irréversible.", color=0x00ff00)
            msg.add_field(name="**Attention**", value="Si vous autorisez un autre membre à accéder à ce salon, il pourra supprimer la catégorie et tous les salons qu'elle contient.")

            button = Button(style=ButtonStyle.danger, label="❌ Fermer la catégorie", custom_id='close_room')
            view = View()
            view.add_item(button)
            await delete_channel.send(embed=msg, view=view)

            # send the success message            
            await ctx.followup.send(f"Catégorie {category.name} créée avec succès !", ephemeral=True)
        except Exception as e:
            await ctx.followup.send(f"Erreur: {e}", ephemeral=True)

    async def on_cancel(self, ctx: Interaction) -> None:
        await ctx.response.send_message("Création annulée", ephemeral=True)

class DeletionConfirmation(Modal, title="Confirmation de suppression"):
    confirm = TextInput(label="Tapez 'CONFIRMER' pour supprimer la room.", placeholder="CONFIRMER", style=TextStyle.short, max_length=9)
    
    async def on_submit(self, ctx: Interaction) -> None:
        if self.confirm.value != "CONFIRMER":
            await ctx.response.send_message("Erreur: La confirmation est incorrecte.", ephemeral=True)
            return
        # Delete the category
        await ctx.response.defer()
        try:
            # Get the category
            category = ctx.channel.category

            # delete all the channels in the category
            for channel in category.channels:
                await channel.delete()

            # delete the category
            await category.delete()

            # send the success message
            await ctx.user.send(f"Catégorie {category.name} a été supprimée avec succès !")

        except Exception as e:
            await ctx.followup.send(f"Erreur: {e}", ephemeral=True)

    async def on_cancel(self, ctx: Interaction) -> None:
        await ctx.response.send_message("Suppression annulée", ephemeral=True)

# handle room deletion
async def handle_room_deletion(ctx: Interaction):
    # send a modal to confirm the deletion
    await ctx.response.send_modal(DeletionConfirmation())

# handle category creation
async def handle_room_creation(ctx: Interaction):
    # Send the modal to ask the name of the category
    await ctx.response.send_modal(RoomName())

# Send a embed with a button to create a private room
@command(name="room", description="Envoie un bouton pour créer une catégorie privée")
@has_any_role(CLIENT.config['admin_role'].id, CLIENT.config['moderator_role'].id)
async def room(ctx: Interaction):
    # Build the embed message
    msg = Embed(title="Catégorie privée", description="Un devoir a faire en groupe ? Une LAN League of Legends endiablée ? Pas de souis, vous pouvez profiter d'un salon privé !", color=0x00ff00)
    msg.add_field(name="**Comment faire ?**", value="Cliquez sur le bouton ci-dessous pour créer une catégorie privée.", inline=False)
    msg.add_field(name="**Note**", value="Les catégories privées sont visibles uniquement par les membres qui y ont accès, ainsi que la modération.", inline=False)
    msg.set_footer(text="Les règles du serveur s'appliquent également dans les catégories privées, avec une certaine tolérance selon le contexte.")

    # Build the button
    button = Button(style=ButtonStyle.danger, label="🔒 Créer une catégorie privée", custom_id='create_room')
    view = View()
    view.add_item(button)

    # Send the message
    await ctx.response.send_message(embed=msg, view=view)

# handle failure on role check
@room.error
async def room_error(ctx: Interaction, error: Exception):
    await ctx.response.send_message(f"Erreur: {error}\nTu ne ne sembles pas avoir les permissions nécessaires pour ça...", ephemeral=True)