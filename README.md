# APEX — Augmented Project & Execution Engine

APEX is a dual-RAG (Retrieval-Augmented Generation) research companion for
Digital Humanities (DH) students. It combines a small, hand-curated library of
open-licensed DH methodology sources with the user's own project material, and
it is built around a single principle: **the AI proposes, the human decides.**
Rather than acting as an oracle, APEX surfaces methodological options, applies
them to the user's own documents, and is transparent at every step about where
each part of an answer actually comes from.

---

## Table of contents

1. [Vision](#vision)
2. [What makes APEX different](#what-makes-apex-different)
3. [Architecture](#architecture)
4. [The curated Reference Library](#the-curated-reference-library)
5. [Setup](#setup)
6. [Usage](#usage)
7. [Project structure](#project-structure)
8. [Evaluation](#evaluation)
9. [Critical reflection](#critical-reflection)
10. [Known limitations](#known-limitations)
11. [Licensing](#licensing)

---

## Vision

Generative AI is increasingly present in humanities research, but general-purpose
chat tools have two structural weaknesses for scholarly work: they blur the line
between grounded knowledge and plausible invention, and they encourage users to
delegate their own judgement to the model. APEX is designed as a *cognitive
catalyst* rather than an answer machine. It supports a DH project at any stage —
from early planning, through data collection and analysis, to communicating
findings — while keeping the researcher in control of every methodological
decision.

The name reflects the project's guiding metaphor of a structured ascent toward a
goal, organised into four phases: **Foundation**, **Ascent** (analysis),
**Checkpoint** (human-in-the-loop), and **Summit** (communication).

## What makes APEX different

- **Curated methodology, not training-data guesswork.** APEX draws on a small
  set of hand-selected, openly licensed DH sources — not on whatever the model
  happened to absorb during training.
- **Grounded in the user's own material.** Uploaded project documents form a
  *Corpus* that the retrieved methodology is applied to directly and concretely.
- **Transparency instead of silent guessing.** Every answer indicates whether it
  is grounded in the curated Reference Library, in the user's own documents, or
  in the model's general reasoning. When a question falls outside the curated
  sources, APEX says so explicitly before answering from general knowledge.
- **The human stays in the loop.** After each answer, APEX proposes concrete
  next steps, but the user always chooses the direction.

## Architecture

APEX uses two independent retrieval sources, deliberately kept separate because
they play different roles:

| Source | Role | Storage |
|---|---|---|
| **Reference Library** | Curated DH methodology (the "how") | Persistent local vector database (ChromaDB) |
| **Corpus** | The user's own project material (the "what") | Temporary, in-memory index, rebuilt per session |

### Retrieval and answer flow

1. A question is embedded and matched against both sources.
2. Retrieved chunks are filtered by a **relevance threshold** (see below) so that
   weak, incidental matches are discarded rather than presented as genuine
   sources.
3. The Reference Library provides the methodological grounding; the Corpus
   provides the material the methodology is applied to.
4. If neither source genuinely covers the question, APEX states this explicitly
   and then answers from the model's general reasoning, clearly labelled.
5. A concise set of core DH principles is kept as light background awareness, so
   that specific answers stay anchored to the retrieved sources instead of
   defaulting to generic advice.

### The relevance threshold

A standard vector retriever always returns its top-*k* nearest chunks, regardless
of how weak the match is — so an out-of-scope question still receives "the least
bad" results from the small corpus, which can then be misattributed as genuine
sources. To prevent this, APEX discards any retrieved chunk whose similarity
score falls below a fixed threshold.

The threshold was calibrated empirically rather than guessed. Comparing an
in-scope question against an out-of-scope one produced a clear separation:

| Question | Similarity score range |
|---|---|
| In-scope (FAIR principles) | 0.395 – 0.529 |
| Out-of-scope (OCR software) | 0.208 – 0.236 |

A threshold of **0.30** sits comfortably in the gap between these ranges,
excluding irrelevant matches without discarding genuine ones.

### Technology stack

- **Orchestration:** LlamaIndex
- **Vector store:** ChromaDB (persistent, local) for the Reference Library;
  in-memory `VectorStoreIndex` for the Corpus
- **Embeddings:** HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (runs
  locally, no API key)
- **Language model:** `gpt-oss:20b`, served fully locally via
  [Ollama](https://ollama.com)
- **Interface:** Streamlit

Because both the embedding model and the language model run locally, APEX needs
no API key and no internet connection once the model has been downloaded. Nothing
about a user's conversation or uploaded documents is sent to an external server.

## The curated Reference Library

The Reference Library is intentionally small and hand-curated. Every source is
openly licensed, allowing it to be redistributed with the project. The sources
are organised into the four project phases:

### Foundation

1. **Wilkinson et al. (2016)** — *The FAIR Guiding Principles for scientific data
   management and stewardship.* Scientific Data. — CC BY 4.0
2. **Tayler, Mitchell, Ripp & Dangoisse (2022)** — *Data Primer.* eCampusOntario
   Pressbooks. — CC BY 4.0

### Ascent (Analysis)

3. **Underwood (2017)** — *A Genealogy of Distant Reading.* Digital Humanities
   Quarterly. — CC BY-ND 4.0
4. **Clement (2016)** — *Where Is Methodology in Digital Humanities?* Debates in
   the Digital Humanities 2016. — CC BY-NC-ND 4.0
5. **Perkins & Roe (2024)** — *The Use of Generative AI Tools in Academic
   Research.* arXiv:2408.06872. — CC BY-SA
6. **De Sá Pereira (2019)** — *Mixed Methodological Digital Humanities.* Debates
   in the Digital Humanities 2019. — CC BY-NC-ND

### Checkpoint (Human-in-the-loop)

7. **Guingrich, Mehta & Bhatt (2026)** — *Belief Offloading in Human-AI
   Interaction.* arXiv:2602.08754. — CC BY
8. **Kalai, Nachum, Vempala & Zhang (2025)** — *Why Language Models Hallucinate.*
   arXiv:2509.04664. — CC BY
9. **Simons, Zichert & Wüthrich (2025)** — *Large Language Models for History,
   Philosophy, and Sociology of Science.* arXiv:2506.12242. — CC BY

### Summit (Communication)

10. **Sanz-Tejeda et al. (2025)** — *The Impact of Generative AI on Academic
    Reading and Writing.* Frontiers in Education.
    DOI: 10.3389/feduc.2025.1711718. — CC BY
11. **Zhang, Reynolds, Lugmayr, Damjanov & Hassan (2022)** — *A Visual Data
    Storytelling Framework.* Informatics 9(4):73.
    DOI: 10.3390/informatics9040073. — CC BY

## Setup

APEX runs entirely on a local machine. The steps below assume macOS with a
recent Apple-silicon chip and at least 24 GB of RAM, which comfortably runs the
`gpt-oss:20b` model.

### 1. Install Ollama and download the model

Download and install Ollama from [ollama.com/download](https://ollama.com/download),
then pull the model:

```bash
ollama pull gpt-oss:20b
```

### 2. Set up the Python environment

```bash
cd apex-dh-research-assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Build the Reference Library (first run only)

The first launch reads the 11 PDFs in `data/` and builds the persistent vector
database. This happens automatically, but it can also be triggered directly:

```bash
python rag_backend.py
```

From then on, the database is loaded rather than rebuilt.

### 4. Launch the app

```bash
streamlit run app.py
```

No API key and no `.env` file are required.

## Usage

- **Ask a question or describe a task.** The single compose box accepts both
  ("What are the FAIR principles?" or "Help me set up a corpus analysis").
- **Upload your own documents** in the sidebar to create a Corpus. Supported
  formats include PDF, Word, Excel, CSV, plain text, Markdown, XML/TEI,
  PowerPoint, and EPUB.
- **Read the sources.** Each answer lists the sources it consulted, labelled as
  either *Reference Library* or *Corpus*.
- **Continue with suggested next steps.** After each answer, APEX proposes
  concrete follow-up actions; selecting one continues the same conversation.
- **Save and resume.** Conversations can be explicitly saved to a file and
  reloaded later. Nothing is saved automatically.

## Project structure

```
apex-dh-research-assistant/
├── app.py                 # Streamlit interface
├── answer_engine.py       # Core retrieval + prompting logic
├── rag_backend.py         # Builds/loads the Reference Library (ChromaDB)
├── db_b.py                # Builds the temporary Corpus from uploads
├── design.py              # Shared visual design system (CSS, marks)
├── check_database.py      # Diagnostic: reports what is stored in the DB
├── inspect_chunks.py      # Diagnostic: prints raw chunk text
├── check_relevance.py     # Diagnostic: prints similarity scores per chunk
├── apex_favicon.png       # Application icon
├── requirements.txt       # Python dependencies
├── data/                  # The 11 curated PDFs (Reference Library)
└── README.md              # This file
```

The three diagnostic scripts (`check_database.py`, `inspect_chunks.py`,
`check_relevance.py`) are not required to run the application. They are retained
because they document the verification and calibration process behind the system.

## Evaluation

APEX is evaluated along four dimensions that map directly onto its design goals,
rather than on raw accuracy alone — because its core promise is transparency
about the *source* of an answer, not only correctness:

| Dimension | What it measures |
|---|---|
| **Source grounding accuracy** | Does an in-scope question retrieve the correct source from the Reference Library? |
| **Fabrication rate** | Does the system invent locators (page/section numbers, DOIs, named frameworks) not present in the retrieved context? |
| **Transparency correctness** | For out-of-scope questions, does APEX explicitly flag that it is answering from general reasoning, rather than silently blending it in? |
| **Operational robustness** | Does the system complete a response reliably, without silent truncation or unhandled crashes? |

### Scenario matrix

Testing follows a 2×2 matrix — *Corpus present or absent* × *question answerable
from the Reference Library or not* — to confirm the system behaves transparently
in every combination.

| Scenario | Corpus | Question | Expected behaviour |
|---|---|---|---|
| **A** | absent | In-scope (FAIR principles) | Grounded answer from the Reference Library; no Corpus source |
| **B** | absent | Out-of-scope (OCR software) | Explicit "not covered" statement; no irrelevant sources cited |
| **C** | present | Spans both (distant reading applied to an uploaded document) | Both Reference Library and Corpus cited; methodology applied to the document |
| **D** | present | Out-of-scope (OCR software) | Explicit "not covered" statement, despite a Corpus being present |

### Key result: the relevance threshold

Early testing surfaced the most important structural finding. In scenarios B and
D, the retriever returned its top-*k* nearest chunks regardless of how weak the
match was, so an out-of-scope question still received "the least bad" results,
which were then misattributed as genuine sources. The behaviour was also
inconsistent between B and D — the presence of a Corpus alone could change whether
the transparency statement was triggered.

Similarity scores were measured directly (via `check_relevance.py`) to
distinguish real matches from incidental ones:

| Question | Similarity score range |
|---|---|
| In-scope (FAIR principles) | 0.395 – 0.529 |
| Out-of-scope (OCR software) | 0.208 – 0.236 |

The clear gap between these ranges motivated a fixed relevance threshold of
**0.30**, below which retrieved chunks are discarded. After this change,
out-of-scope questions no longer retrieve or cite irrelevant Reference Library
sources, and the transparency statement fires consistently whether or not a
Corpus is present.

### Fabrication spot-checks

Specific details cited by the system — for example a DOI and the term "SpokenWeb"
attributed to the Data Primer — were manually verified against the source
documents using `inspect_chunks.py` and confirmed genuine rather than fabricated.
These checks are logged as passed, not assumed. This is itself an instance of the
human-in-the-loop verification the tool is designed to promote.

## Development process

APEX was built in distinct stages, each resolving a specific design or technical
question before moving on.

1. **Source curation.** The Reference Library was assembled first. Candidate DH
   methodology sources were evaluated for relevance and, crucially, for licensing:
   only openly licensed works that could be redistributed with the project were
   retained. Paywalled candidates were replaced with open equivalents. The final
   eleven sources were organised into the four project phases.

2. **Reference Library RAG.** The curated PDFs were embedded and stored in a
   persistent local vector database. Retrieval quality was verified directly
   against the stored chunks rather than assumed.

3. **Corpus upload.** A second, temporary retrieval source was added so users can
   bring their own documents. This was kept in memory rather than persisted, so
   uploaded material never touches disk and disappears when the session ends.

4. **Answer engine and prompting.** The core logic that combines both sources was
   developed here, including the anti-fabrication rule, the transparency
   behaviour for out-of-scope questions, and the reprioritisation that keeps
   answers grounded in retrieved sources rather than generic principles.

5. **Interface and interaction design.** A conversational Streamlit interface was
   built around the engine, with automatic next-step suggestions, explicit
   save/resume, and a consistent visual identity.

6. **Evaluation and iteration.** The system was tested against the scenario matrix
   above, and the relevance threshold was introduced in direct response to the
   findings.

### Iteration log

The following technical issues were identified and resolved during development.
They are recorded here because the debugging process is itself part of the
project's methodology.

| Issue | Diagnosis | Resolution |
|---|---|---|
| Retrieved chunks contained raw PDF binary rather than text | A required file-reader package was missing, so PDFs were silently read as raw bytes | Installed the correct reader, rebuilt the index, and verified clean extraction against the stored chunks |
| Answers were empty or truncated on longer prompts | The reasoning model's hidden "thinking" tokens consumed the response budget before the visible answer | Tuned the reasoning effort and per-call token budgets so the visible answer completes |
| Out-of-scope questions cited irrelevant sources | The retriever always returned its top-*k* chunks regardless of match strength | Introduced an empirically calibrated relevance threshold (0.30) |
| Apparent over-precise citations (invented section numbers) | The prompt allowed the model to blend fabricated locators with real ones | Added an explicit anti-fabrication rule forbidding invented page/section/DOI details unless present verbatim in the retrieved context |
| Near-identical answers regardless of the question | Detailed core principles dominated every prompt, overshadowing the retrieved sources | Shortened the core principles to light background and reprioritised the prompt so retrieved content leads |

### From cloud API to local inference

An earlier iteration used a hosted inference API. This was replaced with fully
local inference via Ollama after the hosted model was deprecated and free-tier
usage limits repeatedly interrupted testing. The migration removed all external
dependencies, usage limits, and API keys, and it strengthened the project's data
stewardship: no user data leaves the local machine. This shift is itself a useful
illustration of how external infrastructure constraints can shape the
architecture of a RAG system, not just its cost.



APEX is built around the same literature it draws on, and several of its design
decisions are direct responses to that literature:

- **Hallucination.** Kalai et al. (2025) explain why language models produce
  confident, incorrect output. APEX mitigates this with an explicit
  anti-fabrication instruction (never invent page numbers, section numbers,
  DOIs, or named frameworks that do not appear verbatim in the retrieved
  context) and with the relevance threshold that prevents weak matches from being
  presented as genuine sources. These are mitigations, not guarantees — see
  *Known limitations*.
- **Belief offloading.** Guingrich et al. (2026) describe how users can offload
  belief formation onto an AI system, eroding their own critical judgement. APEX
  responds to this at the level of interaction design: it proposes options and
  next steps rather than issuing conclusions, and it labels the provenance of
  every answer so the user can judge how much to trust it.
- **Data stewardship and licensing.** The FAIR principles (Wilkinson et al.,
  2016) and the Data Primer (Tayler et al., 2022) inform both the tool's advice
  and its own construction: every source in the Reference Library is openly
  licensed and can be redistributed with the project, and no user data leaves the
  local machine.

## Known limitations

These limitations are documented deliberately, in the spirit of the transparency
the tool is built to promote:

- **Prompt-based rules are not hard guarantees.** The anti-fabrication and
  transparency instructions are followed reliably in most cases but not with
  absolute certainty, which is an inherent property of prompt-based control over
  language models.
- **Combined-concept retrieval.** Questions that contrast two concepts (for
  example, close reading versus distant reading) tend to favour whichever single
  document already discusses both terms together, rather than combining two
  separate sources.
- **English-optimised embeddings.** The embedding model is optimised for English.
  All eleven curated sources are in English, so the Reference Library is
  unaffected, but non-English Corpus uploads may retrieve less precisely.
- **Empirically tuned threshold.** The relevance threshold is calibrated to this
  specific corpus and embedding model; a different corpus would require
  recalibration.
- **Local performance trade-off.** Running the model locally removes all usage
  limits and keeps data private, but responses are slower than they would be on
  dedicated cloud inference hardware.

## Licensing

All eleven sources in the Reference Library are distributed under open Creative
Commons licenses (CC BY, CC BY-SA, CC BY-ND, CC BY-NC-ND, as listed above),
permitting their inclusion in this repository. Users retain full ownership of any
material they upload as a Corpus; such material is processed only in memory and
is never transmitted off the local machine.
