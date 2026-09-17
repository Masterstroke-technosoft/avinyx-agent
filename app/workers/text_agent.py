import pika
import json
import logging
import httpx
import time
import os
import sys
# pyrefly: ignore [missing-import]
import openai
# Ensure we can import app.core
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.core.queue import publish_task

logging.basicConfig(level=logging.INFO, format="%(asctime)s - TEXT_AGENT - %(message)s")

RABBITMQ_URL = "amqp://civic_queue:queue_pass@localhost:5672/"
API_WEBHOOK = "http://127.0.0.1:8000/api/v1/agent-tasks"

def process_text_task(ch, method, properties, body):
    payload = json.loads(body)
    task_id = payload.get("task_id")
    text_content = payload.get("payload", {}).get("description", "")
    
    logging.info(f"Received Text Task {task_id}. Analyzing text: '{text_content}'...")
    
    severity = 3
    intent = "general_complaint"
    is_emergency = False
    language = "en"
    
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            client = openai.OpenAI(api_key=api_key)
            prompt = f"""
            Analyze the following civic complaint text. 
            Determine the severity on a scale of 1-10. 
            Determine the intent (e.g., 'hazardous_emergency', 'pothole', 'noise_complaint').
            Determine if it is an emergency (boolean).
            Identify the language.
            Return the result as JSON with keys: severity, intent, is_emergency, language.
            
            Text: '{text_content}'
            """
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            ai_output = json.loads(response.choices[0].message.content)
            
            severity = ai_output.get("severity", severity)
            intent = ai_output.get("intent", intent)
            is_emergency = ai_output.get("is_emergency", is_emergency)
            language = ai_output.get("language", language)
            
            if is_emergency:
                logging.warning("CRITICAL EMERGENCY DETECTED IN TEXT BY AI!")
                
        except Exception as e:
            logging.error(f"OpenAI API failed, falling back to basic parsing: {e}")
            text_lower = text_content.lower()
            if "spill" in text_lower or "chemical" in text_lower or "live wire" in text_lower or "power line" in text_lower:
                severity = 10
                intent = "hazardous_emergency"
                is_emergency = True
                logging.warning("CRITICAL EMERGENCY DETECTED IN TEXT (FALLBACK)!")
    else:
        # Fallback if no API key
        text_lower = text_content.lower()
        if "spill" in text_lower or "chemical" in text_lower or "live wire" in text_lower or "power line" in text_lower:
            severity = 10
            intent = "hazardous_emergency"
            is_emergency = True
            logging.warning("CRITICAL EMERGENCY DETECTED IN TEXT!")
            
    ai_result = {
        "status": "completed",
        "result_data": {
            "severity": severity,
            "intent": intent,
            "language": language
        }
    }
    
    # 1. Update Orchestrator with the text result
    logging.info(f"Text analysis complete. Submitting to Orchestrator...")
    try:
        httpx.post(f"{API_WEBHOOK}/{task_id}/result", json=ai_result)
    except Exception as e:
        logging.error(f"Error calling webhook: {e}")
        
    # 2. EMERGENCY ROUTING (Orchestrator Role of the Text Agent)
    if is_emergency:
        logging.info("Routing task immediately to the Critical/Emergency Agent Pool!")
        emergency_payload = {
            "case_id": payload.get("case_id"),
            "original_task": task_id,
            "threat_level": "extreme",
            "detected_keywords": intent
        }
        publish_task("emergency_queue", emergency_payload)
        
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    logging.info("Starting Text Agent...")
    try:
        parameters = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        channel.queue_declare(queue="text_queue", durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue="text_queue", on_message_callback=process_text_task)
        
        logging.info("Waiting for tasks in 'text_queue'. To exit press CTRL+C")
        channel.start_consuming()
    except Exception as e:
        logging.error(f"Agent crashed: {e}")

if __name__ == "__main__":
    start_worker()
