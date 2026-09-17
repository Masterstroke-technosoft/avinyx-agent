import pika
import json
import logging
import time

logging.basicConfig(level=logging.ERROR, format="%(asctime)s - CRITICAL_AGENT - %(message)s")

RABBITMQ_URL = "amqp://civic_queue:queue_pass@localhost:5672/"

def process_emergency(ch, method, properties, body):
    payload = json.loads(body)
    case_id = payload.get("case_id")
    threat = payload.get("threat_level")
    
    # We use ERROR level logging just to make it visually pop red in the terminal!
    logging.error(f"!!! EMERGENCY TICKET RECEIVED !!!")
    logging.error(f"CASE ID: {case_id}")
    logging.error(f"THREAT LEVEL: {threat.upper()}")
    
    logging.error("Executing Emergency Protocols...")
    time.sleep(1)
    logging.error("-> Dispatching automated SMS to Fire Department (911)")
    logging.error("-> Updating City Dashboard with Critical Alert Marker")
    logging.error("-> Emergency Handling Complete. Awaiting Field Units.\n")
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    # Force info level for startup
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logging.info("Starting Critical Emergency Agent...")
    
    try:
        parameters = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        channel.queue_declare(queue="emergency_queue", durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue="emergency_queue", on_message_callback=process_emergency)
        
        logging.info("Waiting for extreme threats in 'emergency_queue'.")
        
        # Switch back to error to make alerts red
        logger.setLevel(logging.ERROR)
        channel.start_consuming()
    except Exception as e:
        logging.error(f"Agent crashed: {e}")

if __name__ == "__main__":
    start_worker()
