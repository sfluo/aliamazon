#!/usr/bin/env python
"""
	This script is created for crawling Amazon Product Data
	It searches for certain categories with specific keywords
"""

import urllib2
import datetime
import json
import string
import re, os, sys
import cookielib
import hashlib

from datetime import datetime
from bs4 import BeautifulSoup

class Crawler(object):

	def __init__(self, logfile):
		self.Host='http://www.amazon.com'
		self.MaxNumReviews = 100
		self.sortby = 'recent' # or helpful
		self.logfile = (open(logfile, 'a') or stdout)

	def _loadPage(self, url):
		'''
			Get a page with customized http header, cookie and user-agent	
		'''

		tries = 0

		# maximum three failures
		while tries < 3:

			try:
				req = urllib2.Request(url)  # pull the page

				#req.add_header('Cookie', FakeCookie) 
				#req.add_header('User-Agent',UserAgent)
				response = urllib2.urlopen(req, timeout=10)
				page = response.read()

				return page

			except:
				tries += 1

		self.logfile.write(datetime.now().isoformat()+ "\tFail to get " + url + "\n")
		self.logfile.flush()

		return None;
			
	def _extractReviewer(self, authorUrl, Author):
		"""
			Extract information from reviewer profile
			Author: ditionary of reviewer info
			1.	Name
			2.	Location
			3.	User Ranking
			4.	Helpfulness
		"""

		# print(authorUrl)
		
		page = self._loadPage(authorUrl)
		if page is None:
			return

		soup = BeautifulSoup(page) # put into soup
		
		# Step 1: locates the profile
		profile = soup.find('div', class_='profile-info')
		if profile is None:
			return
		
		# Step 2: extract profile info
		try:
			# Task 1: Author Name 
			name = profile.find('span', class_='profile-display-name break-word')
			Author['Name'] = name.string.strip()
		except:
			return # must have a name 

		try:
			# Task 2: Location
			nameblock = profile.find('div', class_='a-row a-spacing-micro')
			location = nameblock.find('span', class_='a-size-small a-color-secondary')
			Author['Location'] = location.string.strip()
		except:
			Author['Location'] = '' 

		# Task 3: User Ranking
		for child in profile.children:
			try: 
				row = child.find('div', class_='a-row')
				ranking = row.find('span', class_='a-size-large a-text-bold')
				Author['Ranking'] = ranking.string.strip()
				break # once we have, break
			except:
				pass

			# if the ranking is not highlighted, then let's try a combined ranking string
			try:
				ranking = child.span #row.find('span', class_='a-size-small a-color-secondary')
				if re.match(r'Reviewer ranking: #\d+', ranking.string.strip()) is not None :
					Author['Ranking'] = ranking.string.strip() # once we have, break
					break
			except:
				Author['Ranking'] = ''
				
		# Task 4: Helpfulness
		try:
			helpful = profile.find('div', class_='a-row customer-helpfulness')
			rate = helpful.find('span', class_='a-size-large a-text-bold')
			Author['Helpfulness'] = rate.string
		except:
			Author['Helpfulness'] = ''

	def _extractReviews(self, revUrl, maxNum, reviews):
		"""
			Extract Reviews from revUrl (recursively)
			@revUrl: the URL of all reviews
			@maxNum: the maximum number of reviews we want
			@reviews: the directionary of reviews (return)

			@return
				AverageStarRating
		"""
	
		numOfReviews = 0

		reviews['ReviewUrl'] = revUrl
		reviews['AverageStarRating'] = ''

		reviewList = []
		while revUrl is not None:

			#print(revUrl)

			# Step 1: get the reviews page
			page = self._loadPage(revUrl)
			if page is None:
				break

			soup = BeautifulSoup(page) # put into soup
			
			# Task 1: Average Star Rating
			if reviews['AverageStarRating'] is '':
				summary = soup.find('div', class_='a-row averageStarRatingNumerical')
				if summary is not None:
					avgscore = soup.find('span', class_='arp-rating-out-of-text')
					stars = avgscore.string
					reviews['AverageStarRating'] = stars
				else:
					reviews['AverageStarRating'] = ''

			if reviews['TotalReviewCount'] is '':
				try:
					prodinfo = soup.find(id='cm_cr-product_info')
					totalReviews = soup.findAll('span',
						{'class' : lambda x: x and re.search('(\s|^)totalReviewCount(\s|$)', x)})
					for tr in totalReviews:
						reviews['TotalReviewCount'] = tr.string.strip()
						break
				except:
					reviews['TotalReviewCount'] = 0
				

			reviewsoup = soup.find(id='cm_cr-review_list')
			#for review in reviewsoup.find_all('div', class_='a-section review'):
			if reviewsoup is None:
				break

			# Task 2: get reviews (list)
			for review in reviewsoup.children:

				# Task 2.0: A review should have a ID
				if review.get('id') is None:
					continue;	

				a_review = {}
				valid = False

				# Task 2.1: Helpfulness vote
				try:
					vote = review.find('span', class_='a-size-small a-color-secondary review-votes')
					hwords = vote.string.split(' ')	
					hrate = float(hwords[0]) / float(hwords[2])
					a_review['Helpfulness'] = hrate
				except:
					a_review['Helpfulness'] = ''

				# Task 2.2: Star Rating
				try:
					stars = review.find('span', class_='a-icon-alt')
					a_review['StarRating'] = stars.string
				except:
					a_review['StarRating'] = ''

				# Task 2.3: Review Date
				date = review.find('span', class_='a-size-base a-color-secondary review-date')
				if date is not None:
					a_review['Date'] = date.string
				else:
					a_review['Date'] = ''

				# Task 2.4: Review Text
				try:
					reviewdata = review.find('div', class_='a-row review-data')
					text = reviewdata.find('span', class_='a-size-base review-text')
					a_review['Text'] = ''.join(text.strings)
					valid = True
				except:
					a_review['Text'] = ''

				# Task 2.5: Reviewer 
				profile = {}
				reviewer = review.find('a', class_='a-size-base a-link-normal author')
				if reviewer is not None:
					authorUrl = self.Host + reviewer.get('href')
					profile = {'ProfileUrl' : authorUrl}
					#extractReviewer(authorUrl, profile)
				else:
					profile = {'ProfileUrl' : ''}
					a_review['Author'] = profile

				if valid is True:
					reviewList.append(a_review)		

				numOfReviews += 1

			# Step 3: Okay, we had enough, time to leave
			if numOfReviews > maxNum:
				break

			# otherwise, continue to explore
			try:
				pagebar = soup.find(id='cm_cr-pagination_bar')
				last = pagebar.find('li', class_="a-last")
				nextpage = last.a.get('href')
				revUrl = self.Host + nextpage
			except:	
				revUrl = None # no more pages

		reviews['ReviewList'] = reviewList 
		#print(reviewList)
	
	def extractName(self, soup, record):
		try:
			name = soup.find(id='productTitle') # book
			if name == None:
				name = soup.find(id='btAsinTitle') # kindle ebook, Video Game
			record['Name'] = name.string.strip(),
		except:
			record['Name'] = ''

	def extractPrice(self, soup, record, itemurl):

		record['OfferPrice'] = ''
		try:
			buyNewSection = soup.find(id='buyNewSection')
			offerPrice = buyNewSection.find('span', class_='a-size-medium a-color-price offer-price a-text-normal')
			record['OfferPrice'] = offerPrice.contents[0].strip()
		except:
			try:
				offerPrice = soup.findAll('span',
					{'class' : lambda x: x and re.search('(\s|^)header-price(\s|$)', x)})
				for op in offerPrice:
					record['OfferPrice'] = op.string.strip()
			except:
				record['OfferPrice'] = ''

		record['ListPrice'] = '' 
		try:
			buyBoxInner = soup.find(id='buyBoxInner')
			listPrice = buyBoxInner.find('span', class_= 'a-color-secondary a-text-strike')
			record['ListPrice'] = listPrice.contents[0].strip()
		except:
			try:
		#		newOffer = soup.find(id='newOfferAccordionRow')
				listPrice = soup.findAll('span',
				{'class' : lambda x: x and re.search('(\s|^)a-text-strike(\s|$)', x)})
				for lp in listPrice:
					record['ListPrice'] = lp.string.strip()
			except:
				record['ListPrice'] = ''

	def extractSaleRankLine(self, salesrank):
		salesrankstr = ''
		try:
			salesrankstr = salesrank.contents[2].strip()
		except:
			pass
		#print "SalesRankString", salesrankstr
		return salesrankstr
			
	def extractSaleRank(self, soup, record):
		record['Salesrank'] = ''
		record['Category'] = '' 
		try:
			salesrank = soup.find(id='SalesRank')
			#print salesrank
			record['Salesrank'] = self.extractSaleRankLine(salesrank)
			rankvalues = salesrank.findAll('li', class_='zg_hrsr_item')
			for rankval in rankvalues:
				record['Salesrank'] = record['Salesrank'] + ' '.join(rankval.stripped_strings)
		except:
			pass
	
	def fetchItem(self, itemurl, record):
		"""
		Given a product url, extract all information we need for our analysis
		We are assuming that Amazon use a template for all their products
		because the extraction heavily depends on the tokens (fix strings)

		Alert: the page might use different template for different categories of products
		"""
		#print(itemurl)

		page = self._loadPage(itemurl)
		if page is None:
			return

		soup = BeautifulSoup(page) # put into soup

		# Here, we extract all information we need

		# Task 0. Time Stamp 
		ts = str(datetime.now())
		record['Timestamp'] = ts;

		self.extractName(soup, record)
		self.extractPrice(soup, record, itemurl)
		self.extractSaleRank(soup, record)

		# Task 4. Star Ratings
		# Task 7. Reviews (Recent 100): review Text, rating and timestamp, Reviewer
		# Task 8. Reviewer Info: Name, Rating, rating, location
		reviews = { 'TotalReviewCount' : ''}
		try:
			review = soup.find(id='customer-reviews_feature_div')
			allrev = review.find('a', id='seeAllReviewsUrl')
			revurl = allrev.get('href')
			if revurl is not None:
				# may replace 'sortBy=bySubmissionDateDescending' with 'sortBy=helpful'
				self._extractReviews(str(revurl), totalReviews, reviews)
				record['Reviews'] = reviews
		except:
			revurl =  itemurl.replace('/dp/', '/product-reviews/') + \
				'/ref=cm_cr_dp_see_all_btm?ie=UTF8&showViewpoints=1&sortBy='+self.sortby
			self._extractReviews(str(revurl), self.MaxNumReviews, reviews)
			record['Reviews'] = reviews

		return True

	def crawlitems(self, urlfile, outputpath):

		with open(urlfile) as urlfd:

			urls = urlfd.readlines()

			for itemurl in urls:
				itemurl = itemurl.strip()
				record = { 'Itemurl' : itemurl}
				valid = self.fetchItem(itemurl, record) # pull the item
				if valid:
					h = hashlib.md5()
					h.update(itemurl)
					#print h.hexdigest()
					with open(outputpath + '/' + h.hexdigest() + '.json', 'w') as f:
						json.dump(record, f)
				self.logfile.write(datetime.now().isoformat() + "\t -- " + itemurl + "\n")
				self.logfile.flush()

	def cleanup(self):
		self.logfile.flush()
		self.logfile.close()

class MusicCrawler(Crawler):
	
	def __init__(self, logfile):
		super(MusicCrawler, self).__init__(logfile)
	
	def extractName(self, soup, record):
		record['Name'] = ''
		try:
			feature = soup.find(id='ppd-center')
			#print feature
			record['Name'] = feature.h1.string.strip()
		except:
			record['Name'] = ''

	def extractPrice(self, soup, record, itemurl):
		
		record['OfferPrice'] = ''
		try:
			MusicID = itemurl[-10:]
			buyNewSection = soup.find(id=MusicID)
			offerPrice = buyNewSection.find('span', class_='a-text-bold')
			record['OfferPrice'] = offerPrice.contents[0].strip()
		except:
			try:
				offerPrice = soup.findAll('span',
					{'class' : lambda x: x and re.search('(\s|^)header-price(\s|$)', x)})
				for op in offerPrice:
					record['OfferPrice'] = op.string.strip()
			except:
				record['OfferPrice'] = ''

		record['ListPrice'] = '' 
		try:
			buyBoxInner = soup.find(id='buyBoxInner')
			listPrice = buyBoxInner.find('span', class_= 'a-color-secondary a-text-strike')
			record['ListPrice'] = listPrice.contents[0].strip()
		except:
			try:
#				newOffer = soup.find(id='newOfferAccordionRow')
				listPrice = soup.findAll('span',
					{'class' : lambda x: x and re.search('(\s|^)a-text-strike(\s|$)', x)})
				for lp in listPrice:
					record['ListPrice'] = lp.string.strip()
			except:
				record['ListPrice'] = ''

class HomeKitchenCrawler(Crawler):

	def __init__(self, logfile):
		super(HomeKitchenCrawler, self).__init__(logfile)
	
	def extractPrice(self, soup, record, itemurl):
		
		record['OfferPrice'] = ''
		try:
			pricediv = soup.find(id='priceblock_ourprice')
			#print pricediv
			record['OfferPrice'] = pricediv.string.strip()
		except:
			try:
				pricespan = soup.find(id='color_name_0_price')
				pspan = pricespan.find('span', class_='a-size-mini')
				record['OfferPrice'] = pspan.string.strip()
			except:
				record['OfferPrice'] =''

		record['ListPrice'] = '' 
		try:
			pricediv = soup.find(id='price_feature_div')
			#print pricediv
			#istPrice = pricediv.find('span', class_= 'a-color-secondary a-text-strike')
			listPrice = pricediv.findAll('td',
					{'class' : lambda x: x and re.search('(\s|^)a-text-strike(\s|$)', x)})
			#print listPrice
			for lp in listPrice:
				record['ListPrice'] = lp.string.strip()
		except:
			#try:
			#	listPrice = soup.findAll('span',
			#		{'class' : lambda x: x and re.search('(\s|^)a-text-strike(\s|$)', x)})
			#	for lp in listPrice:
			#		record['ListPrice'] = lp.string.strip()
			#except:
			record['ListPrice'] = ''

	def extractSaleRankLine(self, salesrank):
		salesrankstr = ''
		try:
			rankvalue = salesrank.find('td', class_= 'value')
			salesrankstr = ''.join(rankvalue.stripped_strings)
		except:
			pass
		return salesrankstr
		
class OfficeCrawler(HomeKitchenCrawler):

	def __init__(self, logfile):
		super(OfficeCrawler, self).__init__(logfile)
	
	def extractSaleRankLine(self, salesrank):
		salesrankstr = ''
		try:
			salesrankstr = salesrank.contents[2].strip()
		except:
			pass
		return salesrankstr


if __name__ == '__main__':
	
	if len(sys.argv) < 4:
		print "Error: invalid parameters. Usge: python crawl_music.py [keyword] [url file] [path to output]"
		exit(0);

	if not os.path.exists(sys.argv[2]):
		print "Error: file [" + sys.argv[2] + "] does not exist"
		exit(0)

	if not os.path.exists(sys.argv[3]): 
		print "Error: path [" + sys.argv[3] + "] does not exist"
		exit(0)

	logfile = sys.argv[3] + '/log_' + str(os.getpid()) + '.txt' 
	crawler = Crawler(logfile)

	if sys.argv[1] == 'home':
		#print "Using Home"
		crawler = HomeKitchenCrawler(logfile)
	elif sys.argv[1] == 'music':
		#print "Using Music"
		crawler = MusicCrawler(logfile)
	elif sys.argv[1] == 'office':
		#print "Using Office"
		crawler = OfficeCrawler(logfile)

	crawler.crawlitems(sys.argv[2], sys.argv[3])	
	crawler.cleanup()


