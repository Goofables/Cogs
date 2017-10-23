import discord
from discord.ext import commands
from .utils.dataIO import dataIO

import PyMySQL

class SQLlog:
	"""Loggs messages to MySQL server"""
	def __init__(self, bot):
		self.bot = bot
		self.login = dataIO.load_json("data/SQLlog/login.json")
		self.db = PyMySQL.connect(self.login["host"],self.login["user"],_login["pass"],_login["db"])
		cursor = db.cursor()
		cursor.execute("SELECT VERSION()")
		data = cursor.fetchone()
		print("Version: {}".format(data))
		print(db)
		db.close()
	
	
def fileCheck():
	if not os.path.exists("data/SQLlog"):
		os.mkdir("data/SQLlog")
	if not os.path.isfile("data/SQLlog/login.json"):
		dataIO.save_json("date/SQLlog/login.json", {"host":"localhost",
													"user":"username",
													"pass":"password",
													"db":"DB"})

def setup(bot):
	fileCheck()
	
	bot.add_cog(SQLlog(bot))
	