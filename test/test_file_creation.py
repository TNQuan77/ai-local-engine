#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from tools.file_tools import make_file_tools

# Get the tools
tools = make_file_tools('d:/Project/code')

# create_file is the 3rd function (index 2)
create_file_func = tools[2]

# Test creating a file
result = create_file_func('test/test.html', '<html><body><h1>Test File</h1></body></html>')
print(f"Result: {result}")

# Check if file exists
if os.path.exists('d:/Project/code/test/test.html'):
    print("File was created successfully!")
    with open('d:/Project/code/test/test.html', 'r') as f:
        print(f"Content: {f.read()}")
else:
    print("File was NOT created!")