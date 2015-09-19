import urllib
import argparse
import re
from bs4 import BeautifulSoup
import time 
from numpy import array
DEFAULT_MSGS = "html/messages.htm"
DEFAULT_NAME = "Benjamin"
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--file', dest='messages_file', default=DEFAULT_MSGS, type=str, help='Input the file you want to parse messages from')
	parser.add_argument('-n', '--name', dest='name', default=DEFAULT_NAME, type=str, help='Input your person of interest')
	
	values = parser.parse_args()
	print values.messages_file
	read_html(values.messages_file, values.name)
	
def read_html(filename, person):
	file_data = urllib.urlopen(filename).read()
	soup = BeautifulSoup(file_data, 'html.parser')
	
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
		print timestamps_filtered[1:10]
		break



if __name__ == '__main__':
	main()
