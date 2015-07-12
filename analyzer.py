#!/usr/bin/env python
"""
	Accept a list of JSON file and aggregates to one CSV file 
	with each row aggregated for one JSON file.

	NOTE: Prerequisite - dictionary file 'warriner_ratings.csv',
		which include the sentiment scores for words

	by Shoufu Luo, 2015.07
"""

import os, sys
import json
import re
import csv
import numpy as np
import datetime
import time
from datetime import datetime

class Analyzer:
	
	def __init__(self, logfile, dict={}):
		self.dict = dict 
		self.schema = ['Group','Category','Product_Name','Average_Rating','Total_Ratings',\
			'Num_Of_5_Star','Num_Of_4_Star','Num_Of_3_Star', 'Num_Of_2_Star','Num_Of_1_Star',\
			'Purchase_Price','Original_Price','TimeID','Timestamp','Sales_Rank','Valence','Arousal']
		filepath = os.path.dirname(logfile)
		if not os.path.exists(filepath):
			os.makedirs(filepath)
		self.logfile = (open(logfile, 'a+') or stdout)

	def logging(self, str):
		"""
			Logging 
		"""
		try:
			self.logfile.write(datetime.now().isoformat() + "\t -- "+ str + "\n")
		except:
			self.logfile.write(datetime.now().isoformat() + "\t -- Unexpected Error. \n")

		self.logfile.flush()

	def getSchema(self):
		"""
			Data Schema
		"""
		return self.schema

	def cleanup(self):
		self.logfile.flush()
		self.logfile.close()

	def scoring(self, text):
		"""
			Calculate valence score and arousal score	
		"""
		valence = []
		arousal = []

		words = re.sub('[^\w]', ' ', text).split() 
		for word in words:
			if not self.dict.has_key(word):
				valence.append(0)
				arousal.append(0)
			else:
				valence.append(self.dict[word][0])
				arousal.append(self.dict[word][1])
		
		val=np.mean(valence) if valence != [] else 0
		ars=np.mean(arousal) if arousal != [] else 0

		return [val, ars]

	def aggregate(self, jsonfile):
		"""
			Aggregate a JSON file into one row in CSV

			[Schema]: use self.schema
		"""
		try:
			jsondata = json.loads(open(jsonfile).read())

			""" 
				The group is filled by the filename, e.g. Xbox-360-Games_video+games.3000.txt 
				[product_info].[number_of_instances].txt
			"""	
			group = jsondata['group'].encode('utf8').split('.')[-3]
			name = jsondata['Name'][0].encode('utf8')
			average = jsondata['Reviews']['AverageStarRating'].split(' ')[0]
			total = jsondata['Reviews']['TotalReviewCount']

			ratings = []
			valence = []
			arousal = []
			for rev in jsondata['Reviews']['ReviewList']:
				ratings.append(rev['StarRating'])
				scores = self.scoring(rev['Text'])
				valence.append(scores[0])
				arousal.append(scores[1])

			# calcuate valence and arousal
			# average of all reviews: scoring(one_review) - average of all words
			avg_valence = np.mean(valence) if valence != [] else 0
			avg_arousal = np.mean(arousal) if arousal != [] else 0
				
			one = ratings.count('1')
			two = ratings.count('2')
			three = ratings.count('3')
			four = ratings.count('4')
			five = ratings.count('5')
			# print one, two, three, four, five

			purchase = jsondata['OfferPrice'].encode('utf8')
			original = jsondata['ListPrice'].encode('utf8')
	
			time_id = jsondata['Timestamp'].split(' ')[0]
			# print time_id
	
			# e.g. "#23,488 in Video Games ( ..."
			# e.g. "#4311 in Electronics > Accessories 
			ranking = ''
			category = ''
			rc = re.compile(r'#([\d,]*?) in (.*?) [(>#]')
			m = rc.match(jsondata['Salesrank'])
			if m:
				ranking = m.group(1)
				category = m.group(2)
	
			return [group, category, name, average, total, five, four, three, two, one, purchase,\
				original, time_id.replace('-', '_'), jsondata['Timestamp'], ranking, avg_valence, avg_arousal]
				
		except Exception as e:
			self.logging(jsonfile + " : " + str(e))

		return []
	
def loadWarrinerDict(filename):
	"""
		Sentiment word list
	"""
	dict = {}
	with open(filename) as csvfile:
		csvreader = csv.reader(csvfile, dialect=csv.excel)
		try:
			for row in csvreader:
				try:
					dict[row[1]] = [ float(row[2]), float(row[5]) ]
				except:
					pass
		except csv.Error as e:
			sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))	
	return dict
			
if __name__ == "__main__":
	
	# argument checking
	if len(sys.argv) < 2 or not sys.argv[1].endswith('.csv'):
		print "Usage: python analyzer.py <output file name> <List of JSON files>"
		exit()

	# put in temporaray folder - just in case we need to know what's going on
	logfile = '/tmp/aliamazon/analyzer/log_' + str(os.getpid()) + '.txt' 

	dict = loadWarrinerDict(os.getcwd() + '/warriner_ratings.csv')
	analyzer = Analyzer(logfile, dict)

	analyzer.logging("Composing " + sys.argv[1])

	with open(sys.argv[1], 'a') as csvfile:

		csvdata = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		csvdata.writerow(analyzer.getSchema())

		# enumerate all files
		for file in sys.argv[2:]:

			analyzer.logging("from " + file + " ...")

			# Ignore files other than JSON
			if not file.endswith(".json"):
				analyzer.logging("Ignore non-JSON file [" + file + "].")
				continue

			try:
				csvrow = analyzer.aggregate(file)
				if csvrow != []:
					csvdata.writerow(csvrow)
			except Exception as e:
				print e
				pass	

	analyzer.cleanup()
