"""
APEX - Relevance Score Inspector

Prints the actual similarity score for each retrieved chunk, for a given
question. Used to empirically determine a sensible relevance threshold
for the Reference Library retriever - i.e. a cutoff below which a
retrieved chunk should be treated as "not actually relevant" rather than
presented to the model as a genuine match.

Usage:
    python check_relevance.py "What are the FAIR principles for research data?"
    python check_relevance.py "What's the best OCR software for 18th century German handwriting?"
"""

import sys
from rag_backend import index as index_a

if len(sys.argv) < 2:
    print("Please provide a question in quotes, e.g.:")
    print('  python check_relevance.py "What are the FAIR principles?"')
    raise SystemExit()

question = sys.argv[1]
retriever = index_a.as_retriever(similarity_top_k=8)

print(f"\nQuestion: {question}\n")
print(f"{'Score':>8}   File")
print("-" * 60)
for node in retriever.retrieve(question):
    file_name = node.metadata.get("file_name", "unknown")
    print(f"{node.score:8.3f}   {file_name}")
