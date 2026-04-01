import pathlib

B = pathlib.Path("/Users/panglaohu/Downloads/DoubleBoatClawSystem/src/backend/channels")
SB = chr(35) + chr(33) + "/usr/bin/env python3\n"

def wf(name, body):
    p = B / name
    p.write_text(SB + body)
    print(f"Created {name}: {p.stat().st_size} bytes, {len(p.read_text().splitlines())} lines")

print("Generator loaded OK")
