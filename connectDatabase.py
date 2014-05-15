
import MySQLdb as mdb
import sys
import ConfigParser

class DBConnection:
        def __init__(self):
		# Parse the arguments
		config = ConfigParser.ConfigParser()
		config.read('config.txt')

		# Read all system properties from the config file
		self.host = config.get('database_section', 'dbhost')
		self.user = config.get('database_section', 'user')
		self.password = config.get('database_section', 'password')
		self.database = config.get('database_section', 'dbname')

		# Establishing connection to database
		self.con = mdb.connect(self.host, self.user, self.password, self.database)

	def getUsers(self):
		""" Fetches Users from database."""
		query= "Select * from Users;"
		cur = self.con.cursor()
		cur.execute(query)
                rows = cur.fetchall()
		userEmailPasswordList = []
		for row in rows:
			user= (row[4],row[5])
			#user[row[4]] = row[5] 			
			userEmailPasswordList.append(user)
                return userEmailPasswordList



