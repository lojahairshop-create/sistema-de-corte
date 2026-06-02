CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700;900&display=swap');

/* ============================================================
   GLOBAL THEME OVERRIDE — Force light mode everywhere
   ============================================================ */

/* Root and App level — Force light background and black text */
html, body, [class*="css"], .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[data-testid="stMainBlockContainer"],
main, header {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #000000 !important;
}

/* Force ALL text elements to black */
p, span, label, li, td, th, caption, summary,
h1, h2, h3, h4, h5, h6,
div, a,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
[data-testid="stWidgetLabel"],
.stWidgetLabel,
.stMarkdown p,
.stMarkdown span,
.stMarkdown li,
.stMarkdown div,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] li,
[data-testid="stText"],
[data-testid="stCaptionContainer"] {
    color: #000000 !important;
}

/* ============================================================
   DIALOG / MODAL — Force white background with black text
   ============================================================ */
div[data-testid="stModal"],
div[data-testid="stModal"] > div,
div[data-testid="stDialog"],
div[data-testid="stDialog"] > div,
div[role="dialog"],
div[role="dialog"] > div,
div[role="dialog"] [data-testid="stVerticalBlock"],
div[role="dialog"] [data-testid="stMarkdownContainer"],
div[role="dialog"] [data-testid="stWidgetLabel"],
[data-testid="stModal"] [data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stDialog"] [data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #ffffff !important;
    color: #000000 !important;
}

div[role="dialog"] p,
div[role="dialog"] span,
div[role="dialog"] label,
div[role="dialog"] h1,
div[role="dialog"] h2,
div[role="dialog"] h3,
div[role="dialog"] div,
div[role="dialog"] li,
div[role="dialog"] [data-testid="stWidgetLabel"] p,
div[role="dialog"] .stMarkdown p {
    color: #000000 !important;
}

/* Dialog inputs */
div[role="dialog"] .stTextInput>div>div>input,
div[role="dialog"] .stNumberInput>div>div>input,
div[role="dialog"] .stSelectbox>div>div>div,
div[role="dialog"] div[data-baseweb="select"],
div[role="dialog"] .stTextArea textarea {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 4px solid #000000 !important;
    border-radius: 0px !important;
}

/* Dialog radio buttons */
div[role="dialog"] [role="radiogroup"] label,
div[role="dialog"] [role="radiogroup"] label span,
div[role="dialog"] [role="radiogroup"] label p,
div[role="dialog"] [data-testid="stRadio"] label {
    color: #000000 !important;
}

/* Dialog close button (X) */
div[role="dialog"] button[aria-label="Close"],
div[role="dialog"] button[aria-label="Close"] svg {
    color: #000000 !important;
}

/* Dialog title */
div[role="dialog"] [data-testid="stDialogTitle"],
div[role="dialog"] h2 {
    color: #000000 !important;
}

/* ============================================================
   ALERTS / INFO / WARNING / ERROR / SUCCESS — Readable text
   ============================================================ */
div[data-testid="stAlert"],
div[role="alert"],
.stAlert,
[data-testid="stNotification"] {
    color: #000000 !important;
}

div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span,
div[data-testid="stAlert"] div,
div[role="alert"] p,
div[role="alert"] span,
div[role="alert"] div,
.stAlert p,
.stAlert span {
    color: #000000 !important;
}

/* ============================================================
   BACKGROUND — Creme with subtle grid pattern
   ============================================================ */
.stApp {
    background-color: #FFFDF5 !important;
    background-size: 30px 30px;
    background-image: linear-gradient(to right, rgba(0, 0, 0, 0.04) 1px, transparent 1px),
                      linear-gradient(to bottom, rgba(0, 0, 0, 0.04) 1px, transparent 1px) !important;
}

/* Hide Streamlit native menus */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* ============================================================
   HEADER CARD — Neobrutalist Yellow Banner
   ============================================================ */
.main-header {
    background: #FFD93D !important;
    padding: 2rem;
    border: 4px solid #000000 !important;
    border-radius: 0px !important;
    margin-bottom: 2.5rem;
    color: #000000 !important;
    text-align: center;
    box-shadow: 8px 8px 0px 0px #000000 !important;
    transform: rotate(-1.2deg);
}
.main-header h1 {
    margin: 0;
    font-size: 2.5rem;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: -0.02em;
    color: #000000 !important;
    -webkit-text-stroke: 1.5px #000000;
    text-shadow: 3px 3px 0px #ffffff;
}
.main-header p {
    margin: 0.6rem 0 0;
    color: #000000 !important;
    font-size: 1.1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ============================================================
   SIDEBAR — Violet Neobrutalist
   ============================================================ */
section[data-testid="stSidebar"] {
    background-color: #C4B5FD !important;
    border-right: 4px solid #000000 !important;
}
section[data-testid="stSidebar"] * {
    color: #000000 !important;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {
    color: #000000 !important;
    font-weight: 900 !important;
    text-transform: uppercase;
    letter-spacing: -0.01em;
}
section[data-testid="stSidebar"] label {
    color: #000000 !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    font-size: 0.9rem !important;
}
section[data-testid="stSidebar"] div[data-testid="stExpander"] {
    background-color: #ffffff !important;
    border: 4px solid #000000 !important;
    border-radius: 0px !important;
    box-shadow: 4px 4px 0px 0px #000000 !important;
}
section[data-testid="stSidebar"] div[data-testid="stExpander"] * {
    color: #000000 !important;
}
section[data-testid="stSidebar"] .stTextInput>div>div>input,
section[data-testid="stSidebar"] .stNumberInput>div>div>input,
section[data-testid="stSidebar"] .stSelectbox>div>div>div,
section[data-testid="stSidebar"] div[data-baseweb="select"],
section[data-testid="stSidebar"] .stTextArea textarea {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 4px solid #000000 !important;
    border-radius: 0px !important;
}

/* ============================================================
   FORM INPUTS — Thick borders, flat yellow focus
   ============================================================ */
.stTextInput>div>div>input,
.stNumberInput>div>div>input,
.stSelectbox>div>div>div,
div[data-baseweb="select"],
.stTextArea textarea {
    border-radius: 0px !important;
    border: 4px solid #000000 !important;
    background-color: #ffffff !important;
    color: #000000 !important;
    transition: none !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
}
.stTextInput>div>div>input:focus,
.stNumberInput>div>div>input:focus,
div[data-baseweb="select"]:focus,
.stTextArea textarea:focus {
    border-color: #000000 !important;
    background-color: #FFD93D !important;
    box-shadow: 4px 4px 0px 0px #000000 !important;
    outline: none !important;
    color: #000000 !important;
}

/* ============================================================
   DROPDOWN / POPOVER menus
   ============================================================ */
div[role="listbox"],
div[role="listbox"] ul,
div[role="listbox"] li,
div[data-baseweb="popover"],
div[data-baseweb="popover"] *,
div[data-baseweb="menu"],
div[data-baseweb="menu"] * {
    background-color: #ffffff !important;
    color: #000000 !important;
}
div[role="listbox"] li:hover,
div[role="listbox"] li[aria-selected="true"] {
    background-color: #FFD93D !important;
    color: #000000 !important;
}

/* ============================================================
   EXPANDERS
   ============================================================ */
div[data-testid="stExpander"] {
    background-color: #ffffff !important;
    border: 4px solid #000000 !important;
    border-radius: 0px !important;
    box-shadow: 6px 6px 0px 0px #000000 !important;
    margin-bottom: 1rem !important;
}
div[data-testid="stExpander"] * {
    color: #000000 !important;
}

/* ============================================================
   FORMS
   ============================================================ */
div[data-testid="stForm"] {
    background-color: #ffffff !important;
    border-radius: 0px !important;
    border: 4px solid #000000 !important;
    padding: 1.5rem !important;
    box-shadow: 8px 8px 0px 0px #000000 !important;
}

/* ============================================================
   BUTTONS — Mechanical Red
   ============================================================ */

/* White text ONLY on buttons */
div.stButton > button:first-child,
div.stFormSubmitButton > button:first-child {
    background: #FF6B6B !important;
    color: #ffffff !important;
    border: 4px solid #000000 !important;
    border-radius: 0px !important;
    padding: 0.75rem 1.8rem !important;
    font-weight: 900 !important;
    text-transform: uppercase !important;
    font-size: 1rem !important;
    box-shadow: 4px 4px 0px 0px #000000 !important;
    transition: transform 0.05s ease-out, box-shadow 0.05s ease-out !important;
    width: 100%;
}
div.stButton > button:first-child *,
div.stFormSubmitButton > button:first-child *,
div.stButton > button:first-child p,
div.stFormSubmitButton > button:first-child p,
div.stButton > button:first-child span,
div.stFormSubmitButton > button:first-child span {
    color: #ffffff !important;
}
div.stButton > button:first-child:hover,
div.stFormSubmitButton > button:first-child:hover {
    background: #ff5252 !important;
    transform: translate(-2px, -2px) !important;
    box-shadow: 6px 6px 0px 0px #000000 !important;
}
div.stButton > button:first-child:active,
div.stFormSubmitButton > button:first-child:active {
    transform: translate(4px, 4px) !important;
    box-shadow: 0px 0px 0px 0px #000000 !important;
}
div.stButton > button:first-child:disabled,
div.stFormSubmitButton > button:first-child:disabled {
    background: #e2e8f0 !important;
    color: #94a3b8 !important;
    border-color: #94a3b8 !important;
    box-shadow: none !important;
    cursor: not-allowed !important;
    transform: none !important;
}

/* Download buttons — same style */
div.stDownloadButton > button:first-child {
    background: #FF6B6B !important;
    color: #ffffff !important;
    border: 4px solid #000000 !important;
    border-radius: 0px !important;
    font-weight: 900 !important;
    text-transform: uppercase !important;
    box-shadow: 4px 4px 0px 0px #000000 !important;
}
div.stDownloadButton > button:first-child *,
div.stDownloadButton > button:first-child p,
div.stDownloadButton > button:first-child span {
    color: #ffffff !important;
}

/* ============================================================
   FILE UPLOADER
   ============================================================ */
section[data-testid="stFileUploader"] {
    border-radius: 0px !important;
    border: 4px dashed #000000 !important;
    background-color: #ffffff !important;
    padding: 1.5rem !important;
    box-shadow: 6px 6px 0px 0px #000000 !important;
}
section[data-testid="stFileUploader"]:hover {
    border-style: solid !important;
    background-color: #FFFDF5 !important;
}

/* ============================================================
   RESULT CARDS — Thick Outlines & Offset Shadows
   ============================================================ */
.result-card {
    background: #ffffff !important;
    border-radius: 0px !important;
    padding: 1.25rem !important;
    color: #000000 !important;
    text-align: center !important;
    margin-bottom: 1.2rem !important;
    box-shadow: 6px 6px 0px 0px #000000 !important;
    border: 4px solid #000000 !important;
    transition: transform 0.15s ease-out, box-shadow 0.15s ease-out !important;
}
.result-card:hover {
    transform: translate(-4px, -4px) !important;
    box-shadow: 10px 10px 0px 0px #000000 !important;
}
.result-card .label {
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    color: #000000 !important;
    margin-bottom: 0.5rem !important;
    font-weight: 900 !important;
}
.result-card .value {
    font-size: 1.8rem !important;
    font-weight: 900 !important;
    color: #000000 !important;
}

/* Card color variations */
.result-card-green { background: #86EFAC !important; }
.result-card-green .value, .result-card-green .label { color: #000000 !important; }

.result-card-orange { background: #FFD93D !important; }
.result-card-orange .value, .result-card-orange .label { color: #000000 !important; }

.result-card-blue { background: #93C5FD !important; }
.result-card-blue .value, .result-card-blue .label { color: #000000 !important; }

/* ============================================================
   SECTION TITLES & DIVIDERS
   ============================================================ */
.section-title {
    font-size: 1.5rem !important;
    font-weight: 900 !important;
    color: #000000 !important;
    text-transform: uppercase !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    margin: 2.5rem 0 1.5rem !important;
}
.section-title::before {
    content: '' !important;
    display: block !important;
    width: 8px !important;
    height: 28px !important;
    background: #FFD93D !important;
    border: 3px solid #000000 !important;
    border-radius: 0px !important;
}
.custom-divider {
    border: none;
    height: 4px;
    background: #000000;
    margin: 2.5rem 0;
}
.info-box {
    background: #ffffff;
    border: 4px solid #000000;
    padding: 1rem;
    border-radius: 0px;
    box-shadow: 4px 4px 0px 0px #000000;
    margin: 1.5rem 0;
    font-size: 1rem;
    font-weight: 700;
    color: #000000;
}

/* ============================================================
   TABS — Neobrutalist Folder Tabs
   ============================================================ */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background-color: transparent !important;
    padding: 0px !important;
    border-bottom: 4px solid #000000 !important;
    border-radius: 0px !important;
}
.stTabs [data-baseweb="tab"] {
    color: #000000 !important;
    font-weight: 900 !important;
    text-transform: uppercase !important;
    padding: 8px 16px !important;
    border-radius: 0px !important;
    border-top: 4px solid #000000 !important;
    border-left: 4px solid #000000 !important;
    border-right: 4px solid #000000 !important;
    background-color: #ffffff !important;
    margin-bottom: -4px !important;
    transition: transform 0.1s ease-out !important;
}
.stTabs [data-baseweb="tab"] * {
    color: #000000 !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background-color: #FFD93D !important;
}
.stTabs [aria-selected="true"] {
    color: #ffffff !important;
    background-color: #FF6B6B !important;
    transform: translateY(-4px) !important;
    box-shadow: 4px 4px 0px 0px #000000 !important;
}
.stTabs [aria-selected="true"] *,
.stTabs [aria-selected="true"] p,
.stTabs [aria-selected="true"] span {
    color: #ffffff !important;
}

/* ============================================================
   DATA EDITOR / DATAFRAME — Force white bg and black text
   ============================================================ */
[data-testid="stDataFrame"],
[data-testid="stDataEditor"],
[data-testid="stDataFrame"] *,
[data-testid="stDataEditor"] * {
    color: #000000 !important;
}

/* ============================================================
   MULTISELECT / TAGS
   ============================================================ */
div[data-baseweb="tag"] {
    background-color: #FFD93D !important;
    color: #000000 !important;
}
div[data-baseweb="tag"] * {
    color: #000000 !important;
}

/* ============================================================
   TOOLTIPS
   ============================================================ */
div[data-baseweb="tooltip"],
div[data-baseweb="tooltip"] * {
    background-color: #000000 !important;
    color: #ffffff !important;
}

/* ============================================================
   METRIC / NUMBER INPUT steppers
   ============================================================ */
.stNumberInput button {
    color: #000000 !important;
    background-color: #ffffff !important;
    border: 2px solid #000000 !important;
    border-radius: 0px !important;
}

/* ============================================================
   CHECKBOX / RADIO — Force black text
   ============================================================ */
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] label *,
[data-testid="stRadio"] label,
[data-testid="stRadio"] label *,
[role="radiogroup"] label,
[role="radiogroup"] label * {
    color: #000000 !important;
}

/* ============================================================
   SCROLLBAR (optional) — Subtle dark track
   ============================================================ */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #FFFDF5; }
::-webkit-scrollbar-thumb { background: #000000; border-radius: 0px; }

</style>
"""
