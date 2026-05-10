#!/usr/bin/env python3
import requests
import json

# Test the chat API
url = "http://localhost:8000/api/chat"
data = {
    "messages": [
        {"role": "user", "content": "Create a simple HTML file called test2.html with content '<html><body><h1>Hello World</h1></body></html>'"}
    ],
    "model": "qwen2.5-coder:7b",
    "provider": "local",
    "working_dir": "d:/Project/code"
}

print("Sending request to backend...")
response = requests.post(url, json=data, stream=True, timeout=30)

if response.status_code == 200:
    print("Response received:")
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            print(f"Raw line: {line_str}")
            if line_str.startswith('data: '):
                data_str = line_str[6:]  # Remove 'data: ' prefix
                try:
                    event = json.loads(data_str)
                    print(f"Event: {event}")
                    if event.get('type') == 'tool_call':
                        print(f"TOOL CALL: {event}")
                    elif event.get('type') == 'tool_result':
                        print(f"TOOL RESULT: {event}")
                    elif event.get('type') == 'text':
                        print(f"TEXT: {event['content']}")
                except json.JSONDecodeError:
                    print(f"JSON error: {data_str}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)