import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
import time
import re


# Load key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")

def run_stream():
  # Create placeholders for different types of updates
  status_placeholder = st.empty()

  # Stream text tokens to Streamlit as they arrive.
  with client.responses.stream(
    model="gpt-5-nano",
    input=[
      # {
      #     "role": "system",
      #     "content": "According to the attached documents, what vendor is selling the LED lights in this catalog?",
      # },
      #  {
      #    "role": "user", "content":
      #    "Write a haiku"
      #  },
      {
        "role": "user", "content":
        "Give a brief overview of the types of products sold in the attached document."
      }
    ],
    text={"format": {"type": "text"}, "verbosity": "low"},
    reasoning={"effort": "medium", "summary": "auto"},
    tools=[
      {"type": "file_search", "vector_store_ids": [VECTOR_STORE_ID]},
      # {
      #   "type": "web_search",
      #   "user_location": {
      #     "type": "approximate",
      #     "country": "US",
      #     "region": "Pennsylvania",
      #     "city": "Hatboro"
      #   },
      #   "search_context_size": "medium",
      #   "filters": {
      #     "allowed_domains": [
      #       "amazon.com",
      #       "ledlightingsupply.com",
      #       "greenlightdepot.com",
      #       "ledmyplace.com",
      #       "e-conolight.com",
      #       "superbrightleds.com"
      #     ]
      #   }
      # }
    ],
    store=True,
    include=[
      "web_search_call.results",
      "file_search_call.results",
    ],
  ) as stream:
    status_placeholder = st.empty()
    status_text = ""

    for event in stream:
      if event.type == "response.created":
        status_text += "Response started\n"
        status_placeholder.write(status_text)
      elif event.type == "response.reasoning_summary_text.delta":
        status_text += event.delta + "\n"
        status_placeholder.write(status_text)
      elif event.type == "response.file_search_call.in_progress":
        status_text += "\nSearching file\n"
        status_placeholder.write(status_text)
      elif event.type == "response.reasoning_summary_text.done":
        status_text += "\n\n"
        status_placeholder.write(status_text)
      elif event.type == "response.content_part.added":
        status_text += "FINAL RESPONSE:\n"
        status_placeholder.write(status_text)
      elif event.type == "response.output_text.delta":
        status_text += "\n" + event.delta
        status_placeholder.write(status_text)
      # else:
      #   status_text += event.type + "\n"
        #   status_placeholder.write(status_text)


if __name__ == "__main__":
  run_stream()
