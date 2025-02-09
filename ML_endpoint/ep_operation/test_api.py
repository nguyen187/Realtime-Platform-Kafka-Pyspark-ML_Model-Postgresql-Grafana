import numpy as np
import httpx
import asyncio

# Define the URL of your FastAPI endpoint
url = "http://127.0.0.1:8000/predict"

# Sample input data
input_data = np.array(
    [
        [80, 253.0, 53, 296.0, 13.87591373591667, 73408.0, 5.142756158733616],
        [80, 253.0, 53, 296.0, 13.87591373591667, 73408.0, 5.142756158733616],
    ]
).tolist()

# Create a JSON payload
payload = {"data": input_data}


async def send_request():
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(url, json=payload)

    if response.status_code == 200:
        print("Response from the server:")
        print(response.json())
    else:
        print(f"Failed with status code: {response.status_code}")
        print(response.text)


# Run the async function
asyncio.run(send_request())
