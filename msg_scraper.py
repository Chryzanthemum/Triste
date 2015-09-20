import urllib
import argparse
import re
from bs4 import BeautifulSoup
import time 
from numpy import array
from dateutil.parser import parse
from datetime import datetime
from msg_alchemize import *
from input_to_sql import *
DEFAULT_MSGS = "html/benmessages4.htm"
#DEFAULT_MSGS = "test_messages.htm"
DEFAULT_NAME = "Benjamin"


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--file', dest='messages_file', default=DEFAULT_MSGS, type=str, help='Input the file you want to parse messages from')
	parser.add_argument('-n', '--name', dest='name', default=DEFAULT_NAME, type=str, help='Input your person of interest')
	
	values = parser.parse_args()
	#print values.messages_file
	# Dictionary indexed by timestamp
	message_dict = read_html(values.messages_file, values.name)
	# Updating values of dictionary to contain tuple of message content and sentiment score given by alchemy
	for key,val in message_dict.items():
		val = calculate_sentiments(val)
		message_dict[key] = val
	#print message_dict
	#print con
	messages_to_sql(message_dict)
	
def read_html(filename, person):
	file_data = urllib.urlopen(filename).read()
	soup = BeautifulSoup(file_data, 'html.parser')
	date_to_msgs = {}
	for thread in soup.find_all('div', class_='thread'):
		msgs = thread.find_all('p')
		msgs = [m.get_text().encode("ascii", "ignore") for m in msgs]

		# holds the name and timestamp information
		msg_meta = thread.find_all('div', class_='message')

		# filter to only messages by our person of interest
		meta_filtered_idx = [idx for (idx,p) in enumerate(msg_meta) 
			if (person in p.span.get_text().encode("ascii","ignore"))]
		msgs_filtered = list(array(msgs)[meta_filtered_idx])
		# also the timestamps mapping to the msgs
		just_timestamps = [str(ts.find('span', class_="meta").get_text()) 
			for ts in msg_meta if ts.find('span', class_="meta")]
		timestamps_filtered = list(array(just_timestamps)[meta_filtered_idx])
		for idx,timestamp in enumerate(timestamps_filtered):
			ts = parse(timestamp) # date object
			if ts not in date_to_msgs:
				date_to_msgs[ts] = [msgs_filtered[idx]]
			else:
				date_to_msgs[ts].append(msgs_filtered[idx])
	return date_to_msgs
	


if __name__ == '__main__':
	main()
