CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
.stApp { background-color: #f8fafc; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
.main-header { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 2.5rem 2rem; border-radius: 16px; margin-bottom: 2rem; color: white; text-align: center; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.2); position: relative; overflow: hidden; }
.main-header h1 { margin: 0; font-size: 2.2rem; font-weight: 800; letter-spacing: -0.5px; }
.main-header p { margin: 0.5rem 0 0; opacity: 0.8; font-size: 1rem; }
section[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
.stTextInput>div>div>input, .stNumberInput>div>div>input, div[data-baseweb="select"] { border-radius: 8px !important; border: 1px solid #cbd5e1 !important; }
div.stButton > button:first-child { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; border: none; border-radius: 8px; padding: 0.6rem 2rem; font-weight: 600; box-shadow: 0 4px 6px -1px rgba(37,99,235,0.3); transition: all 0.3s; width: 100%; }
div.stButton > button:first-child:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(37,99,235,0.4); }
section[data-testid="stFileUploader"] { border-radius: 12px; border: 2px dashed #94a3b8; background-color: #f8fafc; padding: 1.5rem; }
.result-card { background: white; border-radius: 12px; padding: 1.5rem; color: #1e293b; text-align: center; margin-bottom: 1rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; transition: transform 0.2s, box-shadow 0.2s; }
.result-card:hover { transform: translateY(-4px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
.result-card .label { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; color: #64748b; margin-bottom: 0.5rem; font-weight: 700; }
.result-card .value { font-size: 1.8rem; font-weight: 800; color: #0f172a; }
.result-card-green { background: linear-gradient(135deg, #f0fdf4, #dcfce7); border-color: #bbf7d0; }
.result-card-green .value { color: #166534; }
.result-card-orange { background: linear-gradient(135deg, #fff7ed, #ffedd5); border-color: #fed7aa; }
.result-card-orange .value { color: #9a3412; }
.result-card-blue { background: linear-gradient(135deg, #eff6ff, #dbeafe); border-color: #bfdbfe; }
.result-card-blue .value { color: #1e40af; }
.section-title { font-size: 1.3rem; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px; margin: 2rem 0 1.5rem; }
.section-title::before { content: ''; display: block; width: 5px; height: 24px; background-color: #2563eb; border-radius: 4px; }
.custom-divider { border: none; height: 1px; background: linear-gradient(90deg, transparent, #cbd5e1, transparent); margin: 2rem 0; }
.info-box { background: #eff6ff; border-left: 4px solid #2563eb; padding: 1rem 1.2rem; border-radius: 0 8px 8px 0; margin: 1rem 0; font-size: 0.95rem; color: #1e3a8a; }
.item-header { background: linear-gradient(135deg, #1e40af, #1e3a8a); color: white; padding: 0.8rem 1.2rem; border-radius: 10px 10px 0 0; font-weight: 700; font-size: 1rem; }
.item-body { background: white; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 10px 10px; padding: 1rem; margin-bottom: 1rem; }
</style>
"""
