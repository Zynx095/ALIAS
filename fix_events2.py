with open('backend/app/api/events.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('    try:\n        ws_manager', '    try:\n        ws_manager')
# actually wait, I just need to remove '    try:\n' on line 19 and indent everything until except.
