from __future__ import annotations
import streamlit as st
from supabase import create_client, Client
import time
import uuid

# ==========================================
# 1. إعدادات الصفحة والتهيئة الأساسية
# ==========================================
st.set_page_config(
    page_title="مكتبة الهندسة الرقمية",
    page_icon=":material/local_library:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تهيئة حالة الوضع الداكن/الفاتح (تُحفظ في الجلسة الحالية)
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# لوحتا الألوان: فاتح (ورقي دافئ) وداكن (أرشيف ليلي)
THEMES = {
    "light": {
        "ink": "#1B1815", "ink_soft": "#6E6455", "ink_faint": "#A79C8A",
        "paper": "#F4EEE3", "paper_raised": "#FBF7EF", "line": "#DDD1BA",
    },
    "dark": {
        "ink": "#F2ECDD", "ink_soft": "#C9BEA8", "ink_faint": "#8B8071",
        "paper": "#17140F", "paper_raised": "#211D16", "line": "#3A342A",
    },
}
_active_theme = THEMES[st.session_state.theme]

# ------------------------------------------
# Design System: ألوان، خطوط، مسافات موحّدة
# فلسفة التصميم: هوية أكاديمية هادئة (Navy + Neutral)
# لون أساسي واحد (Navy) + محايدات + ألوان حالة فقط (نجاح/تحذير/خطأ)
# ------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ============================================================
   هوية "الأرشيف" — نظام تصميم أصلي مستوحى من فهارس المكتبات
   الورقية وسجلات الأرشيف الأكاديمي، بدل قوالب الـ SaaS الجاهزة.

   - عرض (Serif/Fraunces): للعناوين، بشخصية طباعية واضحة.
   - Inter: للواجهة والنصوص التشغيلية.
   - JetBrains Mono: للبيانات الوصفية (تواريخ، أرقام، وسوم حالة)
     بأسلوب "بطاقة الفهرسة".
   - لون واحد جريء (طوبي محروق) بدل الأزرق المؤسسي المعتاد.
   ============================================================ */

:root {
    --ink: __INK__;
    --ink-soft: __INK_SOFT__;
    --ink-faint: __INK_FAINT__;
    --paper: __PAPER__;
    --paper-raised: __PAPER_RAISED__;
    --line: __LINE__;
    --accent: #A8481F;
    --accent-hover: #8A3A18;
    --accent-soft: #EFDCC6;
    --on-accent: #FBF3E7;
    --success: #3E6A46;
    --success-bg: #E6EDDF;
    --warning: #8A6A1E;
    --warning-bg: #F3E9CE;
    --error: #A23628;
    --error-bg: #F3DFD5;
    /* ثابتة دائماً بغض النظر عن الوضع الداكن/الفاتح — عمود الأرشيف الجانبي */
    --sb-bg: #1B1815;
    --sb-text: #F4EEE3;
    --sb-text-faint: #A79C8A;
    --sb-line: rgba(244,238,227,0.18);
    --radius: 3px;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background-color: var(--paper);
}

#MainMenu, footer {visibility: hidden;}

/* خلفية بنسيج ورقي خفيف جداً بدل السطح المسطح المعتاد */
.stApp {
    background-image:
        radial-gradient(var(--line) 0.6px, transparent 0.6px);
    background-size: 22px 22px;
    background-position: -8px -8px;
}
.main .block-container {
    padding-top: 2.25rem;
    max-width: 1180px;
}

/* ===== رأس الصفحة: بطاقة فهرسة كبيرة ===== */
.page-header {
    padding: 0 0 1.75rem 0;
    margin-bottom: 2.25rem;
    border-bottom: 2px solid var(--ink);
    position: relative;
}
.page-header .eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'JetBrains Mono', monospace;
    color: var(--accent);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 0.85rem;
}
.page-header .eyebrow::before {
    content: "";
    display: inline-block;
    width: 22px;
    height: 1px;
    background: var(--accent);
}
.page-header h1 {
    font-family: 'Fraunces', serif;
    font-optical-sizing: auto;
    font-size: 2.6rem;
    font-weight: 600;
    line-height: 1.15;
    color: var(--ink);
    margin: 0 0 0.6rem 0;
    letter-spacing: -0.01em;
}
.page-header p {
    color: var(--ink-soft);
    font-size: 1rem;
    max-width: 46rem;
    margin: 0;
}

/* ===== قوائم موارد بأسلوب "بطاقة الفهرسة" — خطوط فاصلة بدل الصناديق ===== */
.archive-row {
    display: block;
    padding: 1.1rem 0;
    border-bottom: 1px solid var(--line);
    transition: padding-right 0.18s ease;
}
.archive-row:hover {
    padding-right: 0.4rem;
}
.archive-row .row-top {
    display: flex;
    align-items: baseline;
    gap: 0.6rem;
    margin-bottom: 0.3rem;
}
.archive-row .row-index {
    font-family: 'JetBrains Mono', monospace;
    color: var(--accent);
    font-size: 0.78rem;
    font-weight: 600;
}
.archive-row .item-title {
    font-family: 'Fraunces', serif;
    font-weight: 500;
    color: var(--ink);
    font-size: 1.08rem;
}
.archive-row .item-meta {
    font-family: 'JetBrains Mono', monospace;
    color: var(--ink-faint);
    font-size: 0.72rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-right: 1.4rem;
}

/* بديل مضغوط (للطلبات المعلقة داخل الإدارة) */
.content-card {
    background: var(--paper-raised);
    border: 1px solid var(--line);
    border-right: 3px solid var(--accent);
    border-radius: 2px;
    padding: 1rem 1.15rem;
    margin-bottom: 0.65rem;
}
.content-card .item-title {
    font-family: 'Fraunces', serif;
    font-weight: 500;
    color: var(--ink);
    font-size: 1.02rem;
    margin-bottom: 0.25rem;
}
.content-card .item-meta {
    font-family: 'JetBrains Mono', monospace;
    color: var(--ink-soft);
    font-size: 0.72rem;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

/* ===== وسوم حالة بأسلوب "ختم الأرشيف" بدل الشارات المدورة ===== */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.25rem 0.55rem;
    border: 1px solid currentColor;
    border-radius: 2px;
}
.status-pill.success { color: var(--success); background: var(--success-bg); }
.status-pill.warning { color: var(--warning); background: var(--warning-bg); }

/* ===== أزرار: مستطيلة، حروف متباعدة، بلا انحناءات مبالغ فيها ===== */
.stButton>button {
    width: 100%;
    border-radius: var(--radius);
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.82rem;
    letter-spacing: 0.03em;
    border: 1.5px solid var(--ink);
    padding: 0.55rem 1rem;
    transition: all 0.15s ease;
    background-color: transparent;
    color: var(--ink);
}
.stButton>button:hover {
    background-color: var(--ink);
    color: var(--paper) !important;
    border-color: var(--ink);
}
.stButton>button[kind="primary"] {
    background-color: var(--accent);
    border-color: var(--accent);
    color: var(--on-accent);
}
.stButton>button[kind="primary"]:hover {
    background-color: var(--accent-hover);
    border-color: var(--accent-hover);
    color: var(--on-accent) !important;
}
.stButton>button[kind="secondary"] {
    background-color: transparent !important;
    color: var(--ink) !important;
    border-color: var(--line) !important;
}
.stButton>button[kind="secondary"] p,
.stButton>button[kind="secondary"] span {
    color: inherit !important;
}
.stButton>button[kind="secondary"]:hover {
    color: var(--paper) !important;
    background-color: var(--ink) !important;
    border-color: var(--ink) !important;
}
div[data-testid="stLinkButton"] a {
    border-radius: var(--radius) !important;
    border: 1.5px solid var(--ink) !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em;
}

/* ===== حقول الإدخال: خط سفلي بدل الصندوق الكامل ===== */
.stTextInput input, .stTextArea textarea {
    border: none !important;
    border-bottom: 1.5px solid var(--line) !important;
    border-radius: 0 !important;
    background: transparent !important;
    padding-right: 0 !important;
    color: var(--ink) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-bottom-color: var(--accent) !important;
    box-shadow: none !important;
}
.stSelectbox div[data-baseweb="select"] {
    border-radius: var(--radius) !important;
    border-color: var(--line) !important;
}
label[data-testid="stWidgetLabel"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--ink-soft) !important;
}

/* ===== الشريط الجانبي: "عمود الأرشيف" الداكن، ثابت بغض النظر عن الوضع ===== */
section[data-testid="stSidebar"] {
    background-color: var(--sb-bg);
    border-right: none;
}
section[data-testid="stSidebar"] * {
    color: var(--sb-text);
}
.sidebar-brand {
    padding: 0.25rem 0 1.5rem 0;
    border-bottom: 1px solid var(--sb-line);
    margin-bottom: 1.25rem;
}
.sidebar-brand .brand-mark {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent-soft);
    margin-bottom: 0.6rem;
}
.sidebar-brand .brand-name {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 1.5rem;
    line-height: 1.2;
    color: var(--sb-text);
}
.sidebar-brand .brand-sub {
    font-size: 0.78rem;
    color: var(--sb-text-faint);
    margin-top: 0.4rem;
}
.sidebar-footnote {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.02em;
    line-height: 1.7;
    color: var(--sb-text-faint);
    padding: 0.9rem 0;
    border-top: 1px solid var(--sb-line);
    margin-top: 1.5rem;
}

/* أزرار التنقل — حدود واضحة دائمة لكل عنصر + تمييز إضافي عند التفعيل */
.nav-btn {
    margin-bottom: 0.55rem;
}
section[data-testid="stSidebar"] .stButton>button {
    text-align: right !important;
    background: rgba(244,238,227,0.02) !important;
    border: 1px solid var(--sb-line) !important;
    border-radius: var(--radius) !important;
    color: var(--sb-text-faint) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em;
    padding: 0.65rem 0.9rem !important;
    transition: all 0.15s ease;
}
section[data-testid="stSidebar"] .stButton>button:hover {
    color: var(--sb-text) !important;
    border-color: var(--sb-text-faint) !important;
    background: rgba(244,238,227,0.06) !important;
}
.nav-btn.active .stButton>button,
section[data-testid="stSidebar"] .nav-btn.active button {
    color: var(--sb-text) !important;
    border-color: var(--accent) !important;
    background: rgba(168,72,31,0.16) !important;
    font-weight: 600 !important;
    box-shadow: inset 3px 0 0 var(--accent);
}
/* فاصل خفيف بين خيارات التنقل وزر تبديل الوضع */
.sidebar-divider {
    height: 1px;
    background: var(--sb-line);
    margin: 0.9rem 0 0.9rem 0;
}

/* زر تبديل الوضع الداكن/الفاتح — دائري، يتوسط الشريط الجانبي، مختلف تماماً عن أزرار التنقل */
.theme-toggle {
    display: flex;
    justify-content: center;
    margin-top: 0.2rem;
}
.theme-toggle div[data-testid="stButton"] {
    width: auto !important;
}
.theme-toggle .stButton>button {
    width: 44px !important;
    height: 44px !important;
    min-width: 44px !important;
    border-radius: 50% !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: transparent !important;
    border: 1px dashed var(--sb-line) !important;
    color: var(--sb-text-faint) !important;
    box-shadow: none !important;
}
.theme-toggle .stButton>button:hover {
    color: var(--accent-soft) !important;
    border: 1px solid var(--accent-soft) !important;
    background: rgba(244,238,227,0.06) !important;
}

/* ===== سهم طي/فتح الشريط الجانبي — تثبيت لون واضح في الوضعين ===== */
/* السهم داخل الشريط الجانبي (عند فتحه) — فاتح دائماً لأن خلفية الشريط غامقة ثابتة */
section[data-testid="stSidebar"] [data-testid*="ollapse"] svg,
section[data-testid="stSidebar"] button[kind="header"] svg {
    color: var(--sb-text) !important;
    fill: var(--sb-text) !important;
}
/* السهم اللي يظهر فوق المحتوى الرئيسي عند طيّ الشريط — يتبع لون الوضع الحالي */
[data-testid="collapsedControl"] svg,
div[data-testid*="ollapsedControl"] svg,
header[data-testid="stHeader"] [data-testid*="ollapse"] svg {
    color: var(--ink) !important;
    fill: var(--ink) !important;
}
[data-testid="collapsedControl"],
div[data-testid*="ollapsedControl"] {
    background: var(--paper-raised) !important;
    border: 1px solid var(--line) !important;
    border-radius: var(--radius) !important;
}

/* فواصل */
hr {
    border-color: var(--line) !important;
}

/* ===== تبويبات (Tabs): أسلوب فهرس أفقي بخط تحت التبويب النشط ===== */
button[data-baseweb="tab"] {
    color: var(--ink-soft) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.01em;
}
button[data-baseweb="tab"] p {
    color: inherit !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--ink) !important;
    font-weight: 700 !important;
}
div[data-baseweb="tab-highlight"] {
    background-color: var(--accent) !important;
    height: 2.5px !important;
}
div[data-baseweb="tab-border"] {
    background-color: var(--line) !important;
}

/* ===== تثبيت الألوان العامة + العناوين الفرعية بالخط العريض ===== */
.stApp, .stApp p, .stApp label, .stApp span {
    color: var(--ink);
}
h2, h3, .stApp [data-testid="stMarkdownContainer"] h3 {
    font-family: 'Fraunces', serif !important;
    font-weight: 600 !important;
    color: var(--ink) !important;
}

/* رسائل النظام (نجاح/خطأ/تنبيه/معلومة) بحواف حادة بدل المدورة */
div[data-testid="stAlert"] {
    border-radius: 2px !important;
    border-width: 1px 1px 1px 3px !important;
    border-style: solid !important;
}

/* تبويب/تاب فورم — إزالة الظل الافتراضي عن العناصر */
div[data-testid="stForm"] {
    border: 1px solid var(--line) !important;
    border-radius: var(--radius) !important;
    background: var(--paper-raised) !important;
}
</style>
""".replace("__INK_SOFT__", _active_theme["ink_soft"]) \
   .replace("__INK_FAINT__", _active_theme["ink_faint"]) \
   .replace("__INK__", _active_theme["ink"]) \
   .replace("__PAPER_RAISED__", _active_theme["paper_raised"]) \
   .replace("__PAPER__", _active_theme["paper"]) \
   .replace("__LINE__", _active_theme["line"]), unsafe_allow_html=True)

# ==========================================
# 2. إعدادات الاتصال بقاعدة البيانات Supabase
# ==========================================
SUPABASE_URL = "https://oluniwydxvldqtgyfgne.supabase.co"
SUPABASE_KEY = "sb_publishable_1COvxRnhVYkxNxM7-jsIHQ_lXKlkueM"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# ==========================================
# 3. الهيكل الأكاديمي الموحد والثابت
# ==========================================
ACADEMIC_STRUCTURE = {
    "الهندسة الميكانيكية": {
        "السنة الأولى": ["السمستر الأول (Semester 1)", "السمستر الثاني (Semester 2)"],
        "السنة الثانية": ["السمستر الثالث (Semester 3)", "السمستر الرابع (Semester 4)"],
        "السنة الثالثة": ["السمستر الخامس (Semester 5)", "السمستر السادس (Semester 6)"],
        "السنة الرابعة": ["السمستر السابع (Semester 7)", "السمستر الثامن (Semester 8)"],
        "السنة الخامسة": ["السمستر التاسع (Semester 9)", "السمستر العاشر (Semester 10)"]
    },
    "الهندسة الكهربائية": {
        "السنة الأولى": ["السمستر الأول (Semester 1)", "السمستر الثاني (Semester 2)"],
        "السنة الثانية": ["السمستر الثالث (Semester 3)", "السمستر الرابع (Semester 4)"],
        "السنة الثالثة": ["السمستر الخامس (Semester 5)", "السمستر السادس (Semester 6)"],
        "السنة الرابعة": ["السمستر السابع (Semester 7)", "السمستر الثامن (Semester 8)"],
        "السنة الخامسة": ["السمستر التاسع (Semester 9)", "السمستر العاشر (Semester 10)"]
    },
    "الهندسة المدنية": {
        "السنة الأولى": ["السمستر الأول (Semester 1)", "السمستر الثاني (Semester 2)"],
        "السنة الثانية": ["السمستر الثالث (Semester 3)", "السمستر الرابع (Semester 4)"],
        "السنة الثالثة": ["السمستر الخامس (Semester 5)", "السمستر السادس (Semester 6)"],
        "السنة الرابعة": ["السمستر السابع (Semester 7)", "السمستر الثامن (Semester 8)"],
        "السنة الخامسة": ["السمستر التاسع (Semester 9)", "السمستر العاشر (Semester 10)"]
    },
    "الهندسة الزراعية": {
        "السنة الأولى": ["السمستر الأول (Semester 1)", "السمستر الثاني (Semester 2)"],
        "السنة الثانية": ["السمستر الثالث (Semester 3)", "السمستر الرابع (Semester 4)"],
        "السنة الثالثة": ["السمستر الخامس (Semester 5)", "السمستر السادس (Semester 6)"],
        "السنة الرابعة": ["السمستر السابع (Semester 7)", "السمستر الثامن (Semester 8)"],
        "السنة الخامسة": ["السمستر التاسع (Semester 9)", "السمستر العاشر (Semester 10)"]
    },
    "الهندسة المعمارية": {
        "السنة الأولى": ["السمستر الأول (Semester 1)", "السمستر الثاني (Semester 2)"],
        "السنة الثانية": ["السمستر الثالث (Semester 3)", "السمستر الرابع (Semester 4)"],
        "السنة الثالثة": ["السمستر الخامس (Semester 5)", "السمستر السادس (Semester 6)"],
        "السنة الرابعة": ["السمستر السابع (Semester 7)", "السمستر الثامن (Semester 8)"],
        "السنة الخامسة": ["السمستر التاسع (Semester 9)", "السمستر العاشر (Semester 10)"]
    }
}

def fetch_subjects_from_db(specialization: str, year: str, semester: str):
    """جلب المواد الدراسية ديناميكياً من قاعدة البيانات بناءً على الهيكل الأكاديمي"""
    try:
        response = supabase.table("subjects").select("id, subject_name")\
            .eq("specialization", specialization)\
            .eq("year", year)\
            .eq("semester", semester)\
            .execute()
        return response.data # يُرجع قائمة تحتوي على معرف المادة واسمها
    except Exception:
        return []

def fetch_published_exams(specialization: str, year: str, sem: str, subject: str):
    """جلب الامتحانات المنشورة مرتبة من الأحدث للأقدم"""
    try:
        response = supabase.table("exams").select("*")\
            .eq("specialization", specialization)\
            .eq("year", year)\
            .eq("semester", sem)\
            .eq("subject", subject)\
            .order("created_at", desc=True)\
            .execute()
        return response.data
    except Exception:
        return []

# ==========================================
# 4. دوال التعامل مع التخزين الآمن
# ==========================================
def upload_file_secure(file_obj, is_pending=True):
    try:
        if file_obj.type != "application/pdf":
            return None, "خطأ: مسموح برفع ملفات PDF فقط."
        if file_obj.size > 15 * 1024 * 1024:
            return None, "خطأ: حجم الملف أكبر من الحد المسموح (15 ميجابايت)."
            
        file_bytes = file_obj.getvalue()
        file_extension = file_obj.name.split('.')[-1]
        secure_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # استبدل أسماء الـ buckets القديمة بالاسم الموجود عندك فعلياً
        bucket_name = "pdf_files"
        
        supabase.storage.from_(bucket_name).upload(
            path=secure_filename,
            file=file_bytes,
            file_options={"content-type": "application/pdf"}
        )
        public_url = supabase.storage.from_(bucket_name).get_public_url(secure_filename)
        return public_url, "نجاح"
    except Exception as e:
        return None, f"خطأ في الرفع: {str(e)}"

# ==========================================
# 5. الشريط الجانبي للتنقل
# ==========================================
NAV_ITEMS = [
    {"key": "library", "label": "تصفح المكتبة", "icon": ":material/local_library:"},
    {"key": "upload", "label": "مساهمة طالب", "icon": ":material/upload_file:"},
    {"key": "admin", "label": "لوحة تحكم المشرف", "icon": ":material/admin_panel_settings:"},
]

def render_sidebar():
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "library"

    st.sidebar.markdown("""
        <div class="sidebar-brand">
            <div class="brand-mark">Vol. 01 — Archive</div>
            <div class="brand-name">مكتبة الهندسة<br/>الرقمية</div>
            <div class="brand-sub">منصة أكاديمية موحّدة للموارد الدراسية</div>
        </div>
    """, unsafe_allow_html=True)

    for idx, item in enumerate(NAV_ITEMS, start=1):
        is_active = st.session_state.app_mode == item["key"]
        wrapper_class = "nav-btn active" if is_active else "nav-btn"
        st.sidebar.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)
        if st.sidebar.button(
            f"{idx:02d}   {item['label']}",
            key=f"nav_{item['key']}",
            icon=item["icon"],
            use_container_width=True,
        ):
            st.session_state.app_mode = item["key"]
            st.rerun()
        st.sidebar.markdown('</div>', unsafe_allow_html=True)

    st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # زر تبديل الوضع الداكن/الفاتح — أسفل خيارات التنقل، بشكل مختلف ومميّز عنها
    is_dark = st.session_state.theme == "dark"
    theme_icon = ":material/light_mode:" if is_dark else ":material/dark_mode:"
    theme_label = "الوضع الفاتح" if is_dark else "الوضع الداكن"
    st.sidebar.markdown('<div class="theme-toggle">', unsafe_allow_html=True)
    if st.sidebar.button("", key="theme_toggle_btn", icon=theme_icon, help=theme_label):
        st.session_state.theme = "light" if is_dark else "dark"
        st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    st.sidebar.markdown("""
        <div class="sidebar-footnote">
            نظام رفع الموارد يمر عبر مراجعة واعتماد من المشرف قبل النشر النهائي في المكتبة.
        </div>
    """, unsafe_allow_html=True)

    return st.session_state.app_mode

# ==========================================
# 6. الواجهة الرئيسية لتصفح المكتبة
# ==========================================
def page_header(eyebrow: str, title: str, subtitle: str, icon: str = ""):
    st.markdown(f"""
        <div class="page-header">
            <div class="eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)

def render_main_library():
    page_header(
        "المكتبة",
        "تصفح مكتبة الهندسة",
        "اختر التخصص، السنة، السمستر، ثم المادة للوصول إلى الموارد المتاحة."
    )

    col1, col2 = st.columns(2)
    with col1:
        spec = st.selectbox("التخصص الهندسي", list(ACADEMIC_STRUCTURE.keys()), key="lib_spec")
        sem = None
    with col2:
        year = st.selectbox("السنة الدراسية", list(ACADEMIC_STRUCTURE[spec].keys()), key="lib_year")

    sem = st.selectbox("السمستر (الفصل الدراسي)", ACADEMIC_STRUCTURE[spec][year], key="lib_sem")

    subjects_data = fetch_subjects_from_db(spec, year, sem)
    subjects_list = [item["subject_name"] for item in subjects_data]

    if not subjects_list:
        st.info("لا توجد مواد مسجلة لهذا السمستر حتى الآن. يمكن إضافتها عبر لوحة التحكم.", icon=":material/info:")
        subject = None
    else:
        subject = st.selectbox("المادة الدراسية", subjects_list, key="lib_sub")

    if subject:
        st.markdown("<div style='height: 1.25rem'></div>", unsafe_allow_html=True)
        st.subheader(f"الموارد الخاصة بمادة: {subject}")
        exams = fetch_published_exams(spec, year, sem, subject)

        if not exams:
            st.info("لا توجد موارد مرفوعة لهذه المادة حتى الآن.", icon=":material/folder_off:")
        else:
            for idx, exam in enumerate(exams, start=1):
                col_info, col_action = st.columns([5, 1])
                with col_info:
                    st.markdown(f"""
                        <div class="archive-row">
                            <div class="row-top">
                                <span class="row-index">{idx:02d}</span>
                                <span class="item-title">{exam.get('title', 'مورد أكاديمي')}</span>
                            </div>
                            <span class="item-meta">أُضيف بتاريخ {exam.get('created_at', '')[:10]}</span>
                        </div>
                    """, unsafe_allow_html=True)
                with col_action:
                    file_url = exam.get('file_url')
                    if file_url:
                        st.link_button("معاينة وتحميل", file_url, use_container_width=True, icon=":material/download:")

# ==========================================
# 7. صفحة مساهمة طالب
# ==========================================
def render_student_upload():
    page_header(
        "المساهمات",
        "مساهمة طالب — رفع مورد جديد",
        "التسلسل: التخصص، ثم السنة، ثم السمستر، ثم المادة، ثم رفع ملف PDF للمراجعة."
    )

    col1, col2 = st.columns(2)
    with col1:
        spec = st.selectbox("التخصص الهندسي", list(ACADEMIC_STRUCTURE.keys()), key="stu_spec_fixed")
    with col2:
        year = st.selectbox("السنة الدراسية", list(ACADEMIC_STRUCTURE[spec].keys()), key="stu_year_fixed")

    sem_options = ACADEMIC_STRUCTURE[spec][year]
    sem = st.selectbox("السمستر (الفصل الدراسي)", sem_options, key=f"stu_sem_{spec}_{year}")

    subjects_data = fetch_subjects_from_db(spec, year, sem)
    subjects_list = [item["subject_name"] for item in subjects_data]

    if subjects_list:
        subject = st.selectbox("المادة الدراسية", subjects_list, key=f"stu_sub_{spec}_{year}_{sem}")
    else:
        subject = st.selectbox("المادة الدراسية", ["لا توجد مواد مسجلة لهذا السمستر"], key=f"stu_sub_empty_{spec}_{year}_{sem}")

    title = st.text_input("عنوان المورد", key="stu_title_fixed", placeholder="مثال: ملخص محاضرات — خريف 2025")
    uploaded_file = st.file_uploader(
        "رفع ملف PDF",
        type=["pdf"],
        key="stu_file_fixed",
        help="الحد الأقصى لحجم الملف 15 ميجابايت، وبصيغة PDF فقط."
    )

    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
    submitted = st.button("إرسال للمراجعة", key="stu_submit_btn", type="primary", icon=":material/send:")

    if submitted:
        if not title or not uploaded_file or not subject or subject == "لا توجد مواد مسجلة لهذا السمستر":
            st.error("يرجى إكمال الحقول واختيار مادة صحيحة وإرفاق ملف PDF.", icon=":material/error:")
        else:
            with st.spinner("جاري رفع الملف..."):
                public_url, msg = upload_file_secure(uploaded_file, is_pending=True)
                if public_url:
                    try:
                        supabase.table("pending_exams").insert({
                            "specialization": spec,
                            "year": year,
                            "semester": sem,
                            "subject": subject,
                            "title": title,
                            "file_url": public_url
                        }).execute()
                        st.success("تم إرسال الملف بنجاح إلى الطلبات المعلقة للمراجعة.", icon=":material/check_circle:")
                    except Exception as db_err:
                        st.error(f"خطأ في قاعدة البيانات: {db_err}", icon=":material/error:")
                else:
                    st.error(msg, icon=":material/error:")

# ==========================================
# 8. لوحة تحكم الأدمن (مع نظام إضافة وتعديل وحذف المواد)
# ==========================================
def render_admin_dashboard():
    page_header(
        "الإدارة",
        "لوحة تحكم المشرفين",
        "إدارة المواد الدراسية، مراجعة الطلبات المعلقة، ونشر الموارد."
    )

    admin_password = st.text_input("كلمة مرور المشرف", type="password", key="admin_pass_input")

    if admin_password == "090909":
        st.markdown("""
            <span class="status-pill success">تم التحقق بنجاح</span>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

        admin_tab1, admin_tab2, admin_tab3, admin_tab4 = st.tabs([
            "إدارة وإضافة المواد",
            "الطلبات المعلقة",
            "رفع مباشر",
            "إدارة الموارد المنشورة"
        ])

        # Tab 1: إدارة وإضافة وتعديل المواد الدراسية
        with admin_tab1:
            st.subheader("إضافة وتعديل المواد الدراسية في الهيكل الأكاديمي")

            sub_action = st.radio("العملية", ["إضافة مادة جديدة", "تعديل أو حذف مادة موجودة"], horizontal=True, label_visibility="collapsed")

            if sub_action == "إضافة مادة جديدة":
                with st.form("add_subject_form"):
                    m_spec = st.selectbox("التخصص الهندسي", list(ACADEMIC_STRUCTURE.keys()), key="add_m_spec")
                    m_year = st.selectbox("السنة الدراسية", list(ACADEMIC_STRUCTURE[m_spec].keys()), key="add_m_year")
                    m_sem = st.selectbox("السمستر", ACADEMIC_STRUCTURE[m_spec][m_year], key="add_m_sem")
                    m_name = st.text_input("اسم المادة الجديدة")

                    submit_subject = st.form_submit_button("حفظ وإضافة المادة", type="primary", icon=":material/add:")

                    if submit_subject:
                        if m_name.strip():
                            try:
                                supabase.table("subjects").insert({
                                    "specialization": m_spec,
                                    "year": m_year,
                                    "semester": m_sem,
                                    "subject_name": m_name.strip()
                                }).execute()
                                st.success(f"تم إضافة المادة ({m_name}) بنجاح وربطها بالهيكل.", icon=":material/check_circle:")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"خطأ أثناء الإضافة: {e}", icon=":material/error:")
                        else:
                            st.error("يرجى كتابة اسم المادة.", icon=":material/error:")

            else: # تعديل أو حذف مادة
                st.markdown("##### تعديل أو حذف مواد السمسترات الحالية")
                e_spec = st.selectbox("تصفية حسب التخصص", list(ACADEMIC_STRUCTURE.keys()), key="edit_m_spec")
                e_year = st.selectbox("تصفية حسب السنة", list(ACADEMIC_STRUCTURE[e_spec].keys()), key="edit_m_year")
                e_sem = st.selectbox("تصفية حسب السمستر", ACADEMIC_STRUCTURE[e_spec][e_year], key="edit_m_sem")

                current_subjects = fetch_subjects_from_db(e_spec, e_year, e_sem)

                if not current_subjects:
                    st.info("لا توجد مواد مسجلة في هذا السمستر لتعديلها.", icon=":material/info:")
                else:
                    for sub in current_subjects:
                        col_n, col_edit, col_del = st.columns([2, 2, 1])
                        with col_n:
                            st.markdown(f"<div class='item-title' style='padding-top:0.6rem'>{sub['subject_name']}</div>", unsafe_allow_html=True)
                        with col_edit:
                            new_name_input = st.text_input("تعديل الاسم", value=sub['subject_name'], key=f"rename_{sub['id']}", label_visibility="collapsed")
                            if st.button("حفظ التعديل", key=f"save_ren_{sub['id']}", use_container_width=True):
                                try:
                                    supabase.table("subjects").update({"subject_name": new_name_input.strip()}).eq("id", sub['id']).execute()
                                    st.success("تم تحديث اسم المادة بنجاح.", icon=":material/check_circle:")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"خطأ: {e}", icon=":material/error:")
                        with col_del:
                            if st.button("حذف", key=f"del_sub_{sub['id']}", use_container_width=True, icon=":material/delete:"):
                                try:
                                    supabase.table("subjects").delete().eq("id", sub['id']).execute()
                                    st.warning("تم حذف المادة.", icon=":material/warning:")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"خطأ: {e}", icon=":material/error:")
                        st.divider()

        # Tab 2: الطلبات المعلقة
        with admin_tab2:
            st.subheader("قائمة الطلبات المعلقة بانتظار الموافقة")
            try:
                pending_res = supabase.table("pending_exams").select("*").execute()
                pending_items = pending_res.data

                if not pending_items:
                    st.info("لا توجد طلبات معلقة حالياً.", icon=":material/info:")
                else:
                    for item in pending_items:
                        st.markdown(f"""
                            <div class="content-card">
                                <div class="item-title">{item.get('title')}</div>
                                <div class="item-meta">{item.get('specialization')} · {item.get('year')} · {item.get('semester')} · {item.get('subject')}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        file_url = item.get('file_url')
                        if file_url:
                            st.link_button("معاينة الملف المرفق", file_url, icon=":material/visibility:")

                        col_approve, col_reject = st.columns(2)
                        with col_approve:
                            if st.button("موافقة ونشر", key=f"approve_{item.get('id')}", type="primary", use_container_width=True, icon=":material/check:"):
                                supabase.table("exams").insert({
                                    "specialization": item.get('specialization'),
                                    "year": item.get('year'),
                                    "semester": item.get('semester'),
                                    "subject": item.get('subject'),
                                    "title": item.get('title'),
                                    "file_url": file_url
                                }).execute()
                                supabase.table("pending_exams").delete().eq("id", item.get('id')).execute()
                                st.success("تمت الموافقة ونشر الملف بنجاح.", icon=":material/check_circle:")
                                time.sleep(1)
                                st.rerun()

                        with col_reject:
                            if st.button("رفض وحذف", key=f"reject_{item.get('id')}", use_container_width=True, icon=":material/close:"):
                                supabase.table("pending_exams").delete().eq("id", item.get('id')).execute()
                                st.warning("تم رفض وحذف الطلب.", icon=":material/warning:")
                                time.sleep(1)
                                st.rerun()
                        st.divider()
            except Exception as e:
                st.error(f"خطأ في جلب الطلبات المعلقة: {e}", icon=":material/error:")

        # Tab 3: رفع مباشر للأدمن
        with admin_tab3:
            st.subheader("رفع ونشر مباشر (تخطي الموافقة)")
            ad_spec = st.selectbox("التخصص الهندسي", list(ACADEMIC_STRUCTURE.keys()), key="ad_spec_fixed")
            ad_year = st.selectbox("السنة الدراسية", list(ACADEMIC_STRUCTURE[ad_spec].keys()), key="ad_year_fixed")

            ad_sem_options = ACADEMIC_STRUCTURE[ad_spec][ad_year]
            ad_sem = st.selectbox("السمستر (الفصل الدراسي)", ad_sem_options, key=f"ad_sem_{ad_spec}_{ad_year}")

            ad_subjects_data = fetch_subjects_from_db(ad_spec, ad_year, ad_sem)
            ad_subjects_list = [item["subject_name"] for item in ad_subjects_data]

            if ad_subjects_list:
                ad_subject = st.selectbox("المادة الدراسية", ad_subjects_list, key=f"ad_sub_{ad_spec}_{ad_year}_{ad_sem}")
            else:
                ad_subject = st.selectbox("المادة الدراسية", ["لا توجد مواد مسجلة لهذا السمستر"], key=f"ad_sub_empty_{ad_spec}_{ad_year}_{ad_sem}")

            ad_title = st.text_input("عنوان المورد", key="ad_title_fixed")
            ad_file = st.file_uploader("رفع ملف PDF", type=["pdf"], key="ad_file_fixed")

            submitted_direct = st.button("نشر مباشرة", key="ad_submit_btn", type="primary", icon=":material/publish:")

            if submitted_direct:
                if ad_file and ad_title and ad_subject and ad_subject != "لا توجد مواد مسجلة لهذا السمستر":
                    with st.spinner("جاري رفع ونشر الملف..."):
                        public_url, msg = upload_file_secure(ad_file, is_pending=False)
                        if public_url:
                            supabase.table("exams").insert({
                                "specialization": ad_spec,
                                "year": ad_year,
                                "semester": ad_sem,
                                "subject": ad_subject,
                                "title": ad_title,
                                "file_url": public_url
                            }).execute()
                            st.success("تم نشر الملف مباشرة في المكتبة بنجاح.", icon=":material/check_circle:")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg, icon=":material/error:")
                else:
                    st.error("يرجى التأكد من اكتمال الحقول وإرفاق ملف PDF صالح.", icon=":material/error:")

        # Tab 4: إدارة الحذف للموارد المنشورة
        with admin_tab4:
            st.subheader("إدارة أو حذف الموارد المنشورة")
            try:
                all_exams_res = supabase.table("exams").select("*").execute()
                all_exams = all_exams_res.data
                if not all_exams:
                    st.info("لا توجد موارد منشورة حالياً.", icon=":material/info:")
                else:
                    for idx, ex in enumerate(all_exams, start=1):
                        col_info, col_del = st.columns([4, 1])
                        with col_info:
                            st.markdown(f"""
                                <div class="archive-row">
                                    <div class="row-top">
                                        <span class="row-index">{idx:02d}</span>
                                        <span class="item-title">{ex.get('title')}</span>
                                    </div>
                                    <span class="item-meta">{ex.get('specialization')} · {ex.get('year')} · {ex.get('semester')} · {ex.get('subject')}</span>
                                </div>
                            """, unsafe_allow_html=True)
                        with col_del:
                            if st.button("حذف", key=f"del_pub_{ex.get('id')}", use_container_width=True, icon=":material/delete:"):
                                supabase.table("exams").delete().eq("id", ex.get('id')).execute()
                                st.success("تم حذف المورد بنجاح.", icon=":material/check_circle:")
                                time.sleep(1)
                                st.rerun()
            except Exception as e:
                st.error(f"خطأ في جلب الموارد: {e}", icon=":material/error:")

    elif admin_password:
        st.error("كلمة المرور غير صحيحة.", icon=":material/lock:")

# ==========================================
# 9. نقطة التشغيل الرئيسية
# ==========================================
def main():
    app_mode = render_sidebar()
    if app_mode == "library":
        render_main_library()
    elif app_mode == "upload":
        render_student_upload()
    else:
        render_admin_dashboard()

if __name__ == "__main__":
    main()