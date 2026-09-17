import pika
import json
import logging
import httpx
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - GEO_AGENT - %(message)s")

RABBITMQ_URL = "amqp://civic_queue:queue_pass@localhost:5672/"
API_WEBHOOK = "http://127.0.0.1:8000/api/v1/agent-tasks"

# Simulated memory for duplicate detection (In production, this would query Postgres or Redis)
recent_locations = {}

def process_geo_task(ch, method, properties, body):
    payload = json.loads(body)
    task_id = payload.get("task_id")
    case_id = payload.get("case_id")
    geo_data = payload.get("payload", {})
    
    lat = geo_data.get("latitude")
    lon = geo_data.get("longitude")
    ward = geo_data.get("ward")
    
    logging.info(f"Received Geo Task {task_id}. Analyzing coordinates: {lat}, {lon} (Ward: {ward})")
    time.sleep(1) # Simulate geospatial calculation
    
    # Simple Duplicate Detection Logic
    location_key = f"{lat},{lon}"
    if location_key in recent_locations:
        recent_locations[location_key] += 1
        count = recent_locations[location_key]
        logging.warning(f"DUPLICATE DETECTED! Location {location_key} has {count} reports today.")
        
        # Post back to webhook to update status to clustered/duplicate
        ai_result = {
            "status": "completed",
            "result_data": {
                "geo_cluster": True,
                "cluster_count": count,
                "message": "Flagged as duplicate based on proximity to existing reports."
            }
        }
        try:
            httpx.post(f"{API_WEBHOOK}/{task_id}/result", json=ai_result)
        except Exception as e:
            logging.error(f"Error calling webhook: {e}")
            
    else:
        logging.info(f"Location is clear. First report for coordinates {location_key}.")
        recent_locations[location_key] = 1
        
        # Post back success to orchestrator
        ai_result = {
            "status": "completed",
            "result_data": {
                "geo_cluster": False,
                "message": "Location is clear. No nearby duplicates found."
            }
        }
        try:
            httpx.post(f"{API_WEBHOOK}/{task_id}/result", json=ai_result)
        except Exception as e:
            logging.error(f"Error calling webhook: {e}")
        
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    logging.info("Starting Geo-Analytics Agent...")
    try:
        parameters = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        channel.queue_declare(queue="geo_queue", durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue="geo_queue", on_message_callback=process_geo_task)
        
        logging.info("Waiting for spatial tasks in 'geo_queue'. To exit press CTRL+C")
        channel.start_consuming()
    except Exception as e:
        logging.error(f"Agent crashed: {e}")

if __name__ == "__main__":
    start_worker()
