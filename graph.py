#!/usr/bin/env python

import json
import re, os
import sys
import csv

def extractGraph(jsonfile):

	try:
		jsondata = json.loads(open(jsonfile).read())

		itemurl = jsondata['Itemurl'].encode('utf8')
		m = re.search('(?<=/dp/)\w+', itemurl)
		if m is None:
			print 'No valid item'
			yield([])

		itemid = m.group(0)

		for rev in jsondata['Reviews']['ReviewList']:

			try:
				authorurl = rev['Author']['ProfileUrl']
				m = re.search('(?<=/profile/)\w+', authorurl)
				authorid = m.group(0)				
				ratings = rev['StarRating']
				date = rev['Date']

				yield([itemid, authorid, ratings, date])

			except:
				# just ignore this review 
				pass

	except Exception as e:
		print str(e)
		#self.logging(jsonfile + " : " + str(e))

	yield([])

def construct(sys.argv):

	with open(sys.argv[1], 'a') as csvfile:

		csvdata = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		#csvdata.writerow(analyzer.getSchema())

		# enumerate all files
		for file in sys.argv[2:]:

			# Ignore files other than JSON
			if not file.endswith(".json"):
				#analyzer.logging("Ignore non-JSON file [" + file + "].")
				continue

			try:
				csvrows = extractGraph(file)
				for csvrow in csvrows:	
					if csvrow is [] or csvrow is None:
						continue;
					csvdata.writerow(csvrow)
			except Exception as e:
				print e
				pass	

if __name__ == "__main__":
