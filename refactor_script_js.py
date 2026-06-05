import os

js_path = os.path.join('static', 'js', 'script.js')
if not os.path.exists(js_path):
    print("script.js not found!")
    exit(1)

with open(js_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = 'const REACTIONS = ['
start_index = content.find(start_marker)
if start_index == -1:
    print("Could not find start of REACTIONS array in script.js")
    exit(1)

# Find the end of the array
bracket_count = 0
index = start_index

# Find the opening bracket
while index < len(content) and content[index] != '[':
    index += 1

if index >= len(content):
    print("Could not find [ after REACTIONS marker")
    exit(1)

bracket_count = 1
index += 1

while index < len(content) and bracket_count > 0:
    if content[index] == '[':
        bracket_count += 1
    elif content[index] == ']':
        bracket_count -= 1
    index += 1

# Check for the semicolon after the closing bracket
while index < len(content) and content[index] in (';', '\r', '\n', ' '):
    index += 1

array_block = content[start_index:index]

replacement = """let REACTIONS = [];

// Dynamically fetch reactions from the server database
fetch('/api/reactions')
  .then(res => res.json())
  .then(data => {
    REACTIONS = data.reactions || [];
    console.log("Successfully loaded " + REACTIONS.length + " reactions dynamically.");
    if (typeof filterReactions === 'function') {
      filterReactions();
    }
  })
  .catch(err => console.error("Error loading reactions from database:", err));
"""

# Replace the block
new_content = content[:start_index] + replacement + content[index:]

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Successfully refactored script.js for dynamic reaction loading!")
