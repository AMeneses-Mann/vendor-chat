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
		{"role": "user", "content": "What can you tell me about the data in the attached vector store?"}
	],
	text={
		"format": {"type": "text"},
		"verbosity": "medium"
	},
	reasoning={
		"effort": "medium",
		"summary": "auto"
	},
	tools=[
		{
			"type": "file_search",
		},
		{
			"type": "web_search",
			"user_location": {
				"type": "approximate",
				"country": "US",
				"region": "Pennsylvania",
				"city": "Hatboro"
			},
			"search_context_size": "medium",
			"filters": {
				"allowed_domains": [
					"amazon.com",
					"ledlightingsupply.com",
					"greenlightdepot.com",
					"ledmyplace.com",
					"e-conolight.com",
					"superbrightleds.com"
				]
			}
		}
	],
  tool_resources={
		"file_search": {
			"vector_store_ids": [VECTOR_STORE_ID]
		}
	},
	store=True,
	include=[
			"reasoning.encrypted_content",
			"web_search_call.action.sources"
	]
)

print(response.output_text)
