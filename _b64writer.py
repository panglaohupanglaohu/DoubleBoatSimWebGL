import pathlib, base64, sys
data = pathlib.Path(sys.argv[1]).read_bytes()
content = base64.b64decode(data).decode('utf-8')  
target = '/Users/panglaohu/Downloads/DoubleBoatClawSystem/src/frontend/agent-team-config.html'
pathlib.Path(target).write_text(content)
print('Written', len(content.splitlines()), 'lines,', len(content), 'bytes')
