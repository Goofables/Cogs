# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from time import sleep
from .utils import checks
import asyncio
import re
import os

class Antided:
	"""Deletes all `ded` messages."""
	def __init__(self, bot):
		self.bot = bot
		self.regex = re.compile("((.*(^|[\W_\d]+)d[\W_\d]*e[\W_\d]*d([\W_\d]+|ing|ed|er|$))|^dead$)")
	
	def fmt(self, message:discord.Message):
		return "\n{} #{} @{} >> \"{}\"".format(message.timestamp.strftime("%Y-%m-%d %H:%M:%S"), message.id, message.author, message.content)

	@commands.group(pass_context=True)
	@checks.mod_or_permissions(manage_messages=True)
	async def dednuker(self, ctx):
		"""Finds all `ded` messages"""
		if ctx.invoked_subcommand is None:
			await ctx.invoke(self.channel_dednuker, False, ctx.message.channel)

	@dednuker.command(name="channel", pass_context=True)
	@checks.mod_or_permissions(manage_messages=True)
	async def channel_dednuker(self, ctx, delete: str = False, channel: discord.Channel = None, user: discord.User = None):
		"""Finds all `ded` messages in a channel."""
		if channel is None:
			channel = ctx.message.channel
		total = {"messages" : 0, "msg" : 0}
		msg = "```"
		async for message in self.bot.logs_from(channel, limit=10000000, before=None):
			total["messages"] += 1
			if user and not message.author == user:
				continue
			if self.regex.match(message.content.lower()) and len(message.content) < 20:
				total["msg"] += 1
				msg += self.fmt(message)
				if message.pinned:
					continue
				await self.bot.add_reaction(message, "👎")
				if delete:
					try:
						await self.bot.delete_message(message)
					except discord.Forbidden:
						pass
		msg += "```"
		if not msg == "``````":
			msg = "Channel: {} Messages: `{}`\n{}".format(channel.mention, total["msg"], msg)
			if len(msg) > 2000:
				await self.bot.send_message(stx.message.channel, "Error too long!")
			await self.bot.send_message(ctx.message.channel, msg)
		msg = "Done!"
		msg += "\nScanned `{}` messages in this channels.".format(total["messages"])
		msg += "\nFound `{}` matches.".format(total["msg"])
		await self.bot.send_message(ctx.message.channel, msg)

	
	@dednuker.command(name="server", pass_context=True)
	@checks.admin_or_permissions(administrator=True)
	async def server_dednuker(self, ctx, delete: str = False, user: discord.User = None):
		server = ctx.message.server
		total = {"messages" : 0, "channels" : 0, "msg" : 0, "ch" : 0}
		for channel in server.channels:
			total["channels"] += 1
			inCh = 0
			msg = "```"
			try:
				async for message in self.bot.logs_from(channel, limit=10000000, before=None):
					total["messages"] += 1
					if user and not message.author == user:
						continue
					if self.regex.match(message.content.lower()) and len(message.content) < 20:
						total["msg"] += 1
						inCh += 1
						msg += self.fmt(message)
						if message.pinned:
							continue
						await self.bot.add_reaction(message, "👎")
						if delete:
							try:
								await self.bot.delete_message(message)
							except discord.Forbidden:
								pass
			except discord.Forbidden:
				pass
			msg += "```"
			if not msg == "``````":
				total["ch"] += 1
				msg = "Channel: {} Messages: `{}`\n{}".format(channel.mention, inCh, msg)
				if len(msg) > 2000:
					await self.bot.send_message(stx.message.channel, "Error too long!")
				await self.bot.send_message(ctx.message.channel, msg)
		msg = "Done!"
		msg += "\nScanned `{}` messages in `{}` channels in this servers.".format(total["messages"], total["channels"])
		msg += "\nFound `{}` matches in `{}` channels.".format(total["msg"], total["ch"])
		await self.bot.send_message(ctx.message.channel, msg)
		

	@dednuker.command(name="global", pass_context=True)
	@checks.is_owner()
	async def global_dednuker(self, ctx, delete: str = False, user: discord.User = None):
		total = {"messages" : 0, "channels" : 0, "servers" : 0, "msg" : 0, "ch" : 0}
		for server in self.bot.servers:
			total["servers"] += 1
			await self.bot.send_message(ctx.message.channel, "Server: `{}`".format(server.name))
			for channel in server.channels:
				total["channels"] += 1
				inCh = 0
				msg = "```"
				try:
					async for message in self.bot.logs_from(channel, limit=10000000, before=None):
						total["messages"] += 1
						if user and not message.author == user:
							continue
						if self.regex.match(message.content.lower()) and len(message.content) < 20:
							total["msg"] += 1
							inCh += 1
							msg += self.fmt(message)
							if message.pinned:
								continue
							await self.bot.add_reaction(message, "👎")
				except discord.Forbidden:
					pass
				msg += "```"
				if not msg == "``````":
					total["ch"] += 1
					msg = "Channel: {} Messages: `{}`\n{}".format(channel.mention, inCh, msg)
					if len(msg) > 2000:
						await self.bot.send_message(stx.message.channel, "Error too long!")
					await self.bot.send_message(ctx.message.channel, msg)
		msg = "Done!"
		msg += "\nScanned `{}` messages in `{}` channels in `{}` servers.".format(total["messages"], total["channels"], total["servers"])
		msg += "\nFound `{}` matches in `{}` channels.".format(total["msg"], total["ch"])
		await self.bot.send_message(ctx.message.channel, msg)
		

	
	async def on_message(self, message):
		"""Message listener"""
		if message.author.bot:
			return
		if self.regex.match(message.content.lower()):
			await self.bot.add_reaction(message, "👎")
			"""overwrites = channel.overwrites_for(message.author)
			overwrites.send_messages = False
			try:
				await self.bot.edit_channel_permissions(channel, user, overwrites)
			except discord.Forbidden:"""
			sleep(1)
			await self.bot.delete_message(message)
			"""sleep(10)
			overwrites.send_messages = False
			try:
				await self.bot.edit_channel_permissions(channel, user, overwrites)
			except discord.Forbidden:
				pass"""

def setup(bot):
	bot.add_cog(Antided(bot))
