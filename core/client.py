import os
import json
from typing import Tuple

from discord import Client, Intents
from discord.app_commands import Command, CommandTree

# Get the config
from data.config import load_config

# Set the intents
intents = Intents.all()

class Client(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(intents=intents, *args, **kwargs)
        self.token = None
        self.tree = CommandTree(self)
        self.config = None

        if os.path.exists('data/xp.json'):
            self.xp: dict = json.load(open('data/xp.json'))
            # Convert the keys to integers
            self.xp = {int(key): value for key, value in self.xp.items()}

        else:
            self.xp = {}
            open('data/xp.json', 'w').write('{}')

    def wake_up(self, token):
        # Run the bot
        self.run(token)

    async def load_commands(self):
        # import the commands module
        import commands
        # Get all named imported from the commands module
        cmd = []
        for name in dir(commands):
            obj = getattr(commands, name)
            if isinstance(obj, Command):
                cmd.append(obj)

        # Add the commands to the tree
        for command in cmd:
            self.tree.add_command(command)
            print(f"Added command {command.name} to the tree")

        await self.tree.sync()


    async def on_ready(self):
        # Load the config
        self.config = await load_config(self)

        # Load the commands
        await self.load_commands()

        print(f'{self.user} has connected to Discord!')

    def get_user_level(self, user_id) -> Tuple[int, int, int]:
        # Create the entry if it doesn't exist
        if user_id not in self.xp:
            self.xp[user_id] = 0

        # Get the level of the user (levels needs to be calculated with the Fibonacci sequence)
        level = 0
        prev_xp_needed = 100
        xp_needed = 100
        remaning_xp = self.xp[user_id]
        while remaning_xp >= xp_needed:
            level += 1
            remaning_xp -= xp_needed
            prev_xp_needed, xp_needed = xp_needed, prev_xp_needed + xp_needed

        return level, remaning_xp, xp_needed

    def add_xp(self, user_id, xp) -> bool:
        # Create the entry if it doesn't exist
        if user_id not in self.xp:
            self.xp[user_id] = 0

        # Monitor the level up
        level, remaning_xp, xp_needed = self.get_user_level(user_id)

        # Add the xp
        self.xp[user_id] += xp

        # Check if the user leveled up
        level_up = False
        if remaning_xp + xp >= xp_needed:
            level_up = True

        # Save the xp
        json.dump(self.xp, open('data/xp.json', 'w'))

        return level_up

CLIENT = Client()
        
        