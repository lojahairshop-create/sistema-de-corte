CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Apply font to all elements */
html, body, [class*="css"], .stApp {
    font-family: 'Outfit', sans-serif !important;
}

/* Background */
.stApp {
    background-color: #f8fafc !important;
}

/* Hide Streamlit native menus */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Custom Header Card */
.main-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    padding: 2.2rem 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    color: white;
    text-align: center;
    box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15), 0 8px 10px -6px rgba(15, 23, 42, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.05);
}
.main-header h1 {
    margin: 0;
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.main-header p {
    margin: 0.6rem 0 0;
    color: #94a3b8;
    font-size: 1.05rem;
    font-weight: 500;
}

/* Sidebar styling overrides */
section[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {
    color: #0f172a !important;
    font-weight: 700 !important;
}

/* Form Inputs styling */
.stTextInput>div>div>input, 
.stNumberInput>div>div>input, 
.stSelectbox>div>div>div,
div[data-baseweb="select"] {
    border-radius: 8px !important;
    border: 1px solid #cbd5e1 !important;
    background-color: #ffffff !important;
    color: #0f172a !important;
    transition: all 0.2s ease-in-out !important;
    font-size: 0.95rem !important;
}
.stTextInput>div>div>input:focus, 
.stNumberInput>div>div>input:focus,
div[data-baseweb="select"]:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.12) !important;
}

/* Expanders styling */
div[data-testid="stExpander"] {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.02) !important;
    margin-bottom: 0.5rem !important;
}

/* Forms styling */
div[data-testid="stForm"] {
    background-color: #ffffff !important;
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important;
    padding: 1.5rem !important;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;
}

/* Premium Buttons styling */
div.stButton > button:first-child,
div.stFormSubmitButton > button:first-child {
    background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.8rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    box-shadow: 0 4px 10px -2px rgba(79, 70, 229, 0.3) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    width: 100%;
}
div.stButton > button:first-child:hover,
div.stFormSubmitButton > button:first-child:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 14px -2px rgba(79, 70, 229, 0.45) !important;
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
}
div.stButton > button:first-child:disabled,
div.stFormSubmitButton > button:first-child:disabled {
    background: #e2e8f0 !important;
    color: #94a3b8 !important;
    box-shadow: none !important;
    cursor: not-allowed !important;
    transform: none !important;
}

/* Uploader box */
section[data-testid="stFileUploader"] {
    border-radius: 12px !important;
    border: 2px dashed #cbd5e1 !important;
    background-color: #ffffff !important;
    padding: 1.5rem !important;
    transition: border-color 0.2s !important;
}
section[data-testid="stFileUploader"]:hover {
    border-color: #4f46e5 !important;
}

/* Stripe-style Result Cards */
.result-card {
    background: #ffffff !important;
    border-radius: 12px !important;
    padding: 1.25rem !important;
    color: #0f172a !important;
    text-align: center !important;
    margin-bottom: 1rem !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
    border: 1px solid #e2e8f0 !important;
    transition: all 0.2s ease-in-out !important;
}
.result-card:hover {
    transform: translateY(-2px) !important;
    border-color: #cbd5e1 !important;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.03) !important;
}
.result-card .label {
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    color: #64748b !important;
    margin-bottom: 0.4rem !important;
    font-weight: 700 !important;
}
.result-card .value {
    font-size: 1.8rem !important;
    font-weight: 800 !important;
    color: #0f172a !important;
}

/* Customized card variations */
.result-card-green {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%) !important;
    border-color: #bbf7d0 !important;
}
.result-card-green .value {
    color: #15803d !important;
}

.result-card-orange {
    background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%) !important;
    border-color: #fde68a !important;
}
.result-card-orange .value {
    color: #b45309 !important;
}

.result-card-blue {
    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%) !important;
    border-color: #bfdbfe !important;
}
.result-card-blue .value {
    color: #1d4ed8 !important;
}

/* Titles and dividers */
.section-title {
    font-size: 1.3rem !important;
    font-weight: 800 !important;
    color: #0f172a !important;
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    margin: 2rem 0 1.2rem !important;
}
.section-title::before {
    content: '' !important;
    display: block !important;
    width: 4px !important;
    height: 24px !important;
    background: linear-gradient(180deg, #4f46e5 0%, #4338ca 100%) !important;
    border-radius: 2px !important;
}
.custom-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #cbd5e1, transparent);
    margin: 2rem 0;
}
.info-box {
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
    padding: 0.8rem 1rem;
    border-radius: 0 8px 8px 0;
    margin: 1.2rem 0;
    font-size: 0.9rem;
    color: #1e3a8a;
}

/* Tabs styling overrides */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #f1f5f9 !important;
    padding: 4px 6px !important;
    border-radius: 10px !important;
    border: 1px solid #e2e8f0 !important;
}
.stTabs [data-baseweb="tab"] {
    color: #64748b !important;
    font-weight: 600 !important;
    padding: 6px 12px !important;
    border-radius: 6px !important;
    border: none !important;
    transition: all 0.2s !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #0f172a !important;
    background-color: #e2e8f0 !important;
}
.stTabs [aria-selected="true"] {
    color: #ffffff !important;
    background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
    box-shadow: 0 2px 8px rgba(79, 70, 229, 0.2) !important;
}
</style>
"""
