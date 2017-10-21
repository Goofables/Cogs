import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
import asyncio
import os

class Antided:
    """Deletes all `ded` messages."""
    
    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json("data/Antided/settings.json", "load")
        self.channels = dataIO.load_json("data/Antided/channels.json", "load")
        
    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def toggleded(self, ctx):
        """Toggles antided in current channel"""
        channel = ctx.message.channel
        
    @commands.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def antided(self, ctx):
        server = ctx.message.server
        message = "Welcome channels:"
        for channel in self.channels:
            try:
                if server.get_channel(channel).server == server:
                    message += "\n{} : {}".format(server.get_channel(channel).mention, self.channels[channel])
            except AttributeError:
                pass
        await self.bot.say(message)
    async def on_message(self, message):
        """Message listener"""
        if message.content is "ded":
            await self.bot.delete_message(message)
    
    def save(self):
        dataIO.save_json('data/Antided/channels.json', self.channels)
        dataIO.save_json('data/Antided/settings.json', self.settings)
        
def checks():
    if not os.path.isdir("data/Antided"):
        os.mkdir("data/Antided")
    if not dataIO.is_valid_json("data/Antided/channels.json"):
        dataIO.save_json("data/Antided/channels.json", {})
    if not dataIO.is_valid_json("data/Antided/settings.json"):
        dataIO.save_json("data/Antided/settings.json", {})
        
def setup(bot):
    checks()
    me = Antided(bot)
    bot.add_listener(me.on_message,"on_message")
    bot.add_cog(me)
