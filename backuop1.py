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
		# {"role": "user", "content": "Attached is a vector store with tabular data of LED lights from distributor. Convert the table data from the attached vector store file into csv, preserving the structure. Include accessory and mounting options. If a table cell has more than one value in it, add them to one csv cell with line breaks between them."}
    
		# {"role": "user", "content": "Attached is a vector store with data of LED lights from a distributor. Compare their offereings to the online LED marketplace"}
		# {"role": "user", "content": "Give me a simple haiku"}
    
    {"role": "user", "content": "What can you tell me about the data in the attached vector store?"}
	],
	text={
    "format": {
      "type": "text"
    },
    "verbosity": "medium"
  },
	reasoning={
    "effort": "medium",
    "summary": "auto"
  },
	tools=[
		{
			"type": "file_search",
			"file_search": {
				"vector_store_ids": [VECTOR_STORE_ID]
			}
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
						# "amazon.com",
						"ledlightingsupply.com",
						"greenlightdepot.com",
						"ledmyplace.com",
						"e-conolight.com",
						"superbrightleds.com"
					]
				}
		}
  ],
	store=True,
  include=[
    "reasoning.encrypted_content",
    "web_search_call.action.sources"
  ]
)
print(response.output_text)