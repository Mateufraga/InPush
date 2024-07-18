import os
import time
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import concurrent.futures

load_dotenv("key.env")

openai_api_key = os.getenv('APIKEYS')
OpenAI.api_key = openai_api_key

ASSISTANT_ID = "asst_sqswGlhWTMoyBGAnByXnC8GB"
client = OpenAI(api_key=openai_api_key)

app = Flask(__name__)

def process_request(user_message):
    try:
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": user_message,
                }
            ]
        )

        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=ASSISTANT_ID)

        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            time.sleep(1)

        message_response = client.beta.threads.messages.list(thread_id=thread.id)
        messages = message_response.data

        latest_message = messages[0].content[0].text.value

        return latest_message

    except Exception as e:
        return {"error": str(e)}

@app.route('/InPush', methods=['POST'])
def ask_assistant():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(process_request, user_message)
        response = future.result()

    if isinstance(response, dict) and "error" in response:
        return jsonify({"error": response["error"]}), 500

    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
