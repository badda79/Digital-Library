from __future__ import annotations
import streamlit as st
from supabase import create_client, Client
import time
import uuid

# ==========================================
# 1. إعدادات الصفحة والتهيئة الأساسية
# ==========================================
st.set_page_config(
    page_title="منصة مكتبة الهندسة",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        color: #1E3A8A;
        text-align: center;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-caption {
        text-align: center;
        color: #4B5563;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

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
def render_sidebar():
    st.sidebar.markdown("### 🎛️ خيارات النظام")
    app_mode = st.sidebar.selectbox(
        "اختر القسم:", 
        ["📚 تصفح المكتبة", "📤 مساهمة طالب (رفع ملف)", "🔐 لوحة تحكم المشرف"]
    )
    st.sidebar.markdown("---")
    st.sidebar.info("💡 منصة هندسية آمنة ومزودة بنظام مراجعة وموافقة ذكي.")
    return app_mode

# ==========================================
# 6. الواجهة الرئيسية لتصفح المكتبة
# ==========================================
def render_main_library():
    st.markdown('<div class="main-title">🏛️ منصة مكتبة الهندسة</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-caption">التسلسل الأكاديمي: التخصص ⬅️ السنة الدراسية ⬅️ السمستر ⬅️ المادة</div>', unsafe_allow_html=True)
    
    spec = st.selectbox("1️⃣ اختر التخصص الهندسي:", list(ACADEMIC_STRUCTURE.keys()), key="lib_spec")
    year = st.selectbox("2️⃣ اختر السنة الدراسية:", list(ACADEMIC_STRUCTURE[spec].keys()), key="lib_year")
    sem = st.selectbox("3️⃣ اختر السمستر (الفصل الدراسي):", ACADEMIC_STRUCTURE[spec][year], key="lib_sem")
    
    subjects_data = fetch_subjects_from_db(spec, year, sem)
    subjects_list = [item["subject_name"] for item in subjects_data]
    
    if not subjects_list:
        st.warning("⚠️ لا توجد مواد مسجلة لهذا السمستر حتى الآن. يمكنك إضافتها عبر لوحة التحكم.")
        subject = None
    else:
        subject = st.selectbox("4️⃣ اختر المادة الدراسية:", subjects_list, key="lib_sub")
        
    if subject:
        st.markdown("---")
        st.subheader(f"📂 الامتحانات والموارد الخاصة بمادة: {subject}")
        exams = fetch_published_exams(spec, year, sem, subject)
        
        if not exams:
            st.info("📭 لا توجد امتحانات مرفوعة لهذه المادة حتى الآن.")
        else:
            for exam in exams:
                with st.container():
                    cols = st.columns([3, 1])
                    with cols[0]:
                        st.markdown(f"📄 **{exam.get('title', 'ملف امتحان')}**")
                        st.caption(f"📅 تاريخ الإضافة: {exam.get('created_at', '')[:10]}")
                    with cols[1]:
                        file_url = exam.get('file_url')
                        if file_url:
                            st.markdown(f"[🔗 معاينة وتحميل]({file_url})", unsafe_allow_html=True)
                st.divider()

# ==========================================
# 7. صفحة مساهمة طالب
# ==========================================
def render_student_upload():
    st.markdown("### 📤 مساهمة طالب (رفع امتحان جديد)")
    st.caption("التسلسل: التخصص ⬅️ السنة الدراسية ⬅️ السمستر (التابع للسنة فقط) ⬅️ المادة ⬅️ اسم الامتحان ⬅️ رفع ملف PDF")
    
    spec = st.selectbox("1️⃣ اختر التخصص الهندسي:", list(ACADEMIC_STRUCTURE.keys()), key="stu_spec_fixed")
    year = st.selectbox("2️⃣ اختر السنة الدراسية:", list(ACADEMIC_STRUCTURE[spec].keys()), key="stu_year_fixed")
    
    sem_options = ACADEMIC_STRUCTURE[spec][year]
    sem = st.selectbox("3️⃣ اختر السمستر (الفصل الدراسي):", sem_options, key=f"stu_sem_{spec}_{year}")
    
    subjects_data = fetch_subjects_from_db(spec, year, sem)
    subjects_list = [item["subject_name"] for item in subjects_data]
    
    if subjects_list:
        subject = st.selectbox("4️⃣ اختر المادة الدراسية:", subjects_list, key=f"stu_sub_{spec}_{year}_{sem}")
    else:
        subject = st.selectbox("4️⃣ اختر المادة الدراسية:", ["لا توجد مواد مسجلة لهذا السمستر"], key=f"stu_sub_empty_{spec}_{year}_{sem}")
        
    title = st.text_input("5️⃣ اسم الامتحان:", key="stu_title_fixed")
    uploaded_file = st.file_uploader("6️⃣ رفع ملف PDF:", type=["pdf"], key="stu_file_fixed")
    
    submitted = st.button("7️⃣ زر رفع الملف", key="stu_submit_btn")
    
    if submitted:
        if not title or not uploaded_file or not subject or subject == "لا توجد مواد مسجلة لهذا السمستر":
            st.error("❌ يرجى إكمال الحقول واختيار مادة صحيحة وإرفاق ملف PDF.")
        else:
            with st.spinner("⏳ جاري رفع الملف..."):
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
                        st.success("🎉 تم إرسال الملف بنجاح إلى الطلبات المعلقة للمراجعة!")
                    except Exception as db_err:
                        st.error(f"خطأ في قاعدة البيانات: {db_err}")
                else:
                    st.error(msg)

# ==========================================
# 8. لوحة تحكم الأدمن (مع نظام إضافة وتعديل وحذف المواد)
# ==========================================
def render_admin_dashboard():
    st.markdown('<div class="main-title">🔐 لوحة تحكم المشرفين</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-caption">إدارة المواد الدراسية، الطلبات المعلقة، ونشر الموارد</div>', unsafe_allow_html=True)
    
    admin_password = st.text_input("كلمة مرور المشرف:", type="password", key="admin_pass_input")
    
    if admin_password == "090909":
        st.success("✅ تم التحقق بنجاح.")
        
        admin_tab1, admin_tab2, admin_tab3, admin_tab4 = st.tabs([
            "📚 إدارة وإضافة المواد", 
            "📥 الطلبات المعلقة", 
            "🚀 رفع مباشر", 
            "⚙️ إدارة الموارد المنشورة"
        ])
        
        # Tab 1: إدارة وإضافة وتعديل المواد الدراسية
        with admin_tab1:
            st.subheader("📚 إضافة وتعديل المواد الدراسية في الهيكل الأكاديمي")
            
            sub_action = st.radio("اختر العملية:", ["➕ إضافة مادة جديدة", "✏️ تعديل أو حذف مادة موجودة"], horizontal=True)
            
            if sub_action == "➕ إضافة مادة جديدة":
                with st.form("add_subject_form"):
                    m_spec = st.selectbox("اختر التخصص الهندسي:", list(ACADEMIC_STRUCTURE.keys()), key="add_m_spec")
                    m_year = st.selectbox("اختر السنة الدراسية:", list(ACADEMIC_STRUCTURE[m_spec].keys()), key="add_m_year")
                    m_sem = st.selectbox("اختر السمستر:", ACADEMIC_STRUCTURE[m_spec][m_year], key="add_m_sem")
                    m_name = st.text_input("اسم المادة الجديدة:")
                    
                    submit_subject = st.form_submit_button("حفظ وإضافة المادة")
                    
                    if submit_subject:
                        if m_name.strip():
                            try:
                                supabase.table("subjects").insert({
                                    "specialization": m_spec,
                                    "year": m_year,
                                    "semester": m_sem,
                                    "subject_name": m_name.strip()
                                }).execute()
                                st.success(f"🎉 تم إضافة المادة ({m_name}) بنجاح وربطها بالهيكل!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"خطأ أثناء الإضافة: {e}")
                        else:
                            st.error("يرجى كتابة اسم المادة.")
            
            else: # تعديل أو حذف مادة
                st.markdown("### ✏️ تعديل أو حذف مواد السمسترات الحالية")
                e_spec = st.selectbox("تصفية حسب التخصص:", list(ACADEMIC_STRUCTURE.keys()), key="edit_m_spec")
                e_year = st.selectbox("تصفية حسب السنة:", list(ACADEMIC_STRUCTURE[e_spec].keys()), key="edit_m_year")
                e_sem = st.selectbox("تصفية حسب السمستر:", ACADEMIC_STRUCTURE[e_spec][e_year], key="edit_m_sem")
                
                current_subjects = fetch_subjects_from_db(e_spec, e_year, e_sem)
                
                if not current_subjects:
                    st.info("لا توجد مواد مسجلة في هذا السمستر لتعديلها.")
                else:
                    for sub in current_subjects:
                        col_n, col_edit, col_del = st.columns([2, 2, 1])
                        with col_n:
                            st.write(f"📖 **{sub['subject_name']}**")
                        with col_edit:
                            new_name_input = st.text_input("تعديل الاسم", value=sub['subject_name'], key=f"rename_{sub['id']}")
                            if st.button("حفظ التعديل", key=f"save_ren_{sub['id']}"):
                                try:
                                    supabase.table("subjects").update({"subject_name": new_name_input.strip()}).eq("id", sub['id']).execute()
                                    st.success("تم تحديث اسم المادة بنجاح!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"خطأ: {e}")
                        with col_del:
                            if st.button("🗑️ حذف", key=f"del_sub_{sub['id']}"):
                                try:
                                    supabase.table("subjects").delete().eq("id", sub['id']).execute()
                                    st.warning("تم حذف المادة.")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"خطأ: {e}")
                        st.divider()

        # Tab 2: الطلبات المعلقة
        with admin_tab2:
            st.subheader("📋 قائمة الطلبات المعلقة بانتظار الموافقة")
            try:
                pending_res = supabase.table("pending_exams").select("*").execute()
                pending_items = pending_res.data
                
                if not pending_items:
                    st.info("لا توجد طلبات معلقة حالياً.")
                else:
                    for item in pending_items:
                        with st.container():
                            st.markdown(f"### 📄 {item.get('title')}")
                            st.write(f"التخصص: {item.get('specialization')} | السنة: {item.get('year')} | السمستر: {item.get('semester')} | المادة: {item.get('subject')}")
                            file_url = item.get('file_url')
                            if file_url:
                                st.markdown(f"[🔗 معاينة / تحميل الملف المرفق]({file_url})", unsafe_allow_html=True)
                            
                            col_approve, col_reject = st.columns(2)
                            with col_approve:
                                if st.button("✅ موافقة ونشر", key=f"approve_{item.get('id')}"):
                                    supabase.table("exams").insert({
                                        "specialization": item.get('specialization'),
                                        "year": item.get('year'),
                                        "semester": item.get('semester'),
                                        "subject": item.get('subject'),
                                        "title": item.get('title'),
                                        "file_url": file_url
                                    }).execute()
                                    supabase.table("pending_exams").delete().eq("id", item.get('id')).execute()
                                    st.success("تمت الموافقة ونشر الملف بنجاح!")
                                    time.sleep(1)
                                    st.rerun()
                                    
                            with col_reject:
                                if st.button("❌ رفض وحذف", key=f"reject_{item.get('id')}"):
                                    supabase.table("pending_exams").delete().eq("id", item.get('id')).execute()
                                    st.warning("تم رفض وحذف الطلب.")
                                    time.sleep(1)
                                    st.rerun()
                        st.divider()
            except Exception as e:
                st.error(f"خطأ في جلب الطلبات المعلقة: {e}")

        # Tab 3: رفع مباشر للأدمن
        with admin_tab3:
            st.subheader("🚀 رفع ونشر مباشر (تخطي الموافقة)")
            ad_spec = st.selectbox("1️⃣ اختر التخصص الهندسي:", list(ACADEMIC_STRUCTURE.keys()), key="ad_spec_fixed")
            ad_year = st.selectbox("2️⃣ اختر السنة الدراسية:", list(ACADEMIC_STRUCTURE[ad_spec].keys()), key="ad_year_fixed")
            
            ad_sem_options = ACADEMIC_STRUCTURE[ad_spec][ad_year]
            ad_sem = st.selectbox("3️⃣ اختر السمستر (الفصل الدراسي):", ad_sem_options, key=f"ad_sem_{ad_spec}_{ad_year}")
            
            ad_subjects_data = fetch_subjects_from_db(ad_spec, ad_year, ad_sem)
            ad_subjects_list = [item["subject_name"] for item in ad_subjects_data]
            
            if ad_subjects_list:
                ad_subject = st.selectbox("4️⃣ اختر المادة الدراسية:", ad_subjects_list, key=f"ad_sub_{ad_spec}_{ad_year}_{ad_sem}")
            else:
                ad_subject = st.selectbox("4️⃣ اختر المادة الدراسية:", ["لا توجد مواد مسجلة لهذا السمستر"], key=f"ad_sub_empty_{ad_spec}_{ad_year}_{ad_sem}")
            
            ad_title = st.text_input("5️⃣ اسم الامتحان:", key="ad_title_fixed")
            ad_file = st.file_uploader("6️⃣ رفع ملف PDF:", type=["pdf"], key="ad_file_fixed")
            
            submitted_direct = st.button("7️⃣ زر رفع الملف", key="ad_submit_btn")
            
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
                            st.success("🎉 تم نشر الملف مباشرة في المكتبة بنجاح!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    st.error("يرجى التأكد من اكتمال الحقول وإرفاق ملف PDF صالح.")

        # Tab 4: إدارة الحذف للموارد المنشورة
        with admin_tab4:
            st.subheader("⚙️ إدارة أو حذف الموارد المنشورة")
            try:
                all_exams_res = supabase.table("exams").select("*").execute()
                all_exams = all_exams_res.data
                if not all_exams:
                    st.info("لا توجد موارد منشورة حالياً.")
                else:
                    for ex in all_exams:
                        col_info, col_del = st.columns([3, 1])
                        with col_info:
                            st.write(f"📄 **{ex.get('title')}** | {ex.get('specialization')} - {ex.get('year')} - {ex.get('semester')} - {ex.get('subject')}")
                        with col_del:
                            if st.button("🗑️ حذف", key=f"del_pub_{ex.get('id')}"):
                                supabase.table("exams").delete().eq("id", ex.get('id')).execute()
                                st.success("تم حذف المورد بنجاح.")
                                time.sleep(1)
                                st.rerun()
                        st.divider()
            except Exception as e:
                st.error(f"خطأ في جلب الموارد: {e}")

    elif admin_password:
        st.error("❌ كلمة المرور غير صحيحة.")

# ==========================================
# 9. نقطة التشغيل الرئيسية
# ==========================================
def main():
    app_mode = render_sidebar()
    if app_mode == "📚 تصفح المكتبة":
        render_main_library()
    elif app_mode == "📤 مساهمة طالب (رفع ملف)":
        render_student_upload()
    else:
        render_admin_dashboard()

if __name__ == "__main__":
    main()