# -*- encoding: utf-8 -*-
import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from typing import Union
from datetime import datetime,timedelta
import time
import os
import re
try:
	import pymysql
except:
	print ("Error! pymysql not installed")
	quit()
reg = re.compile("((\d+)d)?((\d+)h)?((\d+)m)?((\d+)s)?")

class SQLlog:
	"""Loggs messages to MySQL server"""
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True)
	@checks.serverowner_or_permissions(administrator=True)
	async def log(self, ctx, time: str, amount: int = 10, channel: discord.Channel = None):
		time = reg.match(time)
		if channel == None:
			channel = ctx.message.channel

		def none0(val):
			return int((val, 0)[val == None])
		datedif = datetime.now() - timedelta(days=none0(time.group(2)), hours=none0(time.group(4)), minutes=none0(time.group(6)), seconds=none0(time.group(8)))
		##await self.bot.say("Time: `{}d{}h{}m{}s` Amt: `{}` Ch: `{}`".format(time.group(2), time.group(4), time.group(6), time.group(8), amount, (channel, "all")[channel == None]))
		##status = await self.bot.say("Searching logs for messages from all users in {}.".format((channel.mention, "all channels")[channel == "*"]))
		
		cursor.execute("SELECT * FROM `{}` WHERE `timestamp` >= '{}' ORDER BY `id` ASC LIMIT {}".format(channel.id, datedif, amount))
		data = cursor.fetchall()
		msg = "Done! Found {} messages: ```".format(len(data))
		
		m = 0
		for entry in data:
			user = discord.utils.get(self.bot.get_all_members(), id=entry[1])
			m += 1
			msg += "\n{} #{} @{} >> \"{}\"".format(entry[4], entry[0], entry[1], entry[3])
		if len(msg) < 1998:
			msg += "```"
		while len(msg) > 6:
			await self.bot.send_message(ctx.message.channel, msg[0:2000] + ("```", "")[len(msg) < 1998])
			msg = "```{}```".format(msg[1994:])
		

		"""	
		if user != None and user != sender:
				continue
			if channel != None and channel != ch:
				continue
			m += 1
			msg += "{} {} > \"{}\"".format(time, sender.name, message)
		msg += "```"
		await self.bot.edit_message(status, msg.format(m))
		"""
	
	async def on_message(self, message):
		"""Message listener"""
		try:
			if "_console" in message.channel.name:
				if message.author.bot:
					return
		except:
			print("{} {} {}".format(message.channel, message.author, message.content))
			return
		##print("#{}  @{}  '{}'".format(message.channel, message.author, message.content))
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
				print("Couldn't log message \"{}\"".format(message.content))
				return
			except pymysql.err.IntegrityError:
				return
			except pymysql.err.ProgrammingError as pe:
				if not cursor.execute("SHOW TABLES LIKE '{}'".format(message.channel.id)):
					print("Table `{0.id}` ({0.name}) does not exist! Creating now...".format(message.channel))
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
						print("Success! Table `{0.id}` ({0.name}) created!".format(message.channel))
						cursor.execute(query)
					else:
						print("Error! Table `{0.id}` ({0.name}) could not be created!".format(message.channel))
						await self.bot.send_message(discord.utils.get(self.bot.get_all_members(), id=self.bot.settings.owner), "Error! Table `{0.id}` ({0.name}) could not be created!".format(message.channel))
				else:
					print("Error! Couldnt log message!")
					print("`{0.timestamp}` > `{0.server.id}` > `{0.channel.id}` > > `{0.id}` > `{0.author}` > `{0.call}` > `{0.type}` > \"{0.content}\"".format(message))
					await self.bot.send_message(discord.utils.get(self.bot.get_all_members(), id=self.bot.settings.owner), "`{0.timestamp}` > `{0.server.id}` > `{0.channel.id}` > > `{0.id}` > `{0.author}` > `{0.call}` > `{0.type}` > \"{0.content}\"".format(message))
					print("ProgrammingError ({0}): {1}".format(pe.strerror))
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
		timeI = int(time.time())
		time2 = time.time()
		for server in self.bot.servers:
			total["servers"] += 1
			for channel in server.channels:
				total["channels"] += 1
				try:
					async for message in self.bot.logs_from(channel, limit=10000000, before=None):
						if time.time() - time2 > 5:
							time2 = time.time()
							await self.bot.edit_message(status, "Status: `{}` messages in `{}` channels in `{}` servers. Time: `{}`".format(total["messages"], total["channels"], total["servers"], timedelta(seconds=int(time.time() - timeI))))
						total["messages"] += 1
						await self.log_message(message)
				except discord.Forbidden:
					pass
		msg = "Done!"
		msg += "\nScanned `{}` messages in `{}` channels in `{}` servers. Time: `{}`".format(total["messages"], total["channels"], total["servers"], timedelta(seconds=int(time.time() - timeI)))
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
		
		print("MySQL Version: {}".format(data))
	except Exception as e:
		print(e)
		print("Error! Could not login")
		if db:
			db.close()
		return
	bot.add_cog(SQLlog(bot))
	