"""
APEX - Reference Library Health Check

Run this any time with:
    python check_database.py

It does NOT call the language model at all - it only looks directly into
ChromaDB and reports what actually got stored. Useful to check that
embedding worked, and that every PDF contributed chunks.
"""

import chromadb

EXPECTED_FILES = [
    "01_foundation_wilkinson_fair_2016.pdf",
    "01_foundation_tayler_dataprimer_2022.pdf",
    "02_analysis_underwood_distant-reading_2017.pdf",
    "02_analysis_clement_methodology-dh_2016.pdf",
    "02_analysis_perkins-roe_genai-research_2024.pdf",
    "02_analysis_desapereira_mixed-methods_2019.pdf",
    "03_hitl_guingrich_belief-offloading_2026.pdf",
    "03_hitl_kalai_why-llms-hallucinate_2025.pdf",
    "03_hitl_simons_llms-hpss_2025.pdf",
    "04_communication_sanz-tejeda_genai-reading-writing_2025.pdf",
    "04_communication_zhang_visual-data-storytelling_2022.pdf",
]

db = chromadb.PersistentClient(path="./chroma_db")
collection = db.get_or_create_collection("apex_db_a")

total_chunks = collection.count()
print(f"Total chunks stored in ChromaDB: {total_chunks}")

if total_chunks == 0:
    print("\nWARNING: The database is empty. Something went wrong when building it.")
    print("Delete the 'chroma_db' folder and run 'python rag_backend.py' again.")
    raise SystemExit()

# Pull all stored chunks with their metadata (file name)
all_data = collection.get(include=["metadatas"])
file_names = [m.get("file_name", "unknown") for m in all_data["metadatas"]]

# Count chunks per file
counts = {}
for name in file_names:
    counts[name] = counts.get(name, 0) + 1

print("\nChunks per source file:")
for name, count in sorted(counts.items()):
    print(f"  {count:>3}  {name}")

# Check which expected files are missing entirely
found_files = set(counts.keys())
missing = [f for f in EXPECTED_FILES if f not in found_files]

print("\n--- Sanity check ---")
if missing:
    print("WARNING: These expected files produced NO chunks at all:")
    for f in missing:
        print("  -", f)
    print("This usually means the PDF is a scanned image with no selectable")
    print("text, or the file name doesn't match exactly.")
else:
    print("All 11 expected files are present in the database.")

# Flag any file with suspiciously few chunks (possible extraction problem)
thin = {name: c for name, c in counts.items() if c <= 1}
if thin:
    print("\nNOTE: These files produced very few chunks (1 or 0):")
    for name, c in thin.items():
        print(f"  - {name} ({c} chunk)")
    print("Worth double-checking these PDFs open normally and contain real text.")
