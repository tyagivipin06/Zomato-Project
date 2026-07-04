import re

with open("docs/edge-case.md", "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(r"\| \*\*Status\*\* \| 🔲 Stub — to implement in Phase \d+ \|", "| **Status** | ✅ Implemented and Verified |", content)

with open("docs/edge-case.md", "w", encoding="utf-8") as f:
    f.write(content)
