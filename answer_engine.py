"""
APEX - Answer Engine

Combines two layers of knowledge to answer a question, in this priority:
1. The Reference Library (retrieved): specific methodological deep-dives.
   When it's genuinely relevant, the answer is grounded in it directly.
2. The Corpus (retrieved, if the user has uploaded material): the user's
   own project content, which the relevant methodology is applied to.

A short set of core Digital Humanities principles is kept as light
background awareness rather than a leading frame, so specific answers stay
grounded in the curated sources instead of defaulting to generic advice.
When neither the Reference Library nor the Corpus covers a question, APEX
says so explicitly before falling back to general reasoning.

Includes safe_complete(), which wraps every language model call so an
error (e.g. a rate limit or a temporary failure) shows a calm, readable
message instead of crashing the app with a raw traceback, and
suggest_next_steps(), which proposes concrete next actions in the project
after each answer using only a short summary of the most recent turn, so
token usage per turn stays roughly constant even in a long conversation.
"""

from llama_index.core import Settings


CORE_PRINCIPLES = """
- Good data stewardship (e.g. FAIR principles) underpins any DH project.
- Match the analysis method to the question rather than defaulting to one approach.
- Use AI critically: verify outputs, and watch for over-reliance (hallucination, belief offloading).
- Keep the human in control of decisions, and communicate findings clearly.
"""

ANTI_FABRICATION_RULE = """
0. NEVER invent specific locators - section numbers (e.g. "3.2"), page numbers,
   DOIs, named frameworks, or named projects/models - unless that exact detail
   appears verbatim in the context provided below. If unsure, refer to a source
   only in general terms instead of inventing a precise locator.
"""


def safe_complete(prompt, max_tokens):
    """
    Calls the language model and returns clean text. If the call fails
    (for example, a temporary connection issue with the local model
    server) or produces an empty response, this returns a calm,
    understandable message instead of letting a raw error crash the app.
    """
    try:
        response = Settings.llm.complete(prompt, num_predict=max_tokens)
        text = str(response).strip()
        if not text:
            return (
                "APEX didn't return a visible answer this time - this can happen "
                "when the model's response budget runs out. Try again, or phrase "
                "the request a bit more narrowly."
            )
        return text
    except Exception as e:
        message = str(e)
        if "rate_limit" in message.lower() or "429" in message or "quota" in message.lower():
            return (
                "APEX has hit a usage limit for now. Wait a bit and try again. "
                "(Technical detail: " + message[:200] + ")"
            )
        return "APEX ran into a technical error: " + message


RELEVANCE_THRESHOLD = 0.30


def _retrieve(index, question, top_k, label):
    """
    Retrieves chunks from an index and tags them with a label.

    Every retrieval call returns its top_k nearest chunks regardless of
    how weak the actual match is - a completely unrelated question still
    gets "the least bad" result from a small corpus. To avoid presenting
    these as genuine matches, chunks below RELEVANCE_THRESHOLD are
    discarded rather than treated as found content.
    """
    parts, sources = [], []
    if index is None:
        return parts, sources
    for node in index.as_retriever(similarity_top_k=top_k).retrieve(question):
        if node.score is not None and node.score < RELEVANCE_THRESHOLD:
            continue
        parts.append(node.text)
        sources.append((label, node.metadata.get("file_name", "unknown")))
    return parts, sources


def answer_question(question, index_a, index_b=None):
    """One-shot direct answer, combining core principles + A + B."""
    method_parts, sources_a = _retrieve(index_a, question, 5, "Reference Library")
    content_parts, sources_b = _retrieve(index_b, question, 5, "Corpus")
    sources = sources_a + sources_b

    method_context = "\n\n---\n\n".join(method_parts) if method_parts else "(no specific deep-dive found in the Reference Library)"
    content_context = "\n\n---\n\n".join(content_parts) if content_parts else "(no project documents uploaded yet)"

    prompt = f"""You are APEX, an assistant for Digital Humanities students, helping
with their projects at any stage, on any topic.

Follow these rules, in order:
{ANTI_FABRICATION_RULE}
1. If the REFERENCE LIBRARY context below is genuinely relevant to the question,
   ground your answer specifically in it. Use what it actually says - do not pad
   the answer with generic principles it doesn't mention.
2. If CORPUS content is available, apply the relevant methodology (from the
   Reference Library if step 1 found something, otherwise general reasoning)
   directly and concretely to that material.
3. If the REFERENCE LIBRARY genuinely does not cover this question, say so
   explicitly ("this isn't covered by APEX's curated library -") before
   answering from general knowledge. Use only as much general knowledge as
   needed for a complete answer - do not over-explain generic concepts that
   the retrieved content already covers specifically.
4. Match the depth of your answer to what the question actually needs -
   this means avoiding unnecessary padding, NOT minimizing length for its
   own sake. A simple factual question still deserves a COMPLETE answer
   (e.g. explain briefly what each part of an acronym means, don't just
   decode the letters). A genuine comparison, multi-step process, or
   request for detail deserves fuller structure - such as a table
   contrasting two concepts - and should NOT be compressed into a single
   short paragraph just to save space.
5. Do NOT restate, repeat, or rephrase the question as a title or heading at
   the start of your answer - the user already sees their own question
   displayed above it. Begin directly with the substantive answer.

Keep this as light background awareness - do not lead every answer with it,
and do not recite it when the context above already gives a specific answer:
{CORE_PRINCIPLES}

REFERENCE LIBRARY:
{method_context}

CORPUS (the user's own project material, if any):
{content_context}

Question: {question}

Answer:"""

    answer_text = safe_complete(prompt, max_tokens=3000)
    return answer_text, sources


def propose_approaches(question, index_a):
    """Propose 2-3 different methodological approaches to a question."""
    method_parts, sources = _retrieve(index_a, question, 4, "Reference Library")
    method_context = "\n\n---\n\n".join(method_parts) if method_parts else "(no specific deep-dive found in the Reference Library)"

    prompt = f"""You are APEX, an assistant for Digital Humanities students.
A student has asked a question. Propose 2 to 3 genuinely DIFFERENT methodological
approaches they could take - grounded in the REFERENCE LIBRARY context below
where it's genuinely relevant. Do not answer the question yet.

Light background awareness, not something to lead with:
{CORE_PRINCIPLES}

Rules:
{ANTI_FABRICATION_RULE}
1. Propose exactly 2 or 3 approaches, each a meaningfully different angle.
2. Each approach: a 3-6 word label, then ONE sentence explaining it.
3. Separate each approach with a line containing exactly: ###
   No other text, numbering, or preamble.

REFERENCE LIBRARY:
{method_context}

Question: {question}

Approaches:"""

    raw_text = safe_complete(prompt, max_tokens=500)
    approaches = [a.strip() for a in raw_text.split("###") if a.strip()]
    if not approaches:
        approaches = [raw_text]
    return approaches, sources


def apply_approach(question, chosen_approach, index_a, index_b=None):
    """Answer in depth, applying a specific chosen approach to the user's content."""
    method_parts, sources_a = _retrieve(index_a, question, 5, "Reference Library")
    content_parts, sources_b = _retrieve(index_b, question, 5, "Corpus")
    sources = sources_a + sources_b

    method_context = "\n\n---\n\n".join(method_parts) if method_parts else "(no specific deep-dive found in the Reference Library)"
    content_context = "\n\n---\n\n".join(content_parts) if content_parts else "(no project documents uploaded yet)"

    prompt = f"""You are APEX, an assistant for Digital Humanities students.

The student chose (or wrote) this approach: {chosen_approach}

Follow these rules, in order:
{ANTI_FABRICATION_RULE}
1. If the REFERENCE LIBRARY context below is genuinely relevant, ground the
   answer specifically in it while applying the chosen approach above.
2. If CORPUS content is available, apply the chosen approach directly and
   concretely to that material.
3. If the REFERENCE LIBRARY genuinely does not cover this, say so explicitly
   ("this isn't covered by APEX's curated library -") before answering from
   general knowledge, using only as much as needed.
4. Match the depth of your answer to what the question actually needs - this
   means avoiding unnecessary padding, NOT minimizing length for its own
   sake. A genuine comparison or request for detail deserves fuller
   structure (e.g. a table), not a compressed one-paragraph summary.

Keep this as light background awareness, not something to lead with:
{CORE_PRINCIPLES}

REFERENCE LIBRARY:
{method_context}

CORPUS (the user's own project material, if any):
{content_context}

Question: {question}

Answer (applying the chosen approach):"""

    answer_text = safe_complete(prompt, max_tokens=3000)
    return answer_text, sources


def suggest_next_steps(last_question, last_answer, index_a):
    """
    Proposes 2-3 concrete NEXT STEPS in the project - not alternative ways
    to answer the same question, but sensible things to do now that the
    student has this answer.

    Only uses a short summary of the LAST turn (not the whole conversation),
    so token usage stays roughly constant no matter how long the chat gets.
    """
    last_answer_summary = last_answer[:600]  # keep this bounded and cheap

    method_parts, sources = _retrieve(index_a, last_question, 3, "Reference Library")
    method_context = "\n\n---\n\n".join(method_parts) if method_parts else "(no specific deep-dive found)"

    prompt = f"""You are APEX, a companion that supports Digital Humanities students
through an ongoing project conversation.

The student just asked: {last_question}
APEX answered (summary): {last_answer_summary}

Propose 2 to 3 concrete NEXT STEPS the student could take now in their project -
not alternative ways to answer the same question, but sensible things to do next
(e.g. "Draft a data management plan", "Pick a pilot sample to test your method",
"Turn this into a research question you can test"). Ground these in the
REFERENCE LIBRARY context below if it's genuinely relevant.

Light background awareness, not something to lead with:
{CORE_PRINCIPLES}

Rules:
{ANTI_FABRICATION_RULE}
1. Each next step: a 3-6 word action label, then ONE short sentence explaining it.
2. Separate each with a line containing exactly: ###
   No other text, numbering, or preamble.

METHODOLOGY (Reference Library):
{method_context}

Next steps:"""

    raw_text = safe_complete(prompt, max_tokens=700)
    next_steps = [s.strip() for s in raw_text.split("###") if s.strip()]
    if not next_steps:
        next_steps = []
    return next_steps, sources
