"""Travel-themed Streamlit CSS."""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Source+Sans+3:wght@400;500;600&display=swap');

.stApp {
  background:
    radial-gradient(1200px 500px at 10% -10%, #d7f0ef 0%, transparent 50%),
    radial-gradient(900px 400px at 100% 0%, #f3e2c8 0%, transparent 45%),
    #f7f3ec;
  color: #1f2a2e;
}
html, body, [class*="css"]  {
  font-family: "Source Sans 3", "Segoe UI", sans-serif;
}
h1, h2, h3, .hero-title {
  font-family: "Fraunces", Georgia, serif;
  color: #0f4c51;
}
.hero {
  background: linear-gradient(135deg, #0f6c73 0%, #1a8f86 58%, #c9783c 140%);
  color: #fff;
  padding: 1.4rem 1.6rem;
  border-radius: 18px;
  margin-bottom: 1rem;
  box-shadow: 0 10px 30px rgba(15, 76, 81, 0.18);
}
.hero p { color: #e8f6f5; margin-bottom: 0; }
.badge {
  display: inline-block;
  padding: 0.2rem 0.7rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.02em;
}
.badge-demo { background: #f4d7a6; color: #7a4b12; }
.badge-ai { background: #c9efe8; color: #0f4c51; }
.card {
  background: #fffdf8;
  border: 1px solid #eadfcf;
  border-radius: 16px;
  padding: 1rem 1.1rem;
  margin-bottom: 0.8rem;
}
.slot-cost { color: #0f6c73; font-weight: 700; }
.small-muted { color: #5c6b70; font-size: 0.9rem; }
div[data-testid="stSidebar"] {
  background: #12383c;
}
div[data-testid="stSidebar"] * {
  color: #edf6f5 !important;
}
div[data-testid="stSidebar"] .stSelectbox label, div[data-testid="stSidebar"] p {
  color: #d5eae8 !important;
}
.stButton>button {
  border-radius: 12px;
  font-weight: 600;
  border: 0;
}
</style>
"""
