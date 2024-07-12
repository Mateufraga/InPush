import os
import time
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("key.env")

openai_api_key = os.getenv('APIKEYS')
OpenAI.api_key = openai_api_key

ASSISTANT_ID = "asst_sqswGlhWTMoyBGAnByXnC8GB"
client = OpenAI(api_key=openai_api_key)

app = Flask(__name__)

@app.route('/InPush', methods=['POST'])
def ask_assistant():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

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
        print(f"👉 Run Created: {run.id}")

        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            print(f"🏃 Run Status: {run.status}")
            time.sleep(1)
        else:
            print(f"🏁 Run Completed!")

        message_response = client.beta.threads.messages.list(thread_id=thread.id)
        messages = message_response.data

       
        latest_message = messages[0].content[0].text.value
        print(f"💬 Response: {latest_message}")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"response": latest_message})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
