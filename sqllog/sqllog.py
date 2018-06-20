# -*- encoding: utf-8 -*-
import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
import os
import pymysql
import logging


class SQLlog:
	"""Loggs messages to MySQL server"""
	def __init__(self, bot):
		self.bot = bot
	
	async def on_message(self, message):
		"""Message listener"""
		try:
			if "_console" in message.channel.name:
				if message.author.bot:
					return
		except:
			logger.info("{} {} {}".format(message.channel, message.author, message.content))
			return
		##logger.info("#{}  @{}  '{}'".format(message.channel, message.author, message.content))
		await self.log_message(message)
		
	async def log_message(self, message):
		try:
			if "_console" in message.channel.name:
				if message.author.bot:
					return
			query = """INSERT INTO `{0.channel.id}` (
			`id`, `author.id`, `author.name`, `content`, `timestamp`, `type`, `attachments`, `embeds`
			) VALUES (
			'{0.id}', '{0.author.id}', '{1}', '{2}', '{0.timestamp}', '{0.type}', '{3}', '{4}'
			)""".format(message,
						message.author.name.replace("\\","\\\\").replace("'","\\'"),
						message.content.replace("\\","\\\\").replace("'","\\'"),
						str(message.attachments).replace("\\","\\\\").replace("'","\\'"),
						str(message.embeds).replace("\\","\\\\").replace("'","\\'"),
						).encode('utf-8')
			try:
				cursor.execute(query)
			except UnicodeEncodeError:
				logger.info("Couldn't log message \"{}\"".format(message.content))
				return
			except pymysql.err.IntegrityError:
				return
			except pymysql.err.ProgrammingError as pe:
				if not cursor.execute("SHOW TABLES LIKE '{}'".format(message.channel.id)):
					logger.info("Table `{0.id}` ({0.name}) does not exist! Creating now...".format(message.channel))
					makedb = """CREATE TABLE `{}`.`{}` (
						`id` BIGINT(18) NOT NULL ,
						`author.id` BIGINT(18) NOT NULL ,
						`author.name` TINYTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL ,
						`content` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL ,
						`timestamp` TIMESTAMP NOT NULL ,
						`type` TINYTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL ,
						`attachments` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL ,
						`embeds` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL ,
						PRIMARY KEY (`id`)) ENGINE = MyISAM;""".format(login["db"], message.channel.id)
					cursor.execute(makedb)
					if cursor.execute("SHOW TABLES LIKE '{}'".format(message.channel.id)):
						logger.info("Success! Table `{0.id}` ({0.name}) created!".format(message.channel))
						cursor.execute(query)
					else:
						logger.info("Error! Table `{0.id}` ({0.name}) could not be created!".format(message.channel))
						await self.bot.send_message(discord.utils.get(self.bot.get_all_members(), id=self.bot.settings.owner), "Error! Table `{0.id}` ({0.name}) could not be created!".format(message.channel))
				else:
					logger.info("Error! Couldnt log message!")
					logger.info("`{0.timestamp}` > `{0.server.id}` > `{0.channel.id}` > > `{0.id}` > `{0.author}` > `{0.call}` > `{0.type}` > \"{0.content}\"".format(message))
					await self.bot.send_message(discord.utils.get(self.bot.get_all_members(), id=self.bot.settings.owner), "`{0.timestamp}` > `{0.server.id}` > `{0.channel.id}` > > `{0.id}` > `{0.author}` > `{0.call}` > `{0.type}` > \"{0.content}\"".format(message))
					logger.info("ProgrammingError ({0}): {1}".format(pe.strerror))
		except discord.errors.NotFound:
			pass

	@commands.command(pass_context=True)
	@checks.is_owner()
	async def logall(self, ctx):
		await self.bot.say("Are you sure you want to log all messages to sql server?"
						   " Type `yes` to confirm.")
		response = await self.bot.wait_for_message(author=ctx.message.author)
		if not response.content.lower().strip() == "yes":
			await self.bot.say("Exiting.")
			return
		status = await self.bot.say("Logging all messages in all channels")
		total = {"messages" : 0, "channels" : 0, "servers" : 0}
		for server in self.bot.servers:
			total["servers"] += 1
			for channel in server.channels:
				total["channels"] += 1
				try:
					async for message in self.bot.logs_from(channel, limit=10000000, before=None):
						total["messages"] += 1
						await self.log_message(message)
						if total["messages"]%1000 == 0:
							await self.bot.edit_message(status, "Status: `{}` messages in `{}` channels in `{}` servers.".format(total["messages"], total["channels"], total["servers"]))
				except discord.Forbidden:
					pass
				await self.bot.edit_message(status, "Status: `{}` messages in `{}` channels in `{}` servers.".format(total["messages"], total["channels"], total["servers"]))
		msg = "Done!"
		msg += "\nScanned `{}` messages in `{}` channels in `{}` servers.".format(total["messages"], total["channels"], total["servers"])
		await self.bot.send_message(ctx.message.channel, msg)
		
def fileCheck():
	if not os.path.exists("data/sqllog"):
		os.mkdir("data/sqllog")
	if not os.path.isfile("data/sqllog/login.json"):
		login = {"host" : "localhost", "user" : "username", "pass" : "password", "db" : "DB"}
		dataIO.save_json("data/sqllog/login.json", login)

def setup(bot):
	fileCheck()
	global login
	login = dataIO.load_json("data/sqllog/login.json")
	try:
		global db 
		db = pymysql.connect(login["host"], login["user"], login["pass"], login["db"])
		global cursor
		cursor = db.cursor()
		cursor.execute('SET NAMES utf8mb4;')
		cursor.execute('SET CHARACTER SET utf8mb4;')
		cursor.execute('SET character_set_connection=utf8mb4;')
		cursor.execute("SELECT VERSION()")
		data = cursor.fetchone()
		
		logger.info("MySQL Version: {}".format(data))
	except Exception as e:
		logger.info(e)
		logger.info("Error! Could not login")
		if db:
			db.close()
		return
	bot.add_cog(SQLlog(bot))
	