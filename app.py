import os
import time
from fastapi import FastAPI, Request
from openai import OpenAI
from dotenv import load_dotenv
import concurrent.futures

load_dotenv("key.env")

openai_api_key = os.getenv('APIKEYS')
OpenAI.api_key = openai_api_key

ASSISTANT_ID = "asst_sqswGlhWTMoyBGAnByXnC8GB"
client = OpenAI(api_key=openai_api_key)

app = FastAPI()

def process_request(user_message):
    try:
        # Tentar várias vezes se a solicitação falhar
        max_retries = 3
        for attempt in range(max_retries):
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
                    time.sleep(1)  # Adicionar um pequeno atraso para evitar loop ocupando CPU
                    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

                message_response = client.beta.threads.messages.list(thread_id=thread.id)
                messages = message_response.data

                latest_message = messages[0].content[0].text.value

                return latest_message

            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return {"error": str(e)}

    except Exception as e:
        return {"error": str(e)}

@app.post('/InPush')
async def ask_assistant(request: Request):
    data = await request.json()
    user_message = data.get("message", "")

    if not user_message:
        return {"error": "No message provided"}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(process_request, user_message)
        response = future.result()

    if isinstance(response, dict) and "error" in response:
        return {"error": response["error"]}

    return {"response": response}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
