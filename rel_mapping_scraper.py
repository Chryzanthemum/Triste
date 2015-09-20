import urllib
import argparse
import re
from bs4 import BeautifulSoup
import time 
import numpy as np
from numpy import array
from dateutil.parser import parse
from datetime import datetime
import indicoio 
import itertools

indicoio.config.api_key = 'd5c238260300f6d80233e6e68c683449'

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
	date_to_msgs = {}
	relationships = {}
	for thread in soup.find_all('div', class_='thread'):
		# check if thread is b/w 2 people
		thread_iter = thread.childGenerator()
		people_involved = thread_iter.next()
		people_involved = people_involved.split(',')
		
		# get all the messages		
		msgs = thread.find_all('p')
		msgs = [m.get_text().encode('ascii', 'ignore') for m in msgs]

		# holds the name and timestamp information
		msg_meta = thread.find_all('div', class_='message')
		# filter to only messages by our person of interest
		total_indices = np.arange(len(msg_meta))
		meta_filtered_idx = [idx for (idx,p) in enumerate(msg_meta) 
			if (person in p.span.get_text().encode('ascii','ignore'))]
		msgs_filtered = list(array(msgs)[meta_filtered_idx])
		
		
		# also the timestamps mapping to the msgs
		just_timestamps = [str(ts.find('span', class_='meta').get_text()) 
			for ts in msg_meta if ts.find('span', class_='meta')]
		just_timestamps = [parse(t) for t in just_timestamps]
		timestamps_filtered = list(array(just_timestamps)[meta_filtered_idx])
		for idx,ts in enumerate(timestamps_filtered):
			if ts not in date_to_msgs:
				date_to_msgs[ts] = [msgs_filtered[idx]]
			else:
				date_to_msgs[ts].append(msgs_filtered[idx])

		if len(people_involved) == 2:
			other = people_involved[0] if person not in people_involved[0] else people_involved[1]
			# get the other person's info
			not_indices = np.setxor1d(total_indices, meta_filtered_idx)
			not_indices = [int(i) for i in not_indices]
			# sometimes the xor returns floats
			if (len(not_indices) > 0 and isinstance(not_indices[0], int)):
				other_filtered = list(array(msgs)[not_indices])
				other_timestamps = list(array(just_timestamps)[not_indices])
				relationships[other] = ([[timestamps_filtered],[msgs_filtered]], 
								[[other_timestamps],[other_filtered]]) # -person-, -other-
			
				ts_grouped = [list(g) for k, g in itertools.groupby(timestamps_filtered, key=lambda d: d.date())]
				other_ts_grouped = [list(g) for k, g in itertools.groupby(other_timestamps, key=lambda d: d.date())]

				[senti, msgs_grouped] = group_msgs(msgs_filtered, ts_grouped)
				[other_senti, other_msgs_grouped] = group_msgs(other_filtered, other_ts_grouped)
				print senti
				print other_senti

def group_msgs(msgs, ts_grouped):
	track_idx = 0
	msgs_grouped = []
	sentiment_mapping = []
	for ts_list in ts_grouped:
		move_up = track_idx + len(ts_list)
		grouping = msgs[track_idx:move_up]
		
		# hits a problem right here...
		single_str = ' '.join(str(elem) for elem in grouping)
		sentiment_rating = indicoio.sentiment_hq(single_str)
		timemap = (ts_list[0].date(), sentiment_rating)
		sentiment_mapping.append(timemap)
		msgs_grouped.append(grouping)
		track_idx = move_up

	return [sentiment_mapping, msgs_grouped]

if __name__ == '__main__':
	main()
