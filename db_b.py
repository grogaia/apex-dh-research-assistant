"""
APEX - Corpus module (user-uploaded project documents)

Builds a TEMPORARY, in-memory vector index from files the user uploads
in the Streamlit app. Unlike the Reference Library, this is NOT saved to disk -
it exists only while the app is running, and disappears when it's closed
or when new files are uploaded.

Supports any file type Llama-Index's SimpleDirectoryReader recognizes,
except images and audio/video (kept out to avoid heavy extra dependencies
and because they're outside APEX's text-based scope). This includes:
.pdf, .docx, .xlsx/.xls, .csv, .txt, .md, .xml (e.g. TEI), .pptx/.ppt,
.epub, .ipynb, .mbox, .hwp. Formats without a dedicated reader (like .txt,
.md, .xml) automatically fall back to being read as plain text.
"""

import tempfile
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader


def build_database_b(uploaded_files):
    """
    Takes a list of Streamlit UploadedFile objects and returns
    (index_b, error_message) - index_b is a VectorStoreIndex built purely
    in memory (no ChromaDB, no disk storage), or None if the list is empty
    or if something went wrong. error_message is None on success, or a
    short, friendly explanation if a file couldn't be read.
    """
    if not uploaded_files:
        return None, None

    # Streamlit gives us in-memory file objects, but SimpleDirectoryReader
    # needs real files on disk to read them. So we save them into a
    # temporary folder first, read them, and the folder is auto-deleted
    # afterwards (that's what the "with" block below does).
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            for uploaded_file in uploaded_files:
                file_path = os.path.join(tmp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            documents = SimpleDirectoryReader(tmp_dir).load_data()
            if not documents:
                return None, "No readable text was found in the uploaded file(s)."
            index_b = VectorStoreIndex.from_documents(documents)
        return index_b, None
    except Exception as e:
        return None, f"Couldn't read one of your files ({e.__class__.__name__}). Try a different file or format."
