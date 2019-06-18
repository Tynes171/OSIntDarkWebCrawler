import time
import shodan
import requests

file = open('OpenServices.txt','r')


for line in file.readlines():

	try:
		req = requests.get('http://'+line)
		results = open('./OpenServiceResults/'+line+'.txt', 'w')
		results.write(req.text)

	except Exception as e:
		print "Error on {}".format(line)
		print e

	
