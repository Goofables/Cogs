# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord.enums import ChannelType
from time import sleep
from .utils import checks
import asyncio
import re
import os

class Filter:
	"""Deletes all filtered messages messages."""
	def __init__(self, bot):
		self.bot = bot
		self.regs = [
	[re.compile("((.*(^|[\W_\d]+)[d]+[\W_\d]*[(e|3|è|é|ê|ë|ē|ė|ę)]+[\W_\d]*[d]+([\W_\d]+|ing|ed|er|$))|^d+e+(a*e*)*d+$)"), 50, ""],
	[re.compile("(^|.*[\W_\d ]+)l+[\W_\d]*[yi]+[\W_\d]*d+[\W_\d]*[iay]+($|[\W_\d]+)"), 2000, "friends"],
	[re.compile("(^|.*[\W_\d ]+)g+[\W_\d]*[aeiy]+[\W_\d]*l+[\W_\d]*[eiya]+[\W_\d]*n+($|[\W_\d]+)"), 2000, "friends"]
		]
	
	def fmt(self, message:discord.Message):
		return "{} #{} @{} >> \"{}\"".format(message.timestamp.strftime("%Y-%m-%d %H:%M:%S"), message.id, message.author, message.content)
		
	def check(self, message:discord.Message):
		msgLen = len(message.content)
		for reg, max, channels in self.regs:
			if msgLen > max or (channels is not None and message.channel.name.lower() in channels):
				continue
			#print("`{}` checked with {} got {}".format(message.content.lower(), max, reg.match(message.content.lower())))
			if reg.match(message.content.lower()):
				return True
		return False
	
	async def delete(self, message:discord.Message):
		try:
			await self.bot.add_reaction(message, "👎")
			sleep(1)
			await self.bot.delete_message(message)
		except discord.Forbidden:
			return False
		return True
	
	@commands.group(pass_context=True)
	@checks.mod_or_permissions(manage_messages=True)
	async def dednuker(self, ctx):
		"""Finds all filtered messages"""
		if ctx.invoked_subcommand is None:
			await ctx.invoke(self.channel_dednuker, False, ctx.message.channel)
	
	@dednuker.command(name="channel", pass_context=True)
	@checks.mod_or_permissions(manage_messages=True)
	async def channel_dednuker(self, ctx, delete: bool = False, channel: discord.Channel = None, user: discord.User = None):
		"""Finds all `ded` messages in a channel."""
		if channel is None:
			channel = ctx.message.channel
		status = await self.bot.send_message(ctx.message.channel, "Scanning channel {} Delete: `{}`".format(channel.mention, delete))
		total = {"scanned" : 0, "found" : 0, "deleted" : 0}
		msg = "\n```"
		tmp = status
		try:
			async for message in self.bot.logs_from(channel, limit=10000000, before=None):
				total["scanned"] += 1
				if total["scanned"]%1000 == 0:
					await self.bot.edit_message(status, "Scanning channel {} Delete: `{}` Scanned: `{}` Found: `{}`".format(channel.mention, delete, total["scanned"], total["found"]))
				
				if user and not message.author == user:
					continue
				tmp = message
				if self.check(message):
					total["found"] += 1
					msg += "\n"+self.fmt(message)
					if message.pinned:
						continue
					await self.bot.add_reaction(message, "👎")
					if delete:
						try:
							await self.bot.delete_message(message)
							total["deleted"] += 1
						except:
							delete = None
		except discord.Forbidden:
			await self.bot.edit_message(status, "No read permissions for channel {}".format(channel.mention))
		if not tmp == status:
			await self.bot.pin_message(tmp)
		msg += "```"
		if msg == "\n``````":
			msg = ""
		msg = "Channel: {} Messages: `{}` Found: `{}` Deleted: `{}` {} {}".format(channel.mention, total["scanned"], total["found"], total["deleted"], ("", "Cant delete")[delete == None], msg)
		while len(msg) > len("Channel: {} continued ``````".format(channel.mention)):
			await self.bot.send_message(ctx.message.channel, msg[0:1997] + "```")
			msg = "Channel: {} continued ```{}".format(channel.mention, msg[1997:-3])
		try:
			await self.bot.delete_message(status)
		except discord.Forbidden:
			pass
		return total
	
	@dednuker.command(name="server", pass_context=True)
	@checks.admin_or_permissions(administrator=True)
	async def server_dednuker(self, ctx, delete: bool = False, user: discord.User = None, server:discord.Server = None):
		if server is None or server is "this":
			server = ctx.message.server
		total = {"scanned" : 0, "channels" : 0, "found" : 0, "ch" : 0, "deleted" : 0}
		for channel in server.channels:
			if "_console" in channel.name or channel.type == ChannelType.voice or channel.type == ChannelType.group:
				continue
			total["channels"] += 1
			try:
				ret = await ctx.invoke(self.channel_dednuker, delete, channel, user)
				total["scanned"] += ret["scanned"]
				total["found"] += ret["found"]
				total["deleted"] += ret["deleted"]
			except discord.Forbidden:
				pass
			
		msg = "Done scanning `{}`".format(server.name)
		msg += "\nScanned `{}` messages in `{}` channels in this servers.".format(total["scanned"], total["channels"])
		msg += "\nFound `{}` matches in `{}` channels.".format(total["found"], total["ch"])
		msg += "\nDeleted `{}` matches".format(total["deleted"])
		await self.bot.send_message(ctx.message.channel, msg)
		return total
	
	@dednuker.command(name="global", pass_context=True)
	@checks.is_owner()
	async def global_dednuker(self, ctx, delete: str = False, user: discord.User = None):
		total = {"scanned" : 0, "channels" : 0, "servers" : 0, "found" : 0, "ch" : 0, "deleted" : 0}
		for server in self.bot.servers:
			total["servers"] += 1
			await self.bot.send_message(ctx.message.channel, "Server: `{}`".format(server.name))
			try:
				ret = await ctx.invoke(self.server_dednuker, delete, user, server)
				total["scanned"] += ret["scanned"]
				total["found"] += ret["found"]
				total["deleted"] += ret["deleted"]
				total["ch"] += ret["ch"]
				total["channels"] += ret["channels"]
			except discord.Forbidden:
				pass
		msg = "**Done scanning all servers!**"
		msg += "\nScanned `{}` messages in `{}` channels in `{}` servers.".format(total["scanned"], total["channels"], total["servers"])
		msg += "\nFound `{}` matches in `{}` channels.".format(total["found"], total["ch"])
		msg += "\nDeleted `{}` matches.".format(total["deleted"])
		await self.bot.send_message(ctx.message.channel, msg)
	
	async def on_message(self, message):
		"""Message listener"""
		if message.author.bot:
			return
		if message.author.id in ["290904610347155456", "230084329223487489"]:
			return
		if self.check(message):
			await self.delete(message)
	
	async def on_message_edit(self, old_msg, message):
		"""Message edit listener"""
		if message.author.bot:
			return
		if message.author.id in ["290904610347155456", "230084329223487489"]:
			return
		if self.check(message):
			await self.delete(message)
	
def setup(bot):
	bot.add_cog(Filter(bot))
