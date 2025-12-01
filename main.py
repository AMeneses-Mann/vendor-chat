import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
import pandas as pd
import time
import re

with open('product-headings.csv', 'r') as file:
  csv_data = file.read()

# Load key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")

def csv_to_json(csv_file_path, json_file_path):
  df = pd.read_csv(csv_file_path)
  df.to_json(json_file_path, orient='records', indent=4)

def run_stream():
  # Create placeholders for different types of updates
  status_placeholder = st.empty()

  # Stream text tokens to Streamlit as they arrive.
  with client.responses.stream(
    model="gpt-5",
    input=[
      {
          "role": "user",
          "content": "Write a haiku",
      },
      #  {
      #    "role": "user", "content":
      #    f"Use file search to read the attached vector store's data. The data includes specs and costs of LED lighting fixtures. Extract the information about each product and place it in the following CSV. The CSV contains headers under which to put the relevant piece of data for the product. Output the modified CSV ONLY, directly in the response. If a product doesn't have a particular piece of data, just leave the relevant cell blank. Note: skip accessories, focusing only on main products and make sure every main product is included. Here is CSV data:\n\n{csv_data}\n\n"
      #  },
      # {
      #   "role": "user", "content":
      #   "Give a brief overview of the types of products sold in the attached document."
      # }
    ],
    text={"format": {"type": "text"}, "verbosity": "low"},
    reasoning={"effort": "medium", "summary": "auto"},
    tools=[
      {"type": "file_search", "vector_store_ids": [VECTOR_STORE_ID]},
    ],
    store=True,
    include=[
      "web_search_call.results",
      "file_search_call.results",
    ],
  ) as stream:
    status_placeholder = st.empty()
    status_text = ""
    final_output = ""

    for event in stream:
      if event.type == "response.reasoning_summary_text.done":
        status_text += event.text + "\n"
        status_placeholder.write(status_text)
      elif event.type == "response.file_search_call.in_progress":
        status_text += "\nSearching file\n"
        status_placeholder.write(status_text)
      elif event.type == "response.reasoning_summary_text.done":
        status_text += "\n\n"
        status_placeholder.write(status_text)
        # print(status_text)
      # elif event.type == "response.content_part.added":
        # status_text += "FINAL RESPONSE:\n"
        # status_placeholder.write(status_text)
        # print(status_text)
      elif event.type == "response.output_text.done":
        # status_text += "\n" + event.text
        # status_placeholder.write(status_text)
        final_output = event.text
        
    final_output_json = csv_to_json(final_output)
    return final_output_json

    # return final_output

if __name__ == "__main__":
  products_json = run_stream()
  print(products_json)
