CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700;900&display=swap');

/* Apply font to all elements */
html, body, [class*="css"], .stApp {
    font-family: 'Space Grotesk', sans-serif !important;
}

/* Force black text on light backgrounds */
p, label, li, h2, h3, h4, h5, h6, [data-testid="stWidgetLabel"] p, .stWidgetLabel, .stMarkdown p {
    color: #000000 !important;
}

/* White text on dark elements */
div.stButton > button:first-child,
div.stFormSubmitButton > button:first-child,
div.stButton > button:first-child *,
.stTabs [aria-selected="true"],
.stTabs [aria-selected="true"] * {
    color: #ffffff !important;
}

/* Inactive tabs text */
.stTabs [data-baseweb="tab"] {
    color: #000000 !important;
}

/* Dropdown popover menu styling (st.selectbox options) */
div[role="listbox"],
div[role="listbox"] ul,
div[role="listbox"] li,
div[data-baseweb="popover"],
div[data-baseweb="popover"] * {
    background-color: #ffffff !important;
    color: #000000 !important;
}
div[role="listbox"] li:hover,
div[role="listbox"] li[aria-selected="true"] {
    background-color: #FFD93D !important;
    color: #000000 !important;
}

/* Background - Creme with discrete grid typical of paper/notebook */
.stApp {
    background-color: #FFFDF5 !important;
    background-size: 30px 30px;
    background-image: linear-gradient(to right, rgba(0, 0, 0, 0.04) 1px, transparent 1px),
                      linear-gradient(to bottom, rgba(0, 0, 0, 0.04) 1px, transparent 1px) !important;
}

/* Hide Streamlit native menus */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Custom Header Card - Neobrutalist Bright Yellow Banner with heavy borders and offset shadow */
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
    color: #000000;
    font-size: 1.1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Sidebar styling overrides - Violet Neobrutalist Sidebar with thick right border */
section[data-testid="stSidebar"] {
    background-color: #C4B5FD !important;
    border-right: 4px solid #000000 !important;
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
section[data-testid="stSidebar"] div[data-testid="stExpander"] label {
    color: #000000 !important;
}
section[data-testid="stSidebar"] .stTextInput>div>div>input, 
section[data-testid="stSidebar"] .stNumberInput>div>div>input, 
section[data-testid="stSidebar"] .stSelectbox>div>div>div,
section[data-testid="stSidebar"] div[data-baseweb="select"] {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 4px solid #000000 !important;
    border-radius: 0px !important;
}

/* Form Inputs styling - Thick borders and flat yellow focus state */
.stTextInput>div>div>input, 
.stNumberInput>div>div>input, 
.stSelectbox>div>div>div,
div[data-baseweb="select"] {
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
div[data-baseweb="select"]:focus {
    border-color: #000000 !important;
    background-color: #FFD93D !important; /* Neobrutalist focus color */
    box-shadow: 4px 4px 0px 0px #000000 !important;
    outline: none !important;
}

/* Expanders styling */
div[data-testid="stExpander"] {
    background-color: #ffffff !important;
    border: 4px solid #000000 !important;
    border-radius: 0px !important;
    box-shadow: 6px 6px 0px 0px #000000 !important;
    margin-bottom: 1rem !important;
}

/* Forms styling */
div[data-testid="stForm"] {
    background-color: #ffffff !important;
    border-radius: 0px !important;
    border: 4px solid #000000 !important;
    padding: 1.5rem !important;
    box-shadow: 8px 8px 0px 0px #000000 !important;
}

/* Premium Buttons styling - Satisfying Mechanical Red Click Button */
div.stButton > button:first-child,
div.stFormSubmitButton > button:first-child {
    background: #FF6B6B !important; /* Bold Red */
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
div.stButton > button:first-child:hover,
div.stFormSubmitButton > button:first-child:hover {
    background: #ff5252 !important;
    transform: translate(-2px, -2px) !important;
    box-shadow: 6px 6px 0px 0px #000000 !important;
}
div.stButton > button:first-child:active,
div.stFormSubmitButton > button:first-child:active {
    transform: translate(4px, 4px) !important; /* Mechanical push down over its shadow */
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

/* Uploader box */
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

/* Neobrutalist Result Cards - Thick Black Outlines & Solid Offset Shadows */
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

/* Customized card variations - Bold Flat Pastels */
.result-card-green {
    background: #86EFAC !important; /* Pop green */
}
.result-card-green .value {
    color: #000000 !important;
}

.result-card-orange {
    background: #FFD93D !important; /* Pop yellow */
}
.result-card-orange .value {
    color: #000000 !important;
}

.result-card-blue {
    background: #93C5FD !important; /* Pop blue */
}
.result-card-blue .value {
    color: #000000 !important;
}

/* Titles and dividers */
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
    position: relative;
}

/* Tabs styling overrides */
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
.stTabs [data-baseweb="tab"]:hover {
    background-color: #FFD93D !important;
}
.stTabs [aria-selected="true"] {
    color: #ffffff !important;
    background-color: #FF6B6B !important;
    transform: translateY(-4px) !important;
    box-shadow: 4px 4px 0px 0px #000000 !important;
}
</style>
"""
