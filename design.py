"""
APEX - Shared design system (colors, type, custom CSS)

Imported by app.py so the whole interface uses consistent colors,
typography, and spacing.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

:root {
    --apex-bg: var(--background-color, #F5F6F7);
    --apex-surface: var(--secondary-background-color, #FFFFFF);
    --apex-ink: var(--text-color, #1B1E23);
    --apex-accent: #2C6E63;
    --apex-muted: color-mix(in srgb, var(--apex-ink) 55%, var(--apex-bg) 45%);
    --apex-accent-soft: color-mix(in srgb, var(--apex-accent) 15%, var(--apex-bg) 85%);
    --apex-border: color-mix(in srgb, var(--apex-ink) 18%, var(--apex-bg) 82%);
}

.stApp {
    background-color: var(--apex-bg);
    font-family: 'IBM Plex Sans', sans-serif;
    color: var(--apex-ink);
}

.block-container {
    max-width: 760px;
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}

h1 {
    font-family: 'Lora', serif;
    font-weight: 600;
    letter-spacing: -0.01em;
    margin-bottom: 0.1rem;
}

h3, h4 {
    font-family: 'Lora', serif;
    font-weight: 500;
    font-size: 22px;
}

[data-testid="stCaptionContainer"] {
    color: var(--apex-muted);
    font-family: 'IBM Plex Sans', sans-serif;
    font-weight: 600;
    font-size: 16px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 0 !important;
}

.apex-divider {
    height: 2px;
    width: 100%;
    margin: 1.1rem 0 1.6rem 0;
    background: linear-gradient(90deg, var(--apex-ink) 0%, var(--apex-accent) 100%);
    border: none;
    border-radius: 2px;
    opacity: 0.85;
}

p, li { line-height: 1.55; font-size: 15px; }

div[data-testid="stTextInput"] input {
    background-color: var(--apex-surface);
    border: 1px solid var(--apex-border);
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    font-family: 'IBM Plex Sans', sans-serif;
}
div[data-testid="stTextInput"] input:focus {
    border-color: var(--apex-accent);
    box-shadow: 0 0 0 1px var(--apex-accent);
}

.stButton > button {
    background-color: var(--apex-surface);
    color: var(--apex-ink);
    border: 1px solid var(--apex-border);
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-family: 'IBM Plex Sans', sans-serif;
    font-weight: 500;
    transition: all 0.15s ease;
}

/* Safety net: several native Streamlit widgets (checkboxes, file uploader,
   sidebar headers, labels) set their own font-family with higher specificity
   than a simple inherited rule on .stApp, silently falling back to
   Streamlit's own default UI font. This makes sure everything that isn't
   a heading uses IBM Plex Sans, per the two-typeface brand system. */
.stCheckbox label, .stFileUploader label, .stFileUploader small,
.stFileUploader button, section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3,
label, .stMarkdown p, .stMarkdown li, .stAlert, details summary {
    font-family: 'IBM Plex Sans', sans-serif !important;
}
.stButton > button:hover {
    background-color: var(--apex-accent-soft);
    border-color: var(--apex-accent);
    color: var(--apex-accent);
}

div[data-testid="column"]:first-child .stButton > button {
    background-color: var(--apex-ink);
    color: var(--apex-surface);
    border-color: var(--apex-ink);
}
div[data-testid="column"]:first-child .stButton > button:hover {
    background-color: var(--apex-accent);
    border-color: var(--apex-accent);
}

section[data-testid="stSidebar"] {
    background-color: var(--apex-surface);
    border-right: 1px solid var(--apex-border);
}

details {
    border: 1px solid var(--apex-border) !important;
    border-radius: 8px !important;
    background-color: var(--apex-surface);
}

.apex-source {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 13px;
    color: var(--apex-muted);
    margin: 0.1rem 0;
}
.apex-source b { color: var(--apex-ink); font-weight: 600; }

.apex-turn-question {
    font-family: 'Lora', serif;
    font-weight: 600;
    font-size: 1.05rem;
    margin-top: 1.6rem;
    color: var(--apex-ink);
}

.apex-turn-divider {
    border: none;
    border-top: 1px solid var(--apex-border);
    margin: 1.8rem 0;
}

footer {visibility: hidden;}
</style>
"""

# --- Official brand marks (from the APEX Brand Styleguide v1.0) ---

# Primary mark: ink-on-light. Use in the header on the app's light background.
VERTEX_MARK_PRIMARY = """
<svg width="42" height="42" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;">
  <path d="M50 8 L88 90 L70 90 L50 48 L30 90 L12 90 Z" fill="#1B1E23"></path>
  <rect x="30" y="60" width="40" height="12" rx="6" fill="#2C6E63"></rect>
  <circle cx="50" cy="10" r="9" fill="#2C6E63"></circle>
</svg>
"""

# Reversed mark: light-on-dark. For use on Ink or teal-accent backgrounds
# (e.g. a dark section divider) - not currently used on the light app
# background, kept available for that case.
VERTEX_MARK_REVERSED = """
<svg width="42" height="42" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;">
  <path d="M50 8 L88 90 L70 90 L50 48 L30 90 L12 90 Z" fill="#F5F6F7"></path>
  <rect x="30" y="60" width="40" height="12" rx="6" fill="#CFE3E0"></rect>
  <circle cx="50" cy="10" r="9" fill="#CFE3E0"></circle>
</svg>
"""

# App-icon tiles (mark + rounded square background) - used to generate the
# browser favicon (see apex_favicon.png). Kept here too in case an in-app
# badge/tile treatment is useful later.
TILE_SOFT = """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <rect width="100" height="100" rx="22" fill="#E3EEEC"></rect>
  <path d="M50 22 L76 78 L62 78 L50 54 L38 78 L24 78 Z" fill="#1B1E23"></path>
  <rect x="38" y="63" width="24" height="8" rx="4" fill="#2C6E63"></rect>
  <circle cx="50" cy="23" r="6" fill="#2C6E63"></circle>
</svg>
"""

TILE_INK = """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <rect width="100" height="100" rx="22" fill="#1B1E23"></rect>
  <path d="M50 22 L76 78 L62 78 L50 54 L38 78 L24 78 Z" fill="#F5F6F7"></path>
  <rect x="38" y="63" width="24" height="8" rx="4" fill="#CFE3E0"></rect>
  <circle cx="50" cy="23" r="6" fill="#CFE3E0"></circle>
</svg>
"""

# Kept as an alias so existing imports (LOGO_ICON_SVG) keep working -
# points to the current official header mark.
LOGO_ICON_SVG = VERTEX_MARK_PRIMARY

# A larger version of the primary mark, used in the empty-state hero
# (centered, with a soft glow behind it) rather than the small header.
VERTEX_MARK_HERO = """
<svg width="88" height="88" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" style="position:relative;">
  <path d="M50 8 L88 90 L70 90 L50 48 L30 90 L12 90 Z" fill="#1B1E23"></path>
  <rect x="30" y="60" width="40" height="12" rx="6" fill="#2C6E63"></rect>
  <circle cx="50" cy="10" r="9" fill="#2C6E63"></circle>
</svg>
"""
