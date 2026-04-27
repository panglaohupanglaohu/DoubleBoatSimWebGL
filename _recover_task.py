"""Recovery: re-apply code from a completed pipeline run to the project."""
import sys, os
sys.path.insert(0, 'src/backend')
from agents.api import (
    _extract_code_deliverables,
    _save_step_to_pipeline,
    _apply_code_from_pipeline,
    _pipeline_dir,
)

TASK_ID = sys.argv[1] if len(sys.argv) > 1 else "12278c93-4e8"
STEP = sys.argv[2] if len(sys.argv) > 2 else "develop"

# Find the step file (NN_step.md)
pdir = _pipeline_dir(TASK_ID)
print(f"[recover] pipeline dir: {pdir}")
md_file = None
for f in sorted(os.listdir(pdir)):
    if f.endswith(f"_{STEP}.md"):
        md_file = os.path.join(pdir, f)
        break
if not md_file:
    print(f"[recover] no {STEP}.md found")
    sys.exit(1)
print(f"[recover] reading: {md_file}")
text = open(md_file).read()

deliverables = _extract_code_deliverables(text)
print(f"[recover] extracted: {len(deliverables)} deliverables")
for d in deliverables:
    print(f"  - {d['path']}  ({len(d['content'])} chars)")

# Save to pipeline workspace (creates 04_develop/code/...)
saved = _save_step_to_pipeline(TASK_ID, STEP, text, deliverables=deliverables)
print(f"[recover] saved to: {saved}")

# Apply
result = _apply_code_from_pipeline(TASK_ID, STEP)
print(f"[recover] apply result:")
print(f"  applied: {len(result['applied'])}")
for a in result['applied']: print(f"    + {a['path']} ({a['size']}B)")
print(f"  skipped: {len(result['skipped'])}")
for s in result['skipped']: print(f"    ~ {s['path']}: {s['reason']}")
print(f"  failed:  {len(result['failed'])}")
for f in result['failed']: print(f"    ! {f['path']}: {f['error']}")
