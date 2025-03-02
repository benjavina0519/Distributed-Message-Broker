# Distributed Message Broker with FastAPI, RabbitMQ, and MongoDB

This project implements a **distributed message processing system** using **FastAPI, RabbitMQ, and MongoDB**. It includes:
- Producer Service (FastAPI) → Accepts raw financial data and sends messages to RabbitMQ.
- Worker Service (Consumer) → Listens for messages, processes data using OpenAI's API, and stores results in MongoDB.
- MongoDB Storage → Stores extracted structured data.

---

## Project Architecture  
[Client] → (FastAPI Producer) → [RabbitMQ Queue] → (Worker Service) → [MongoDB Storage]  

1. Producer (FastAPI) receives financial text via a POST API and sends it to RabbitMQ.  
2. RabbitMQ (Message Broker) queues the messages asynchronously.  
3. Worker Service (Consumer) listens for messages, extracts structured data using OpenAI API, and stores it in MongoDB.  
4. MongoDB stores the processed financial data.  

---

## Prerequisites  

Install the necessary dependencies before running the project:  
- Python 3.8+  
- Docker (if using RabbitMQ/MongoDB in containers)  
- MongoDB (local or Docker)  
- RabbitMQ (local or Docker)  

Install required Python packages:  
```sh
pip install fastapi uvicorn pika pymongo openai python-dotenv
```

---

## Installation & Setup  

### 1. Start RabbitMQ  

#### Option 1: Run RabbitMQ in Docker  
```sh
docker run -d --hostname my-rabbit --name some-rabbit -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```  
Access RabbitMQ Web UI → http://localhost:15672  
Default Credentials → Username: `guest` | Password: `guest`  

#### Option 2: Run RabbitMQ Locally  

Mac/Linux:  
```sh
brew install rabbitmq
rabbitmq-server start
```  
Ubuntu:  
```sh
sudo apt install rabbitmq-server
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server
```  

---

### 2. Start MongoDB  

#### Option 1: Run MongoDB in Docker  
```sh
docker run -d --name some-mongo -p 27017:27017 mongo
```  

#### Option 2: Run MongoDB Locally  

Mac:  
```sh
brew install mongodb-community@6.0
brew services start mongodb-community@6.0
```  
Ubuntu:  
```sh
sudo apt install mongodb-org
sudo systemctl start mongod
```  

---

### 3. Set Up Environment Variables  

Create a `.env` file in the project directory:  
```sh
touch .env
```  
Edit `.env` and add the following:  
```
RABBITMQ_HOST=localhost
RABBITMQ_QUEUE=financial_data_queue
MONGO_URI=mongodb://localhost:27017/
OPENAI_API_KEY=your-api-key-here
```

---

### 4. Start Producer Service (FastAPI)  

Run the FastAPI app:  
```sh
uvicorn producer_service:app --host 0.0.0.0 --port 8000
```  
Now, FastAPI is running at → http://localhost:8000  
OpenAPI Docs → http://localhost:8000/docs  

---

### 5. Start Worker Service (Consumer)  

In another terminal, start the worker:  
```sh
python worker_service.py
```  
The worker listens for messages from RabbitMQ and stores extracted data in MongoDB.  

---

### 6. Send Test Requests  

#### Test Using cURL  
```sh
curl -X POST http://localhost:8000/submit \
     -H "Content-Type: application/json" \
     -d '{"raw_text": "Acme Inc reported a net income of 5.3 million USD for Q1 2024."}'
```  

#### Test Using Python  
```python
import requests

API_URL = "http://localhost:8000/submit"
payload = {"raw_text": "Acme Inc reported a revenue of 30.5 million USD for Q3 2024."}

response = requests.post(API_URL, json=payload)
print(response.json())
```

---

## Query Data in MongoDB  

### Open Mongo Shell  
```sh
mongosh
```  
Switch to the database:  
```js
use financial_db
db.financial_data.find().pretty()
```  
This will display structured financial data extracted by OpenAI.  

---

## Troubleshooting  

### RabbitMQ Not Running?  
Check if RabbitMQ is active:  
```sh
docker ps | grep rabbitmq
```  
If not running, restart:  
```sh
docker start some-rabbit
```  

### MongoDB Connection Issues?  
Check if MongoDB is running:  
```sh
docker ps | grep mongo
```  
If not running, restart:  
```sh
docker start some-mongo
```  

### OpenAI API Errors?  
If you get quota exceeded (429):  
1. Check usage: OpenAI Dashboard  
2. Add a payment method: Billing Page  

---

## Bonus Features  

- Dockerize Everything → Use a Dockerfile and docker-compose.yml  
- Unit Testing → Test RabbitMQ, OpenAI API, and MongoDB interactions using pytest  
- Scalability → Add multiple worker instances to process messages in parallel  

---

## Resources  

- FastAPI Docs → https://fastapi.tiangolo.com/  
- RabbitMQ Docs → https://www.rabbitmq.com/documentation.html  
- MongoDB Docs → https://www.mongodb.com/docs/manual/  
- OpenAI API Docs → https://platform.openai.com/docs/  

