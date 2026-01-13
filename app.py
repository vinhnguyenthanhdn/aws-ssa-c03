import streamlit as st
import streamlit.components.v1 as components
import random
import google.generativeai as genai
from pathlib import Path
from quiz_parser import parse_markdown_file

# Configure Gemini
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

def get_ai_explanation(question, options, correct_answer):
    try:
        model = genai.GenerativeModel('gemini-3-flash-preview')
        prompt = f"""
        Bạn là chuyên gia AWS SAA-C03. Nhiệm vụ của bạn là phân tích câu hỏi trắc nghiệm này để giải thích cho học viên.

        **Câu hỏi:**
        {question}

        **Các lựa chọn:**
        {options}

        **Đáp án đúng:** {correct_answer}

        **Yêu cầu Output (Rất quan trọng):**
        - **TUYỆT ĐỐI KHÔNG** có lời chào mở đầu (VD: "Chào bạn", "Tôi là chuyên gia...").
        - **TUYỆT ĐỐI KHÔNG** có lời chúc hay kết luận xã giao ở cuối (VD: "Chúc thi tốt", "Hy vọng giúp ích...").
        - Chỉ tập trung vào nội dung chuyên môn cô đọng.

        **Cấu trúc phân tích:**
        1. **🎯 Phân tích Yêu cầu:** Xác định từ khóa (keywords) và mục tiêu của đề bài.
        2. **✅ Giải thích đáp án đúng:** Tại sao nó đáp ứng tốt nhất yêu cầu (về kỹ thuật, chi phí, best practice)?
        3. **❌ Giải thích đáp án sai:** Lí do từng đáp án còn lại không phù hợp.
        4. **💡 Mẹo nhớ nhanh:** Mapping từ khóa <-> Dịch vụ.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠ Không thể tải phân tích từ AI. Lỗi: {str(e)}"

def get_ai_theory(question, options):
    try:
        model = genai.GenerativeModel('gemini-3-flash-preview')
        prompt = f"""
        Bạn là từ điển sống về AWS. Hãy giải thích ngắn gọn các **Dịch vụ** hoặc **Khái niệm** AWS xuất hiện trong văn bản sau:

        **Ngữ cảnh (Câu hỏi & Đáp án):**
        {question}
        {options}

        **Yêu cầu Output:**
        - Chỉ tập trung vào CÁC KHÁI NIỆM/DỊCH VỤ (VD: AWS Lambda, IOPS, Consistency Model...).
        - Với mỗi khái niệm: Đưa ra định nghĩa 1 dòng và Use Case chính 1 dòng.
        - Không giải thích câu hỏi, không phân tích đúng sai.
        - Trình bày dạng danh sách Markdown sạch sẽ.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠ Lỗi tải lý thuyết: {str(e)}"

st.set_page_config(page_title="SAA-C03 Prep", page_icon="☁️", layout="wide", initial_sidebar_state="collapsed")

# Load CSS
with open(Path(__file__).parent / "style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Hide Streamlit viewer badge (works on Streamlit Cloud)
# Hide Streamlit viewer badge (JS injection via markdown for better context access)
st.markdown("""
    <script>
        var observer = new MutationObserver(function(mutations) {
            var parentDoc = window.parent.document;
            if (parentDoc) {
                var newStyle = parentDoc.createElement("style");
                newStyle.innerHTML = `
                    ._viewerBadge_nim44_23, 
                    ._container_gzau3_1._viewerBadge_nim44_23, 
                    [class*="viewerBadge"], 
                    header[data-testid="stHeader"],
                    .stDeployButton,
                    [data-testid="stToolbar"] {
                        display: none !important;
                        visibility: hidden !important;
                    }
                `;
                parentDoc.head.appendChild(newStyle);
            }
        });
        observer.observe(window.parent.document.body, { childList: true, subtree: true });
        
        // Initial run
        try {
            var parentDoc = window.parent.document;
            if (parentDoc) {
                var elements = parentDoc.querySelectorAll('._viewerBadge_nim44_23, [class*="viewerBadge"], [data-testid="stToolbar"]');
                elements.forEach(el => el.style.display = 'none');
                
                // Inject style tag into parent for persistence
                var style = parentDoc.createElement('style');
                style.innerHTML = `
                    ._viewerBadge_nim44_23,
                    ._container_gzau3_1._viewerBadge_nim44_23,
                    [class*="viewerBadge"],
                    .stDeployButton,
                    [data-testid="stToolbar"] {
                        display: none !important;
                    }
                `;
                parentDoc.head.appendChild(style);
            }
        } catch (e) {
            console.log("Could not access parent document to hide Streamlit branding: " + e);
        }
    </script>
""", unsafe_allow_html=True)

def load_data():
    """Handles file loading logic."""
    fpath = Path(__file__).parent / "SAA_C03.md"
    if fpath.exists():
        return fpath.read_text(encoding='utf-8')
    return None

def main():
    if 'current_index' not in st.session_state:
        st.session_state.update({'current_index': 0, 'user_answers': {}, 'random_mode': False, 'question_order': []})

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        content = load_data()
        if not content:
            uploaded = st.file_uploader("Upload .md file", type=["md"])
            if uploaded: content = uploaded.getvalue().decode("utf-8")
            else: st.stop()
            
        questions = parse_markdown_file(content)
        total = len(questions)
        
        # Init order
        if len(st.session_state.question_order) != total:
            st.session_state.question_order = list(range(total))
            
        st.markdown(f"**Total Qs:** {total} | **Done:** {len(st.session_state.user_answers)}")
        st.progress(min(len(st.session_state.user_answers) / total, 1.0))
        st.divider()
        
        # Tools
        search = st.text_input("🔍 Search")
        c1, c2 = st.columns(2)
        if c1.button("🔀 Shuffle"):
            st.session_state.random_mode = True
            random.shuffle(st.session_state.question_order)
            st.session_state.current_index = 0
            st.rerun()
        if c2.button("🔄 Reset"):
            st.session_state.random_mode = False
            st.session_state.question_order = list(range(total))
            st.session_state.current_index = 0
            st.session_state.user_answers = {}
            st.rerun()
            


    # Main Logic
    indices = st.session_state.question_order
    is_search = False
    
    if search:
        indices = [i for i in st.session_state.question_order if search.lower() in questions[i]['question'].lower() or search in questions[i]['id']]
        if not indices: st.warning("No matches"); st.stop()
        if 'search_query' not in st.session_state or st.session_state.search_query != search:
            st.session_state.search_query = search; st.session_state.search_idx = 0
        idx_ptr = st.session_state.search_idx if st.session_state.search_idx < len(indices) else 0
        real_idx = indices[idx_ptr]
        is_search = True
    else:
        idx_ptr = st.session_state.current_index
        real_idx = indices[idx_ptr]



    q = questions[real_idx]
    
    # UI Render
    st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span class="question-number">{idx_ptr+1}</span>
                <span style="font-size: 1.5rem; font-weight: 700; color: #232f3e;">Question #{idx_ptr+1}</span>
            </div>
            <span style="font-size: 0.875rem; color: #64748b; font-weight: 500;">{idx_ptr+1} of {len(indices)}</span>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown(f'<div class="question-card"><div class="question-text">{q["question"].replace(chr(10), "<br>")}</div></div>', unsafe_allow_html=True)
        
        # Show multi-select hint
        if q['is_multiselect']:
            st.markdown('<p style="color: #ff9900; font-weight: 600; font-size: 0.875rem; margin-bottom: 0.5rem;">📌 Select all that apply</p>', unsafe_allow_html=True)
        
        with st.form(key=f"q_{q['id']}"):
            user_ch = []
            if q['is_multiselect']:
                for opt in q['options']:
                    if st.checkbox(opt): user_ch.append(opt.split('.')[0])
            else:
                sel = st.radio("Select your answer:", q['options'], index=None, label_visibility="collapsed")
                if sel: user_ch.append(sel.split('.')[0])
            

            
            f1, f2 = st.columns([1, 1])
            with f1:
                sub = st.form_submit_button("✓ Submit Answer", type="primary", use_container_width=True)
            with f2:
                theory_req = st.form_submit_button("📖 Lý Thuyết Basics", use_container_width=True)
            
        ans = st.session_state.user_answers.get(q['id'])
        
        # Init storage
        if "theories" not in st.session_state: st.session_state.theories = {}
        if "explanations" not in st.session_state: st.session_state.explanations = {}

        # Handle Answer Submit
        if sub and user_ch:
            ans = "".join(sorted(user_ch))
            st.session_state.user_answers[q['id']] = ans
        
        # Handle Theory Request
        if theory_req:
             if q['id'] not in st.session_state.theories:
                 with st.spinner("Đang tổng hợp kiến thức..."):
                     opts_text = "\n".join(q['options'])
                     st.session_state.theories[q['id']] = get_ai_theory(q['question'], opts_text)
        
        # Display Results & Content
        if ans:
            correct = ans == (q['correct_answer'] or "")
            if correct:
                st.markdown(f'''
                    <div class="success-msg">
                        <span style="margin-left: 0.5rem;">Correct! You answered: <strong>{ans}</strong></span>
                    </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                    <div class="error-msg">
                        <span style="margin-left: 0.5rem;">Incorrect. You answered: <strong>{ans}</strong></span>
                    </div>
                ''', unsafe_allow_html=True)
            
            # AI Analysis Section
            with st.expander("🤖 Phân Tích (AI Teacher)", expanded=True):
                if q['id'] not in st.session_state.explanations:
                    with st.spinner("Đang phân tích câu hỏi... (Gemini AI)"):
                        opts_text = "\n".join(q['options'])
                        explanation = get_ai_explanation(q['question'], opts_text, q['correct_answer'])
                        st.session_state.explanations[q['id']] = explanation
                
                st.markdown(st.session_state.explanations[q['id']])
                if q['discussion_link']: 
                    st.caption(f"[Xem thảo luận gốc trên ExamTopics]({q['discussion_link']})")

        # Display Theory Section (Independent of Answer status)
        if q['id'] in st.session_state.theories:
            with st.expander("📖 Kiến Thức Nền (Concepts)", expanded=True):
                st.markdown(st.session_state.theories[q['id']])

    # Nav
    st.divider()
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c1:
        if st.button("⬅️ Previous", use_container_width=True):
            if is_search and st.session_state.search_idx > 0: st.session_state.search_idx -= 1; st.rerun()
            elif not is_search and st.session_state.current_index > 0: st.session_state.current_index -= 1; st.rerun()
            
    with c2:
        with st.form("jump_to_question", clear_on_submit=False):
            jc1, jc2 = st.columns([4, 1], gap="small")
            with jc1:
                jump_val = st.number_input("Go to Question #", min_value=1, max_value=len(indices), value=idx_ptr+1, label_visibility="collapsed")
            with jc2:
                # Use a unique key to allow styling via CSS if needed, though form scope helps
                if st.form_submit_button("Go", use_container_width=True):
                    if is_search:
                         st.session_state.search_idx = jump_val - 1
                    else:
                         st.session_state.current_index = jump_val - 1
                    st.rerun()
                    
    with c3:
        if st.button("Next ➡️", use_container_width=True):
            if is_search and st.session_state.search_idx < len(indices)-1: st.session_state.search_idx += 1; st.rerun()
            elif not is_search and st.session_state.current_index < len(questions)-1: st.session_state.current_index += 1; st.rerun()

if __name__ == "__main__":
    main()
