"""
APEX - Chunk Inspector

Shows the actual text stored inside a few chunks of one file,
to check whether the PDF was extracted cleanly or is garbled.

Usage:
    python inspect_chunks.py 04_communication_zhang_visual-data-storytelling_2022.pdf
    python inspect_chunks.py 03_hitl_guingrich_belief-offloading_2026.pdf
"""

import sys
import chromadb

if len(sys.argv) < 2:
    print("Please provide a file name, e.g.:")
    print("  python inspect_chunks.py 04_communication_zhang_visual-data-storytelling_2022.pdf")
    raise SystemExit()

target_file = sys.argv[1]

db = chromadb.PersistentClient(path="./chroma_db")
collection = db.get_or_create_collection("apex_db_a")

data = collection.get(include=["metadatas", "documents"])

matches = [
    (meta.get("file_name", ""), doc)
    for meta, doc in zip(data["metadatas"], data["documents"])
    if meta.get("file_name", "") == target_file
]

print(f"Found {len(matches)} chunks for {target_file}\n")

# Show length stats
lengths = [len(doc) for _, doc in matches]
if lengths:
    print(f"Shortest chunk: {min(lengths)} characters")
    print(f"Longest chunk:  {max(lengths)} characters")
    print(f"Average chunk:  {sum(lengths) // len(lengths)} characters\n")

# Print the first 5 chunks in full for manual inspection
print("--- First 5 chunks (raw text) ---\n")
for i, (name, doc) in enumerate(matches[:5]):
    print(f"[Chunk {i}] ({len(doc)} characters)")
    print(doc)
    print("-" * 60)
