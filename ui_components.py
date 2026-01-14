import streamlit as st

def render_page_header():
    """Render the main page title."""
    st.markdown("""
        <h1 style="text-align: center; color: #232f3e; margin-top: 0; margin-bottom: 2rem; font-size: 2.2rem;">
            AWS Certified Solutions Architect Associate (SAA-C03)
        </h1>
    """, unsafe_allow_html=True)

def render_question_header(idx_ptr, total):
    """Render question number and progress."""
    st.markdown(f"""
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
    <div style="display: flex; align-items: center; gap: 0.75rem;">
        <span style="font-size: 1.5rem; font-weight: 700; color: #232f3e;">Question #{idx_ptr+1}</span>
    </div>
    <span style="font-size: 0.875rem; color: #64748b; font-weight: 500;">{idx_ptr+1} of {total}</span>
</div>
    """, unsafe_allow_html=True)

def render_question_card(question_text, is_multiselect=False):
    """Render question text card."""
    st.markdown(
        f'<div class="question-card"><div class="question-text">{question_text.replace(chr(10), "<br>")}</div></div>', 
        unsafe_allow_html=True
    )
    
    if is_multiselect:
        st.markdown(
            '<p style="color: #ff9900; font-weight: 600; font-size: 0.875rem; margin-bottom: 0.5rem;">📌 Select all that apply</p>', 
            unsafe_allow_html=True
        )

def render_answer_feedback(ans, correct_answer):
    """Render success or error message for user answer."""
    correct = ans == (correct_answer or "")
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

def render_auto_scroll_script():
    """Inject JavaScript for auto-scrolling to elements."""
    st.markdown("""
        <script>
        function scrollToElementWithRetry(id) {
            let attempts = 0;
            const maxAttempts = 20; // Try for 2 seconds (100ms * 20)
            
            const interval = setInterval(() => {
                // Try finding in current doc (if inline) or parent (if iframe)
                let element = document.getElementById(id) || window.parent.document.getElementById(id);
                
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    clearInterval(interval);
                    console.log("Scrolled to " + id);
                } else {
                    attempts++;
                    if (attempts >= maxAttempts) {
                        clearInterval(interval);
                        console.log("Could not find element " + id + " after " + maxAttempts + " attempts");
                    }
                }
            }, 100);
        }
        </script>
    """, unsafe_allow_html=True)

def render_ai_explanation(question_id, explanation_text, discussion_link=None, auto_scroll=False):
    """Render AI explanation section with optional auto-scroll."""
    st.markdown(f'<div id="explanation-{question_id}"></div>', unsafe_allow_html=True)
    with st.expander("🤖 Phân Tích (AI Teacher)", expanded=True):
        st.markdown(explanation_text)
        if discussion_link:
            st.caption(f"[Xem thảo luận gốc trên ExamTopics]({discussion_link})")
        
        if auto_scroll:
            st.markdown(f'<script>scrollToElementWithRetry("explanation-{question_id}");</script>', unsafe_allow_html=True)

def render_ai_theory(question_id, theory_text, auto_scroll=False):
    """Render AI theory section with optional auto-scroll."""
    st.markdown(f'<div id="theory-{question_id}"></div>', unsafe_allow_html=True)
    with st.expander("📖 Kiến Thức Nền (Concepts)", expanded=True):
        st.markdown(theory_text)
        
        if auto_scroll:
            st.markdown(f'<script>scrollToElementWithRetry("theory-{question_id}");</script>', unsafe_allow_html=True)

def render_navigation_buttons(idx_ptr, total, is_search, on_prev, on_next, on_jump):
    """Render navigation buttons (Previous, Jump, Next)."""
    st.divider()
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c1:
        if st.button("⬅️ Previous", use_container_width=True):
            on_prev()
            
    with c2:
        jc1, jc2 = st.columns([3, 1], gap="small")
        with jc1:
            new_val = st.number_input(
                "Go to Question #", 
                min_value=1, 
                max_value=total, 
                value=idx_ptr+1, 
                label_visibility="collapsed"
            )
            if new_val != idx_ptr+1:
                on_jump(new_val - 1)
                
        with jc2:
            if st.button("Go", use_container_width=True):
                pass  # Logic handled by number_input
                    
    with c3:
        if st.button("Next ➡️", use_container_width=True):
            on_next()

def render_sidebar_tools(total_questions, answered_count):
    """Render sidebar settings and tools."""
    st.header("⚙️ Settings")
    
    # Progress
    st.markdown(f"**Total Qs:** {total_questions} | **Done:** {answered_count}")
    st.progress(min(answered_count / total_questions, 1.0))
    st.divider()
    
    # Search
    search = st.text_input("🔍 Search")
    
    # Shuffle and Reset buttons
    c1, c2 = st.columns(2)
    shuffle_clicked = c1.button("🔀 Shuffle")
    reset_clicked = c2.button("🔄 Reset")
    
    return search, shuffle_clicked, reset_clicked
