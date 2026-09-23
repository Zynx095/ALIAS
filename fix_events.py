with open('backend/app/api/events.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out = []
in_fn = False
for line in lines:
    if line.startswith('async def broadcast_ingestion(request: Request, event: dict):'):
        in_fn = True
        out.append(line)
        continue
    
    # End of broadcast_ingestion is when the indentation goes back to def level
    if in_fn and line.startswith('async def'):
        in_fn = False
        
    if in_fn:
        if line == '    if hasattr(request.app.state, \'ws_manager\'):\n':
            out.append('    ws_manager = getattr(request.app.state, \"ws_manager\", None)\n')
            continue
            
        if line.startswith('        '):
            line = line[4:]
            
        if 'await request.app.state.ws_manager.broadcast_event' in line:
            indent = len(line) - len(line.lstrip())
            space = ' ' * indent
            out.append(space + 'if ws_manager:\n')
            out.append(space + '    ' + line.lstrip().replace('request.app.state.ws_manager', 'ws_manager'))
            continue
            
    out.append(line)

with open('backend/app/api/events.py', 'w', encoding='utf-8') as f:
    f.writelines(out)
