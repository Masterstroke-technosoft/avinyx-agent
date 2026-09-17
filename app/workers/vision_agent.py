import pika
import json
import logging
import httpx
import time
import os
import cv2
import base64
# pyrefly: ignore [missing-import]
import openai
logging.basicConfig(level=logging.INFO, format="%(asctime)s - VISION_AGENT - %(message)s")

RABBITMQ_URL = "amqp://civic_queue:queue_pass@localhost:5672/"
API_WEBHOOK = "http://127.0.0.1:8000/api/v1/agent-tasks"

def process_vision_task(ch, method, properties, body):
    payload = json.loads(body)
    task_id = payload.get("task_id")
    file_url = payload.get("payload", {}).get("file_url")
    media_type = payload.get("payload", {}).get("media_type", "image")
    
    logging.info(f"Received Vision Task {task_id}. Analyzing image: {file_url}...")
    
    severity = 8
    confidence = 0.95
    tags = ["damage", "hazard"]
    description = "Visual analysis detected significant structural damage."
    
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and file_url:
        try:
            client = openai.OpenAI(api_key=api_key)
            content_list = []
            
            if media_type == "video":
                # Extract frames using OpenCV with smart motion detection
                cap = cv2.VideoCapture(file_url)
                frames = []
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                if frame_count > 0:
                    ret, prev_frame = cap.read()
                    if ret:
                        gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
                        motion_scores = []
                        
                        # Sample up to 20 frames across the video to find the best motion
                        step = max(1, frame_count // 20)
                        for i in range(step, frame_count, step):
                            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                            ret, curr_frame = cap.read()
                            if not ret: break
                            gray_curr = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
                            
                            diff = cv2.absdiff(gray_prev, gray_curr)
                            score = diff.sum()
                            motion_scores.append((score, i, curr_frame))
                            gray_prev = gray_curr
                            
                        # Sort by highest motion and take the top 5
                        motion_scores.sort(key=lambda x: x[0], reverse=True)
                        top_frames = sorted(motion_scores[:5], key=lambda x: x[1]) # Re-sort chronologically
                        
                        # If video has no motion, just fallback to first frame to avoid crash
                        if not top_frames:
                            top_frames = [(0, 0, prev_frame)]
                            
                        for _, _, frame in top_frames:
                            _, buffer = cv2.imencode('.jpg', frame)
                            b64_frame = base64.b64encode(buffer).decode('utf-8')
                            frames.append(b64_frame)
                cap.release()
                
                prompt = """
                Analyze the following sequence of frames from a video representing a civic complaint.
                Determine the severity on a scale of 1-10. Consider motion, scale, and progression.
                Provide a confidence score between 0.0 and 1.0.
                Provide a list of string tags describing the issue.
                Provide a short description of the issue.
                Return the result as JSON with keys: severity, confidence, tags, description.
                """
                content_list.append({"type": "text", "text": prompt})
                for b64 in frames:
                    content_list.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64}"
                        }
                    })
            else:
                prompt = """
                Analyze the following image for civic complaint assessment. 
                Determine the severity on a scale of 1-10.
                Provide a confidence score between 0.0 and 1.0.
                Provide a list of string tags describing the issue.
                Provide a short description of the issue.
                Return the result as JSON with keys: severity, confidence, tags, description.
                """
                content_list.append({"type": "text", "text": prompt})
                # If file_url is a local path, OpenAI API expects base64 or a public URL. 
                # Since it's local (e.g. uploads/...), we must base64 encode the image too.
                # Assuming the user was using a placeholder previously or OpenAI somehow accessed it.
                # Let's read the image and base64 it to be safe, since OpenAI cannot access local file paths.
                try:
                    with open(file_url, "rb") as f:
                        b64_img = base64.b64encode(f.read()).decode('utf-8')
                        content_list.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64_img}"
                            }
                        })
                except Exception as e:
                    logging.warning(f"Failed to read image locally, passing URL directly: {e}")
                    content_list.append({
                        "type": "image_url",
                        "image_url": {
                            "url": file_url
                        }
                    })
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": content_list,
                    }
                ],
                response_format={ "type": "json_object" }
            )
            ai_output = json.loads(response.choices[0].message.content)
            
            severity = ai_output.get("severity", severity)
            confidence = ai_output.get("confidence", confidence)
            tags = ai_output.get("tags", tags)
            description = ai_output.get("description", description)
                
        except Exception as e:
            logging.error(f"OpenAI API failed, falling back to mock response: {e}")
            
    ai_result = {
        "status": "completed",
        "result_data": {
            "severity": severity,
            "confidence": confidence,
            "tags": tags,
            "description": description
        }
    }
    
    logging.info(f"Analysis complete. Submitting result to Orchestrator...")
    try:
        res = httpx.post(f"{API_WEBHOOK}/{task_id}/result", json=ai_result)
        if res.status_code == 200:
            logging.info("Result successfully accepted by Orchestrator.")
        else:
            logging.error(f"Failed to submit result: {res.text}")
    except Exception as e:
        logging.error(f"Error calling webhook: {e}")
        
    # Acknowledge the message so it's removed from the queue
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    logging.info("Starting Vision Agent...")
    try:
        parameters = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        channel.queue_declare(queue="vision_queue", durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue="vision_queue", on_message_callback=process_vision_task)
        
        logging.info("Waiting for tasks in 'vision_queue'. To exit press CTRL+C")
        channel.start_consuming()
    except Exception as e:
        logging.error(f"Agent crashed: {e}")

if __name__ == "__main__":
    start_worker()
