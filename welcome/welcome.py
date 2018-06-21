# -*- encoding: utf-8 -*-
import discord
from discord.ext import commands
from cogs.utils.dataIO import fileIO
from .utils import checks
import asyncio
import os

class Welcome:
	"""Welcome channels"""
	def __init__(self, bot):
		self.bot = bot
		self.channels = fileIO("data/welcome/channels.json", "load")
		self.messages = {"joined" : ":small_red_triangle: Welcome {0} (#{2})", "left" : ":small_red_triangle_down: Goodbye `{0}` (Members: {2})", "banned" : ":no_entry: `{0}` has been banned! (Members: {2})"}
		
	async def sendWelcome(self, member, server, action):
		print("<> Member '{}' {} server '{}'. {}".format(member.name, action, server.name, server.member_count))
		for channel in self.channels:
			try:
				if self.channels[channel] and server.get_channel(channel).server == server:
					await self.bot.send_message(server.get_channel(channel), self.messages[action].format((member.name, member.mention)[action == "joined"], server, server.member_count))
			except AttributeError:
				pass
	
	async def member_join(self, member):
		"""Member Join listener"""
		await self.sendWelcome(member, member.server, "joined")
	
	async def member_remove(self, member):
		"""Member remove listener"""
		await self.sendWelcome(member, member.server, "left")
	
	async def member_ban(self, member):
		"""Member ban listener"""
		await self.sendWelcome(member, member.server, "banned")
	
	@commands.command(pass_context=True, no_pm=True)
	@checks.admin_or_permissions(manage_server=True)
	async def joinleave(self, ctx, member: discord.Member):
		"""Force member Join message"""
		ctx = member
		self.bot.dispatch("member_join", ctx)
		self.bot.dispatch("member_remove", ctx)

	@commands.group(pass_context=True, no_pm=True)
	@checks.admin_or_permissions(manage_server=True)
	async def welcome(self, ctx):
		"""Manage channels for welcome messages"""
		if ctx.invoked_subcommand is not None:
			return
		server = ctx.message.server
		message = "Welcome channels:"
		for channel in self.channels:
			try:
				if server.get_channel(channel).server == server:
					message += "\n{} : {}".format(server.get_channel(channel).mention, self.channels[channel])
			except AttributeError:
				pass
		await self.bot.say(message)
		
	@welcome.command(name="toggle", pass_context=True, no_pm=True)
	async def toggle_welcome(self, ctx, channel: discord.Channel=None):
		"""Toggles welcome messages for channel"""
		if channel == None:
			channel = ctx.message.channel
		if channel.id not in self.channels:
			self.channels[channel.id] = True
		else:
			self.channels[channel.id] = not self.channels[channel.id]
		if self.channels[channel.id]:
			await self.bot.say('Welcome enabled for {}'.format(channel.mention))
		else:
			await self.bot.say('Welcome disabled for {}'.format(channel.mention))
			del self.channels[channel.id]
		self.save_channels()
		self.channels = fileIO("data/custom/channels.json", "load")

	def save_channels(self):
		fileIO('data/welcome/channels.json', 'save', self.channels)
		
def checks():
	if not os.path.exists("data/welcome"):
		os.mkdir("data/welcome")
	if not os.path.exists("data/welcome/channels.json"):
		fileIO("data/welcome/channels.json", "save", {})
		
def setup(bot):
	checks()
	wbot = Welcome(bot)
	bot.add_listener(wbot.member_join,"on_member_join")
	bot.add_listener(wbot.member_remove,"on_member_remove") 
	bot.add_listener(wbot.member_ban,"on_member_ban") 
	bot.add_cog(wbot)
