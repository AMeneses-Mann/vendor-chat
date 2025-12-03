import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
import pandas as pd
import csv
from io import StringIO

with open('product-headings.csv', 'r') as file:
  csv_data = file.read()


# Load key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")

example_row = "Linear Light","Up/Down LED Linear Light J-LS02 ","$53.00","50/35/25/15W","3500K/4000K/5000K","","","AC120-277V","6500/4550/3250/1950 lm","130LM/W","0-10V dimming; wattage & 3 CCT tunable","UL & DLC 5.1 premium","DB77E-4-50W-A5C3","5.1 premium","","6",""

def write_csv_file(csv_string):
  csv_file_like = StringIO(csv_string)
  reader = csv.reader(csv_file_like)
  with open('output.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    for row in reader:
      writer.writerow(row)

def csv_to_json(csv_string, json_file_path):
  csv_file_like = StringIO(csv_string)
  df = pd.read_csv(csv_file_like)
  df.to_json(json_file_path, orient='records', indent=4)
  
def run_stream():
  # Create placeholders for different types of updates
  status_placeholder = st.empty()

  # Stream text tokens to Streamlit as they arrive.
  with client.responses.stream(
    model="gpt-5",
    input=[
      # {
      #     "role": "user",
      #     "content": "Write a haiku",
      # },
       {
         "role": "user", "content":
         f"Use file search to read the attached vector store's data. The data includes specs and costs of LED lighting fixtures. Extract the information about each product and place it in the following CSV. The CSV contains headers under which to put the relevant piece of data for the product. Output the modified CSV ONLY, directly in the response. If a product doesn't have a particular piece of data, just leave the relevant cell blank. Note: skip accessories, focusing only on main products and make sure every main product is included. Here is CSV data:\n\n{csv_data}\n\n and here is an example row to help guide cell value formatting:\n\n{example_row}\n\n"
       },
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
        
  return final_output

if __name__ == "__main__":
  
  products_data = run_stream()
  write_csv_file(products_data)
  output_json = csv_to_json(products_data)
  
  print(output_json)


