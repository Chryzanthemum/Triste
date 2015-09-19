from alchemyapi import AlchemyAPI
alchemyapi = AlchemyAPI()

## Takes in a list of messages in text and returns a list of the sentiment types and scores calculated by Alchemy in the same order as the original list.
def calculate_sentiments(messages):
	responses = []
	for message in messages:
		response = alchemyapi.sentiment("text", message)
		if response["docSentiment"]["type"] != "neutral":
			responses.append((message, response["docSentiment"]["score"]))
		else: 
			responses.append((message, 0))
	return responses