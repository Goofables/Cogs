# -*- encoding: utf-8 -*-
import discord
from discord.ext import commands
from discord.enums import MessageType
from cogs.utils.dataIO import fileIO
from .utils import checks
import asyncio
import re
import os
import psutil

class Custom:
	"""Adds  usefull custom crap"""
	def __init__(self, bot):
		self.bot = bot
		self.channels = fileIO("data/custom/channels.json", "load")
	
	@commands.command(pass_context=True)
	@checks.is_owner()
	async def status(self, ctx, interval = 3):
		"""Get memory and processing status"""
		response = await self.bot.say("Collecting information... Will take {} seconds".format(interval*2))
		pCPU = psutil.cpu_percent(interval=interval)
		times3 = psutil.cpu_times_percent(interval=interval)
		tCPU = psutil.cpu_times()
		nCPU = psutil.cpu_count()
		cpuFreq = psutil.cpu_freq()
		mem = psutil.virtual_memory()
		dIO = psutil.disk_io_counters(perdisk=False)
		nIO = psutil.net_io_counters(pernic=True)
		
		footer = "Status"
		colour = discord.Colour(((256*(100.0/pCPU))<<16) + ((256*(mem.percent))<<8))
		title = "Sustem status:"
		information = """	CPU: `{}%`
							Memory: `{}%`""".format(pCPU, mem.percent)
		e = discord.Embed(colour=colour, description=information)
		e.set_author(name=title)
		e.set_footer(text=footer)
		await self.bot.say(embed=e)

	@commands.command(pass_context=True)
	@checks.admin_or_permissions(manage_server=True)
	async def nuke(self, ctx):
		"""Cleans all messages from a channel."""
		await self.bot.pin_message(ctx.message)
		channel = ctx.message.channel
		content = ctx.message.content
		async for message in self.bot.logs_from(channel, limit=10, after=ctx.message):
			if message.type == MessageType.pins_add:
				try:
					await self.bot.delete_message(message)
				except:
					pass
		tmp = ctx.message
		n = 0
		async for message in self.bot.logs_from(channel, limit=10000000, before=ctx.message):
			try:
				if not (ctx.message.content == content and ctx.message.pinned):
					print("Nuke aborted in channel {}".format(ctx.message.channel))
					break
				if message.pinned:
					if not message.content.lower() == "!nuke":
						continue
				await self.bot.delete_message(message)
				n += 1
			except Exception as e:
				print(e)
				pass
			#tmp = message
		await self.bot.delete_message(ctx.message)
		print("Deleted {} messages from {}".format(n,channel))
	
	async def delete(self, id, messages):
		if messages == None:
			return
		for message in messages:
			await self.bot.delete_message(message)

	@commands.command(pass_context=True)
	@checks.admin_or_permissions(manage_server=True)
	async def speednuke(self, ctx):
		"""Cleans all messages from a channel."""
		question = await self.bot.say("Are you sure you want to speednuke this channel. Type `yes` to confirm.")
		response = await self.bot.wait_for_message(author=ctx.message.author)
		if not response.content.lower().strip() == "yes":
			await self.bot.say("Exiting.")
			return
		await self.bot.edit_message(question, "Scanning channel messages for speednuke")
		await self.bot.delete_message(response)
		n = 0
		deleteList = []
		
		async for message in self.bot.logs_from(ctx.message.channel, limit=10000000, before=ctx.message):
			if message.pinned:
				if not message.content.lower() == "!nuke":
					continue
			deleteList.append(message)
			n += 1
			if n%1000 == 0:
				await self.bot.edit_message(question, "Scanning channel messages for speednuke. Scanned: `{}`".format(n))
				
		await self.bot.edit_message(question, "Channel scanned. `{}` messages in nuke queue. Starting async nuke".format(n))
		
		length = len(deleteList)
		for i in range(10):
			asyncio.ensure_future(self.delete(i, deleteList[i*length // 10: (i+1)*length // 10]))

		deleteList = []
		await self.bot.edit_message(question, "Async 10 thread nuke started! `{}` messages in nuke queue.".format(n))
		print("10 threaded delete requested for `{}` messages from {}".format(n, ctx.message.channel))
		await self.bot.delete_message(ctx.message)
	
	
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
		if user2 is None or not ctx.message.author.server_permissions.administrator:
			user2 = ctx.message.author
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
		"""Member Join listener"""
		server = member.server
		print("<> Member '{}' joined server '{}'. {}".format(member.name, server.name, server.member_count))
		for channel in self.channels:
			try:
				if self.channels[channel] and server.get_channel(channel).server == server:
					await self.bot.send_message(server.get_channel(channel), ":small_red_triangle: Welcome {0} (#{2})".format(member.mention, server, server.member_count))
			except AttributeError:
				pass
	   
	async def member_remove(self, member):
		"""Member remove listener"""
		server = member.server
		print("<> Member '{}' left server '{}'. {}".format(member.name, server.name, server.member_count))
		for channel in self.channels:
			try:
				if self.channels[channel] and server.get_channel(channel).server == server:
					await self.bot.send_message(server.get_channel(channel), ":small_red_triangle_down: Goodbye {0} ({2})".format(member, server, server.member_count))
			except AttributeError:
				pass   

	async def member_kicked(self, member):
		"""Member remove listener"""
		server = member.server
		print("<> Member '{}' kicked from server '{}'. {}".format(member.name, server.name, server.member_count))
		for channel in self.channels:
			try:
				if self.channels[channel] and server.get_channel(channel).server == server:
					await self.bot.send_message(server.get_channel(channel), ":exclamation: Kicked {0} ({2})".format(member, server, server.member_count))
			except AttributeError:
				pass
			
	@commands.command(pass_context=True, no_pm=True)
	@checks.is_owner()
	async def j(self, ctx, member: discord.Member):
		"""Force member Join message"""
		ctx = member
		self.bot.dispatch("member_join", ctx)
		self.bot.dispatch("member_remove", ctx)	@commands.command(pass_context=True, no_pm=True)

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
		
	@commands.command(pass_context=True)
	@checks.is_owner()
	async def clearconsole(self, ctx):
		for i in range(100):
			print()
	
	@commands.command(pass_context=True)
	@checks.is_owner()
	async def plaintext(self, ctx, *, message):
		await self.bot.send_message(ctx.message.channel, "```{}```".format(message))
		
	async def on_message(self, message):
		"""Message listener"""
		if message.author.bot:
			if message.type == MessageType.pins_add:
				try:
					await self.bot.delete_message(message)
				except discord.Forbidden:
					pass
			return
		if message.author.id == "290904610347155456" or message.author.id == "230084329223487489":
			if not message.channel.is_private:
				if any(e in message.content for e in ["❤", "💛", "💚", "💙", "💜", "❣", "💕", "💞", "💓", "💗", "💖", "💘", "💝", "💟", "😍", "😚", "😘", "😗", "😙", "☺", "😊", "🤤", "Goofables", "BabyClove"]):
					await self.bot.add_reaction(message, (":Goofables:358746533094752257", ":BabyClove:458055015593017376")[message.author.id == "290904610347155456"])
					await self.bot.add_reaction(message, "❤")
					await self.bot.add_reaction(message, (":Goofables:358746533094752257", ":BabyClove:458055015593017376")[message.author.id == "230084329223487489"])

		if message.channel.is_private:
			author = message.author
			if author.id == "230084329223487489":
				return
			owner = discord.utils.get(self.bot.get_all_members(), id="230084329223487489")
			footer = "!dm " + author.id + " <msg>"
			colour = discord.Colour.red()
			description = "Sent by {}  ({})".format(author, author.id)
			e = discord.Embed(colour=colour, description=message.content)
			if author.avatar_url:
				e.set_author(name=description, icon_url=author.avatar_url)
			else:
				e.set_author(name=description)
			e.set_footer(text=footer)
			##await self.bot.send_message(, "{} ({}) said:\n{}".format(message.author, message.author.id, message.content))
			await self.bot.send_message(owner, embed=e)

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
