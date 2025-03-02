#!/usr/bin/env python
# coding: utf-8

# In[7]:


import os
import pika
from fastapi import FastAPI, Request
import json

# Environment variables or hard-coded (not recommended for production)
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "financial_data_queue")

app = FastAPI()

def get_rabbitmq_channel():
    """Create and return a RabbitMQ channel."""
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()
    # Declare the queue to ensure it exists
    channel.queue_declare(queue=RABBITMQ_QUEUE)
    return connection, channel

@app.post("/submit")
async def submit_financial_data(request: Request):
    """Endpoint for receiving raw financial data and publishing it to RabbitMQ."""
    data = await request.json()

    # Convert data to JSON string
    message_body = json.dumps(data)

    # Publish message to RabbitMQ
    connection, channel = get_rabbitmq_channel()
    channel.basic_publish(exchange="",
                          routing_key=RABBITMQ_QUEUE,
                          body=message_body)
    connection.close()

    return {"status": "Message published to RabbitMQ", "data": data}


# In[ ]:




