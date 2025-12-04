import os
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
import csv
import json
from io import StringIO

try:
  with open('product-headings.csv', 'r') as file:
    csv_data = file.read()
except FileNotFoundError:
  print("Error: product-headings.csv not found")
  exit(1)
except Exception as e:
  print(f"Error reading product-headings.csv: {e}")
  exit(1)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")

if not os.getenv("OPENAI_API_KEY"):
  print("Error: OPENAI_API_KEY not found in environment")
  exit(1)
if not VECTOR_STORE_ID:
  print("Error: VECTOR_STORE_ID not found in environment")
  exit(1)

example_row = """"Main Category",Title,"Vendor Cost","wattage",color_temperature,cover,enclosure_rating,"input_voltage","light_output",luminous_efficacy,features,"ratings_certifications","manufacturer_part_number",dlc_version,"dlc_integrated_control","quantity_in_pack",vendor
"Linear Light","Up/Down LED Linear Light J-LS02 ","$53.00","50/35/25/15W","3500K/4000K/5000K","","","AC120-277V","6500/4550/3250/1950 lm","130LM/W","0-10V dimming; wattage & 3 CCT tunable","UL & DLC 5.1 premium","DB77E-4-50W-A5C3","5.1 premium","","6","""""
      
def save_csv(csv_string: str, directory: str, filename: str):
  try:
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, "w", encoding="utf-8") as f:
      f.write(csv_string)
  except Exception as e:
    print(f"Error saving CSV: {e}")
    raise
      
def csv_to_json(csv_string: str):
  try:
    f = StringIO(csv_string)
    reader = csv.DictReader(f)
    return list(reader)
  except Exception as e:
    print(f"Error converting CSV to JSON: {e}")
    raise
  
def ai_read_pdf():
  try:
    with client.responses.stream(
      model="gpt-5",
      input=[
        {
          "role": "user", "content":
          "write a haiku"
        },
        # {
        #   "role": "user", "content":
        #   f"Use file search to read the attached vector store's data. The data includes specs and costs of LED lighting fixtures. Extract the information about each product and place it in the following CSV. The CSV contains headers under which to put the relevant piece of data for the product. Output the modified CSV ONLY, directly in the response. If a product doesn't have a particular piece of data, just leave the relevant cell blank. Note: skip accessories, focusing only on main products and make sure every main product is included. Here is CSV data:\n\n{csv_data}\n\n and here is it with an example row to help guide cell value formatting:\n\n{example_row}\n\n"
        # },
      ],
      text={"format": {"type": "text"}, "verbosity": "low"},
      reasoning={"effort": "medium", "summary": "auto"},
      tools=[
        {"type": "file_search", "vector_store_ids": [VECTOR_STORE_ID]},
      ],
      store=True,
      include=[
        "file_search_call.results",
      ],
    ) as stream:
      status_text = ""
      final_output = ""

      for event in stream:
        if event.type == "response.reasoning_summary_text.done":
          status_text += event.text + "\n"
          print(status_text)
        elif event.type == "response.file_search_call.in_progress":
          status_text += "\nSearching file\n"
          print(status_text)
        elif event.type == "response.output_text.done":
          final_output = event.text
          
    return final_output
  
  except Exception as e:
    print(f"Error during API streaming: {e}")
    raise
  
def ai_search_web(data):
  try:
    with client.responses.stream(
      model="gpt-5",
      input=[
        {
          "role": "user", "content":
          "Can you find the products included in the following json on amazon.com?\n\n{data}\n\n"
        },
      ],
      text={"format": {"type": "text"}, "verbosity": "low"},
      reasoning={"effort": "medium", "summary": "auto"},
      tools=[{"type": "web_search"}],
      store=True,
      include=[
        "web_search_call.results",
      ],
    ) as stream:
      status_text = ""
      final_output = ""

      for event in stream:
        if event.type == "response.reasoning_summary_text.done":
          status_text += event.text + "\n"
          print(status_text)
        elif event.type == "response.file_search_call.in_progress":
          status_text += "\nSearching file\n"
          print(status_text)
        elif event.type == "response.output_text.done":
          final_output = event.text
          
    return final_output
  
  except Exception as e:
    print(f"Error during API streaming: {e}")
    raise


if __name__ == "__main__":
  try:
    # products_data = ai_read_pdf()
    # if not products_data:
    #   print("Warning: No data returned from API")
    #   exit(1)
    
    # if not products_data.strip().startswith('"Main Category"'):
    #   print("Unexpected response format. Output:\n", products_data)
    #   exit(1)
    
    # save_csv(products_data, "./", "products.csv")
    # output_json = csv_to_json(products_data)
    # print("FINAL OUTPUT\n", output_json)
    json_array = [
      {
        "Main Category": "Linear Light",
        "Title": "Up/Down LED Linear Light J-LS02 ",
        "Vendor Cost": "$53.00",
        "wattage": "50/35/25/15W",
        "color_temperature": "3500K/4000K/5000K",
        "cover": "",
        "enclosure_rating": "",
        "input_voltage": "AC120-277V",
        "light_output": "6500/4550/3250/1950 lm",
        "luminous_efficacy": "130LM/W",
        "features": "0-10V dimming; wattage & 3 CCT tunable",
        "ratings_certifications": "UL & DLC 5.1 premium",
        "manufacturer_part_number": "DB77E-4-50W-A5C3",
        "dlc_version": "5.1 premium",
        "dlc_integrated_control": "null",
        "quantity_in_pack": 6,
        "vendor": ""
      },
      {
        "Main Category": "Linear Light",
        "Title": "Up/Down LED Linear Light J-LS03 ",
        "Vendor Cost": "$47.00",
        "wattage": "50W",
        "color_temperature": "3000K/4000K/5000K",
        "cover": "",
        "enclosure_rating": "",
        "input_voltage": "AC120-277V",
        "light_output": "max 6500 lm",
        "luminous_efficacy": "130LM/W",
        "features": "0-10V dimming; 3 CCT selectable",
        "ratings_certifications": "UL & DLC",
        "manufacturer_part_number": "J-4FT-UD-50W-30K/40K/50K",
        "dlc_version": "",
        "dlc_integrated_control": "null",
        "quantity_in_pack": 4,
        "vendor": ""
      },
    ]
    
    json_string = json.dumps(json_array, indent=2)
    output = ai_search_web(json_string)
    print(output)
    
  except Exception as e:
    print(f"Error in main execution: {e}")
    exit(1)
    
    