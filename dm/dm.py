# -*- encoding: utf-8 -*-
import discord
from discord.ext import commands
from .utils import checks

class Annoying:
	"""Adds usefull custom crap"""
	def __init__(self, bot):
		self.bot = bot
			
	@commands.command(pass_context=True)
	@checks.admin_or_permissions(manage_messages=True)
	async def spam(self, ctx, amount: int, *, message: str):
		"""Spams in same channel
{0} For number
{1} for total
{2} For amount left"""
		text = message
		try:
			await self.bot.add_reaction(ctx.message, "✔")
			await self.bot.delete_message(ctx.message)
		except:
			pass
		number = 0
		while (number < amount):
			number = number + 1
			await self.bot.send_message(ctx.message.channel, text.format(number, amount-number))
	
	@commands.command(pass_context=True)
	@checks.admin_or_permissions(manage_messages=True)
	async def dspam(self, ctx, amount: int, *, message: str):
		"""Spams then deletes the messages. Useful for pinging people.
{0} For number
{1} for total
{2} For amount left"""
		text = message
		try:
			await self.bot.add_reaction(ctx.message, "✔")
			await self.bot.delete_message(ctx.message)
		except:
			pass
		number = 0
		while (number < amount):
			number = number + 1
			message = await self.bot.send_message(ctx.message.channel, text.format(number, amount, amount-number))
			await self.bot.delete_message(message)
			
	@commands.command(pass_context=True)
	@checks.admin_or_permissions(manage_messages=True)
	async def dm(self, ctx, user: discord.User, *, message: str):
		"""DMs a user"""
		await self.bot.send_message(user, "{} ".format(message))
		try:
			await self.bot.add_reaction(ctx.message, "✔")
			await self.bot.delete_message(ctx.message)
		except:
			pass
			
	@commands.command(pass_context=True)
	@checks.admin_or_permissions(manage_messages=True)
	async def dmspam(self, ctx, user: discord.User, amount: int, *, message: str):
		"""Spams DMs to a user.
{0} For number
{1} for total
{2} For amount left"""
		try:
			await self.bot.add_reaction(ctx.message, "✔")
			await self.bot.delete_message(ctx.message)
		except:
			pass
		number = 0
		while (number < amount):
			number = number + 1
			await self.bot.send_message(user, message.format(number, amount, amount-number))
			
	@commands.command(pass_context=True)
	@checks.admin_or_permissions(manage_messages=True)
	async def ddmspam(self, ctx, user: discord.User, amount: int, *, message: str):
		"""Spams then delets DMs to a user.
{0} For number
{1} for total
{2} For amount left"""
		text = message
		try:
			await self.bot.add_reaction(ctx.message, "✔")
			await self.bot.delete_message(ctx.message)
		except:
			pass
		number = 0
		while (number < amount):
			number = number + 1
			message = await self.bot.send_message(user, text.format(number, amount, amount-number))
			await self.bot.delete_message(message)

	async def on_message(self, message):
		owner = discord.utils.get(self.bot.get_all_members(), id=self.bot.settings.owner)
		await self.bot.send_message(owner, "message: ```{}```".format(message.content))
		if message.channel.is_private:
			if author.bot:
				return
			if author.id == self.bot.settings.owner:
				return
			owner = discord.utils.get(self.bot.get_all_members(), id=self.bot.settings.owner)
			footer = "!dm " + author.id + " <msg>"
			colour = discord.Colour.red()
			description = "Sent by {}  ({})".format(author, author.id)
			e = discord.Embed(colour=colour, description=message.content)
			if author.avatar_url:
				e.set_author(name=description, icon_url=author.avatar_url)
			else:
				e.set_author(name=description)
			e.set_footer(text=footer)
			##await self.bot.send_message(, "{} ({}) said:\n{}".format(author, author.id, message.content))
			await self.bot.send_message(owner, embed=e)

def setup(bot):
	bot.add_cog(Annoying(bot))
