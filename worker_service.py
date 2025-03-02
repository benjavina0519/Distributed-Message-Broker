import os
import pika
import json
import openai
import re
from pymongo import MongoClient

# Environment variables
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "financial_data_queue")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

with open('ChatGPT API Key.txt', "r") as file:
    OPENAI_API_KEY = file.read().strip()
    
openai.api_key = OPENAI_API_KEY

client = MongoClient(MONGO_URI)
db = client["financial_db"]         # Database name
collection = db["financial_data"]   # Collection name

def read_api_key(file_path):
    with open(file_path, "r") as file:
        return file.read().strip()  # Removes any leading/trailing whitespace

def parse_value(value_str):
    """
    Convert strings like '5.3 million' to integer 5300000.
    Handles various formats such as:
    - 5 million -> 5000000
    - 5.3 million -> 5300000
    - 5 -> 5 (assuming plain integer)
    """
    # Basic pattern matching for "X million" or "X.X million"
    match = re.match(r"([\d\.]+)\s*million", value_str, re.IGNORECASE)
    if match:
        base_value = float(match.group(1))
        return int(base_value * 1_000_000)
    
    # Basic pattern matching for "X billion"
    match = re.match(r"([\d\.]+)\s*billion", value_str, re.IGNORECASE)
    if match:
        base_value = float(match.group(1))
        return int(base_value * 1_000_000_000)
    
    # If none of the above patterns match, try a plain float or int
    try:
        return int(float(value_str))
    except ValueError:
        # If even that fails, return as-is or handle error
        return value_str

def extract_financial_data(raw_text):
    """
    Calls ChatGPT API to extract financial data from the raw_text.
    Expects a JSON response with keys: company, metric, value, currency, quarter
    """
    prompt = f"""
    You are a financial data extraction system.
    Given the following text, extract and return the data in JSON format with keys:
    company, metric, value, currency, quarter.
    
    Text:
    {raw_text}
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.0,
        )

        # Extract content (the JSON) from ChatGPT
        content = response.choices[0].message.content
        data = json.loads(content)  # Parse JSON

        # Normalize the 'value' field
        if "value" in data:
            data["value"] = parse_value(str(data["value"]))

        return data
    except Exception as e:
        print(f"Error in ChatGPT extraction: {e}")
        return None

def callback(ch, method, properties, body):
    """
    Callback function to handle messages from RabbitMQ.
    """
    try:
        raw_message = json.loads(body)
        raw_text = raw_message.get("raw_text", "")
        extracted_data = extract_financial_data(raw_text)

        if extracted_data:
            # Insert into MongoDB
            collection.insert_one(extracted_data)
            print(f"Data inserted into MongoDB: {extracted_data}")
        else:
            print("Failed to extract data.")

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def start_consumer():
    """
    Setup RabbitMQ consumer and start listening.
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE)
    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)
    print("Worker service is listening for messages...")
    channel.start_consuming()

if __name__ == "__main__":
    start_consumer()
