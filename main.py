import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")

# Query the vector store
response = client.responses.create(
	model="gpt-5-nano",
	input=[
		# {
    #   "role": "system", "content": 
		# 	"According to the attached documents, what vendor is selling the LED lights in this catalog?"
		# },
		{
      "role": "user", "content": 
   		"According to the attached documents, what vendor is selling the LED lights in this catalog?"
		}
	],
	text={
		"format": {"type": "text"},
		"verbosity": "low"
	},
	reasoning={
		"effort": "medium",
		"summary": "auto"
	},
	tools=[
		{
			"type": "file_search",
			"vector_store_ids": [
				VECTOR_STORE_ID
			]
		},
		# {
		# 	"type": "web_search",
		# 	"user_location": {
		# 		"type": "approximate",
		# 		"country": "US",
		# 		"region": "Pennsylvania",
		# 		"city": "Hatboro"
		# 	},
		# 	"search_context_size": "medium",
		# 	"filters": {
		# 		"allowed_domains": [
		# 			"amazon.com",
		# 			"ledlightingsupply.com",
		# 			"greenlightdepot.com",
		# 			"ledmyplace.com",
		# 			"e-conolight.com",
		# 			"superbrightleds.com"
		# 		]
		# 	}
		# }
	],
	store=True,
	include=[
		"reasoning.encrypted_content",
		"web_search_call.action.sources",
		"file_search_call.results",
	]
)

print(response.output_text)
