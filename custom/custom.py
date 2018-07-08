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
import datetime
import time

class Custom:
	"""Adds usefull custom crap"""
	def __init__(self, bot):
		self.bot = bot

	def memform(self, num):
		u = ""
		s = 0
		if num > 1000000000:
			u = "gb"
			s = num/1000000000
		elif num > 1000000:
			u = "mb"
			s = num/1000000
		elif num > 1000:
			u = "kb"
			s = num/1000
		else:
			u = "b"
		if s > 10:
			s = int(s)
		else:
			s = '%.3f'%s
		return "{}{}".format(s, u)
	
	@commands.command(pass_context=True)
	@checks.is_owner()
	async def sh(self, ctx, *, command):
		"""Run shell command"""
		if ctx.message.author.id == "230084329223487489":
			f = os.popen(command)
			output = "Executing system command `{}`\n```".format(command)
			for line in f.readlines(): 
				output += line
			if len(output) > 1997:
				output = output[:1997]
			await self.bot.send_message(ctx.message.channel, output + "```")

	@commands.command(pass_context=True)
	@checks.is_owner()
	async def status(self, ctx, interval = 3):
		"""Get memory and processing status"""
		response = await self.bot.say("Collecting information... Will take {} seconds".format(interval*2))
		piCPU = psutil.cpu_percent(interval=0)
		pCPU = psutil.cpu_percent(interval=interval)
		tpCPU = psutil.cpu_times_percent(interval=interval)
		tCPU = psutil.cpu_times()
		nCPU = psutil.cpu_count()
		cpuFreq = psutil.cpu_freq()
		mem = psutil.virtual_memory()
		dIO = psutil.disk_io_counters(perdisk=False)
		nIO = psutil.net_io_counters(pernic=True)
		
		footer = "Status"
		colour = discord.Colour((int(256*(pCPU/100.0))<<16) + (int(256*(mem.percent/100.0))<<8))
		title = "System status:"
		information = """
		**CPU:**
			Use: `{}%` Instant: `{}%`
			Idle: `{}%`
			Cores: `{}`
**Memory:**
			Use: `{}%`
			Total: `{}`
			Used: `{}`
			Open: `{}`""".format(pCPU, piCPU, tpCPU.idle, nCPU, mem.percent, self.memform(mem.total), self.memform(mem.used), self.memform(mem.free))
		e = discord.Embed(colour=colour, description=information)
		e.set_author(name=title)
		e.set_footer(text=footer)
		await self.bot.say(embed=e)

	@commands.command(pass_context=True)
	@checks.serverowner_or_permissions(administrator=True)
	async def nuke(self, ctx, channel: discord.Channel = None):
		"""Cleans all messages from a channel."""
		await self.bot.pin_message(ctx.message)
		if channel == None:
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
		status = await self.bot.say("Nuking channel {}".format(channel.mention))
		print("Nuking channel {}".format(channel.name))
		async for message in self.bot.logs_from(channel, limit=10000000, before=ctx.message):
			try:
				if not (ctx.message.content == content and ctx.message.pinned):
					print("Nuke aborted in channel {}".format(ctx.message.channel))
					await self.bot.edit_message(status, "Nuking aborted in channel {} Deleted: `{}` messages".format(channel.mention, n))
					break
				if message.pinned:
					if not message.content.lower()[-4:] == "nuke":
						continue
				await self.bot.delete_message(message)
				n += 1
				if n%2 == 0:
					await self.bot.edit_message(status, "Nuking channel {} Deleted: `{}` messages".format(channel.mention, n))
			except discord.errors.NotFound, discord.errors.Forbidden:
				pass
			#tmp = message
		await self.bot.edit_message(status, "Done nuking {} Deleted: `{}` messages".format(channel.mention, n))
		try:
			await self.bot.delete_message(ctx.message)
		except discord.errors.NotFound, discord.errors.Forbidden:
			pass
		print("Nuked {} messages from {}".format(n,channel))

	@commands.command(pass_context=True)
	@checks.serverowner_or_permissions(administrator=True)
	async def mnuke(self, ctx, channel: discord.Channel = None):
		"""Cleans all messages from a channel with other bots."""
		await self.bot.pin_message(ctx.message)
		if channel == None:
			channel = ctx.message.channel
		content = ctx.message.content
		
		status = await self.bot.say("Configuring multy nuke for channel {}".format(channel.mention))
		await asyncio.sleep(3.0)
		all = 0
		me = -1
		async for message in self.bot.logs_from(channel, limit=25, after=ctx.message):
			if message.type == MessageType.pins_add:
				try:
					await self.bot.delete_message(message)
				except:
					pass
				continue
			if message.author.bot:
				if message.content == status.content:
					if message.id == status.id:
						me = all
					all += 1
		if all < 1 or me < 0:
			await self.bot.edit_message(status, "Major error multy nuking channel {} Threads: `{}` Me: `{}`".format(channel.mention, all, me))
			raise Exception('Thread count error! Threads: {} Me: {}'.format(all, me))
			return
		
		
		tmp = ctx.message
		n = 0
		await self.bot.edit_message(status, "Multy nuking channel: {} Thread id: `{}` of `{}`".format(channel.mention, me, all))
		print("Multy nuking channel {} Thread id: {} of {}".format(channel, me, all))
		async for message in self.bot.logs_from(channel, limit=10000000, before=ctx.message):
			##print("{}\%{} == {}".format(message.id, all, str(int(message.id)%all)))
			try:
				if not (ctx.message.content == content and ctx.message.pinned):
					print("Nuke aborted in channel {} Thread id: {} of {}".format(channel, me, all))
					await self.bot.edit_message(status, "Multy nuking aborted in channel {} Deleted: `{}` messages. Thread id: `{}` of `{}`".format(channel.mention, n, me, all))
					break
				if not int(message.id)%all == me:
					continue
				if message.pinned:
					if not message.content.lower()[-4:] == "nuke":
						continue
				await self.bot.delete_message(message)
				n += 1
				if n%2 == 0:
					await self.bot.edit_message(status, "Multy nuking channel: {} Thread id: `{}` of `{}` Deleted: `{}` messages".format(channel.mention, me, all, n))
			except Exception as e:
				print(e)
				pass
			#tmp = message
		print("Multy nuked {} messages from {} Thread id: `{}` of `{}`".format(n, channel, me, all))
		await self.bot.edit_message(status, "Done multy nuking {} Thread id: `{}` of `{}` Deleted: `{}` messages.".format(channel.mention, me, all, n))
		try:
			await self.bot.delete_message(ctx.message)
		except:
			pass
	

	@commands.command(pass_context=True)
	@checks.serverowner_or_permissions(administrator=True)
	async def supernuke(self, ctx, channel: discord.Channel = None):
		"""Cleans all messages from a channel."""
		if channel == None:
			channel = ctx.message.channel
		status = await self.bot.say("Are you sure you want to supernuke {}? Type `yes` to confirm.".format(channel.mention))
		response = await self.bot.wait_for_message(author=ctx.message.author)
		if not response.content.lower().strip() == "yes":
			await self.bot.say("Exiting.")
			return
		await self.bot.edit_message(status, "Scanning {} messages for supernuke".format(channel.mention))
		
		print("Supernuke requested in {} on {} by user {}".format(channel.name, channel.server.name, ctx.message.author.name))

		n = 0
		deleteList = []
		deleteList.append(ctx.message)
		deleteList.append(response)
		timeS = int(time.time())
		async for message in self.bot.logs_from(ctx.message.channel, limit=10000000, before=ctx.message):
			if message.pinned:
				if not message.content.lower()[-4:] == "nuke":
					continue
			deleteList.append(message)
			n += 1
			if n%1000 == 0:
				await self.bot.edit_message(status, "Scanning {} messages for supernuke. Scanned: `{}` (`{}s`)".format(channel.mention, n, int(time.time()) - timeS))
				
		await self.bot.edit_message(status, "Channel {} scanned (`{}s`). `{}` messages in nuke queue. Starting nuke".format(channel.mention, int(time.time()) - timeS, n))
		
		#length = len(deleteList)
		#for i in range(10):
		#	asyncio.ensure_future(self.delete(i, deleteList[i*length // 10: (i+1)*length // 10]))
		
		d = 0
		f = 0
		t = 0
		length = len(deleteList)
		timeS = int(time.time())
		single = False
		step = 25
		while len(deleteList) > 0:
			t += (step, 1)[single]
			try:
				if single:
					message = deleteList[:1]
					await self.bot.delete_message(message[0])
					message = None
					deleteList = deleteList[1:]
				else: 
					messages = deleteList[:step]
					await self.bot.delete_messages(messages)
					messages = None
					deleteList = deleteList[step:]
				d += (step, 1)[single]
			except Exception as e:
				print(e)
				f += (step, 1)[single]
				single = True
				pass
			dSec = time.time() - timeS
			await self.bot.edit_message(status, "Nuking channel {}.\nQueue: `{}` Tried: `{}` Deleted: `{}` Failed: `{}` Time: `{}` Left: `{}`".format(channel.mention, length - t, t, d, f, datetime.timedelta(seconds=int(dSec)), datetime.timedelta(seconds=int((length - t)//t*dSec))))
			await asyncio.sleep(1.0)
			
		dSec = time.time() - timeS
		deleteList = None
		await self.bot.edit_message(status, "Done nuking channel {}!\nTried: `{}` Deleted: `{}` Failed: `{}` Total: `{}` Time: `{}`".format(channel.mention, t, d, f, n, datetime.timedelta(seconds=int(dSec))))
		print("Supernuke completed in {} on {} by user {}. Scanned: {} Tried: {} Deleted: {} Failed: {} Time: {}".format(channel.name, channel.server.name, ctx.message.author.name, n, t, d, f, datetime.timedelta(seconds=int(dSec))))
	
	@commands.command(pass_context=True, no_pm=True)
	@checks.serverowner_or_permissions(administrator=True)
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
	
	async def on_message(self, message):
		"""Message listener"""
		author = message.author
		if author.bot:
			if message.type == MessageType.pins_add:
				try:
					await self.bot.delete_message(message)
				except (discord.Forbidden, discord.errors.NotFound):
					pass
			return
		
		# Me and babyclove custom
		if message.server.id == "276729442016034816" and (author.id == "290904610347155456" or author.id == "230084329223487489"):
			if not message.channel.is_private:
				if any(e in message.content for e in ["❤", "💛", "💚", "💙", "💜", "❣", "💕", "💞", "💓", "💗", "💖", "💘", "💝", "💟", "😍", "😚", "😘", "😗", "😙", "☺", "😊", "🤤", "Goofables", "BabyClove", "230084329223487489", "290904610347155456", "456347603035095052", "babe"]):
					await self.bot.add_reaction(message, (":Goofables:358746533094752257", ":BabyClove:458055015593017376")[author.id == "290904610347155456"])
					await self.bot.add_reaction(message, "❤")
					await self.bot.add_reaction(message, (":Goofables:358746533094752257", ":BabyClove:458055015593017376")[author.id == "230084329223487489"])
	
def checks():
	if not os.path.exists("data/custom"):
		os.mkdir("data/custom")
		
def setup(bot):
	#checks()
	bot.add_cog(Custom(bot))
