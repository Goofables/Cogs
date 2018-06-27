# -*- encoding: utf-8 -*-
import discord
from discord.ext import commands
from .utils import checks

class Useful:
	"""Adds usefull custom crap"""
	def __init__(self, bot):
		self.bot = bot
		
	@commands.command(pass_context=True, no_pm=True)
	async def say(self, ctx, *, message):
		"""Says things from a user"""
		try:
			await self.bot.delete_message(ctx.message)
		except:
			pass
		await self.bot.send_message(ctx.message.channel, "`{} said:` {}".format(ctx.message.author.name, message))
	
	@commands.command(pass_context=True, no_pm=True)
	async def ping(self, ctx):
		"""Pong!"""
		await self.bot.say("Pong!")

	@commands.command(pass_context=True, no_pm=True)
	@checks.admin_or_permissions(manage_server=True)
	async def alert(self, ctx, *, message):
		"""Says things as bot"""
		try:
			await self.bot.delete_message(ctx.message)
		except:
			pass
		await self.bot.send_message(ctx.message.channel, message)

	@commands.command(pass_context=True)
	@checks.is_owner()
	async def clearc(self, ctx, lines: int = 50):
		"""Print blank lines to console"""
		for i in range(lines):
			print()
			
	@commands.command(pass_context=True)
	@checks.is_owner()
	async def pin(self, ctx, message:discord.Message):
		await self.bot.pin_message(message)
		await self.bot.say("Pinned message. Channel: {}".format(message.channel.mention))
	
	@commands.command(pass_context=True)
	@checks.admin_or_permissions(manage_server=True)
	async def plaintext(self, ctx, *, message):
		"""Show message in plaintext"""
		await self.bot.send_message(ctx.message.channel, "```{}```".format(message))
		
def setup(bot):
	bot.add_cog(Useful(bot))
