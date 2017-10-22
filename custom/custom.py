import discord
from discord.ext import commands
from cogs.utils.dataIO import fileIO
from .utils import checks
import asyncio
import re
import os

class Custom:
	"""Adds  usefull custom crap"""
	def __init__(self, bot):
		self.bot = bot
		self.channels = fileIO("data/custom/channels.json", "load")
		
	@commands.command(pass_context=True)
	@checks.admin_or_permissions(manage_server=True)
	async def nuke(self, ctx):
		"""Cleans all messages from a channel."""
		await self.bot.pin_message(ctx.message)
		channel = ctx.message.channel
		tmp = ctx.message
		async for message in self.bot.logs_from(channel, limit=10,after=tmp):
			if message.author == ctx.message.server.me and message.content == '':
				await self.bot.delete_message(message)
		n = 0
		async for message in self.bot.logs_from(channel, limit=10000000,before=tmp):
			try:
				if (not ctx.message.pinned):
					break
				if (message.pinned):
					continue
				await self.bot.delete_message(message)
				n += 1
			except:
				pass
			tmp = message
		await self.bot.delete_message(ctx.message)
		print("Deleted {} messages from {}".format(n,channel))
			
	@commands.command(pass_context=True, no_pm=True)
	async def say(self, ctx, *, message):
		"""Says things"""
		try:
			await self.bot.delete_message(ctx.message)
			await self.bot.send_message(ctx.message.channel, "`{} said:` {}".format(ctx.message.author.name, message))
		except:
			pass

	@commands.command(pass_context=True, no_pm=True)
	@checks.serverowner_or_permissions(manage_server=True)
	async def alert(self, ctx, *, message):
		"""Says things"""
		try:
			await self.bot.delete_message(ctx.message)
			await self.bot.send_message(ctx.message.channel, message)
		except:
			pass

	@commands.command(pass_context=True, no_pm=True)
	@checks.serverowner_or_permissions(manage_server=True)
	async def pvt(self, ctx, user: discord.Member, user2: discord.User=None):
		"""Creates a private channel"""
		if user2 is None or not ctx.message.author.server_permissions.administrator: user2 = ctx.message.author
		server = ctx.message.server
		await self.bot.delete_message(ctx.message)
		try:
			user_perms = discord.PermissionOverwrite(read_messages=True)
			mine = discord.PermissionOverwrite(read_messages=True, manage_channels = True)
			created_channel = await self.bot.create_channel(server, "{}_{}".format(user.name, user2.name), (server.default_role, discord.PermissionOverwrite(read_messages=False)), (server.me, mine), (user, user_perms), (user2, user_perms))
			"""created_channel = await self.bot.create_channel(server, re.sub('\W+','', str(user) + str(user2) ))"""
		except discord.errors.Forbidden:
			await self.bot.say("No channel perms")
		try:
			"""perms = discord.PermissionOverwrite()
			perms.read_messages = True
			await self.bot.edit_channel_permissions(created_channel, user, perms)
			await self.bot.edit_channel_permissions(created_channel, user2, perms)
			perms.manage_channels = True
			await self.bot.edit_channel_permissions(created_channel, server.me, perms)
			perms = discord.PermissionOverwrite()
			perms.read_messages = False
			await self.bot.edit_channel_permissions(created_channel, discord.utils.get(server.roles, name='@everyone'), perms)"""
			msg = await self.bot.send_message(created_channel, "Private channel for {} and {}.".format(user.mention, user2.mention))
			"""for i in range(0, duration):
				await asyncio.sleep(1)
				await self.bot.edit_message(msg, "Channel will be deleted in {} seconds".format(duration-i))
			await self.bot.delete_channel(created_channel)"""
		except discord.errors.Forbidden:
			await self.bot.say("Error")

	async def member_join(self, member):
		"""member Join method"""
		server = member.server
		print("<> Member '{}' joined server '{}'. {}".format(member.name, server.name, server.member_count))
		for channel in self.channels:
			try:
				if self.channels[channel] and server.get_channel(channel).server == server:
					await self.bot.send_message(server.get_channel(channel), ":small_red_triangle: Welcome {0} (#{2})".format(member.mention, server, server.member_count))
			except AttributeError:
				pass
	   
	async def member_remove(self, member):
		"""member Join method"""
		server = member.server
		print("<> Member '{}' left server '{}'. {}".format(member.name, server.name, server.member_count))
		for channel in self.channels:
			try:
				if self.channels[channel] and server.get_channel(channel).server == server:
					await self.bot.send_message(server.get_channel(channel), ":small_red_triangle_down: Goodbye {0} ({2})".format(member, server, server.member_count))
			except AttributeError:
				pass
			
	@commands.command(pass_context=True, no_pm=True)
	@checks.is_owner()
	async def j(self, ctx, member: discord.User):
		"""member Join method"""
		ctx = member
		self.bot.dispatch("member_join", ctx)
		self.bot.dispatch("member_remove", ctx)
		"""
		server = member.server
		print("<> Member '{}' joined server '{}'. {}".format(member.name, server.name, server.member_count))
		print("<> Member '{}' left server '{}'. {}".format(member.name, server.name, server.member_count))
		for channel in self.channels:
			try:
				if self.channels[channel] and server.get_channel(channel).server == server:
					await self.bot.send_message(server.get_channel(channel), ":small_red_triangle: Welcome {0} (#{2})".format(member.mention, server, server.member_count))
				if self.channels[channel] and server.get_channel(channel).server == server:
					await self.bot.send_message(server.get_channel(channel), ":small_red_triangle_down: Goodbye {0} (#{2})".format(member, server, server.member_count))
			except AttributeError:
				pass"""

	@commands.command(pass_context=True, no_pm=True)
	@checks.is_owner()
	async def welcome(self, ctx, chan: discord.Channel=None):
		"""Toggles welcome messages for channel"""
		channel = ctx.message.channel
		if not chan == None:
			channel = chan
		await self.bot.delete_message(ctx.message)
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
		
	@commands.command(pass_context=True, no_pm=True)
	@checks.is_owner()
	async def welcomeList(self, ctx):
		server = ctx.message.server
		message = "Welcome channels:"
		for channel in self.channels:
			try:
				if server.get_channel(channel).server == server:
					message += "\n{} : {}".format(server.get_channel(channel).mention, self.channels[channel])
			except AttributeError:
				pass
		await self.bot.say(message)

	def save_channels(self):
		fileIO('data/custom/channels.json', 'save', self.channels)
		
def checks():
	if not os.path.exists("data/custom"):
		os.mkdir("data/custom")
	if not os.path.exists("data/custom/channels.json"):
		fileIO("data/custom/channels.json", "save", {})
		
def setup(bot):
	checks()
	bot.add_listener(Custom(bot).member_join,"on_member_join")
	bot.add_listener(Custom(bot).member_remove,"on_member_remove") 
	bot.add_cog(Custom(bot))
