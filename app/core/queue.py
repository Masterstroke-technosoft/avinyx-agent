import pika
import json
import logging

# We will read this from env in production, but hardcode for local dev for now
RABBITMQ_URL = "amqp://civic_queue:queue_pass@localhost:5672/"

def get_connection():
    try:
        parameters = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        return connection
    except Exception as e:
        logging.error(f"Failed to connect to RabbitMQ: {e}")
        return None

def publish_task(queue_name: str, payload: dict):
    """
    Publish a JSON task to the specified RabbitMQ queue.
    """
    connection = get_connection()
    if not connection:
        logging.warning("RabbitMQ is not reachable. Skipping queue publishing.")
        return False
        
    try:
        channel = connection.channel()
        # Declare queue (creates it if it doesn't exist, ensures we can publish safely)
        channel.queue_declare(queue=queue_name, durable=True)
        
        message = json.dumps(payload)
        
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
            
        logging.info(f"Published task to {queue_name}: {message}")
        connection.close()
        return True
    except Exception as e:
        logging.error(f"Failed to publish message: {e}")
        if connection:
            connection.close()
        return False
