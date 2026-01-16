import streamlit as st
from translations import get_text, get_available_languages
# Force refresh for Streamlit Cloud - 2026-01-16 v2

def render_language_selector():
    """Render language selector buttons."""
    # Get current language
    lang = st.session_state.get('language', 'vi')
    languages = get_available_languages()
    
    # Create a container at the top for language selection
    # Increased button column width to prevent text wrapping
    cols = st.columns([6, 2, 2])
    
    with cols[1]:
        # Vietnamese button
        btn_style = "primary" if lang == "vi" else "secondary"
        if st.button(f"{languages['vi']['flag']} {languages['vi']['name']}", 
                     key='lang_vi', 
                     use_container_width=True,
                     type=btn_style):
            st.session_state.language = 'vi'
            st.rerun()
    
    with cols[2]:
        # English button
        btn_style = "primary" if lang == "en" else "secondary"
        if st.button(f"{languages['en']['flag']} {languages['en']['name']}", 
                     key='lang_en', 
                     use_container_width=True,
                     type=btn_style):
            st.session_state.language = 'en'
            st.rerun()
    
    st.divider()

def render_page_header():
    """Render the main page title."""
    st.markdown("""
        <h1 style="text-align: center; color: #232f3e; margin-top: 0; margin-bottom: 2rem; font-size: 2.2rem;">
            AWS Certified Solutions Architect Associate Prep (SAA-C03)
        </h1>
    """, unsafe_allow_html=True)

def render_preserve_scroll():
    """Inject JavaScript to preserve scroll position during rerun."""
    st.markdown("""
        <script>
        (function() {
            // Save scroll position continuously
            var saveScroll = function() {
                sessionStorage.setItem('streamlitScrollPos', window.scrollY || window.pageYOffset || 0);
            };
            
            // Save on scroll
            window.addEventListener('scroll', saveScroll, { passive: true });
            
            // Restore scroll position IMMEDIATELY on load
            var scrollPos = sessionStorage.getItem('streamlitScrollPos');
            if (scrollPos && scrollPos !== '0') {
                // Restore immediately without delay
                window.scrollTo(0, parseInt(scrollPos));
                
                // Also try again after a short delay for safety
                setTimeout(function() {
                    window.scrollTo(0, parseInt(scrollPos));
                }, 50);
            }
        })();
        </script>
    """, unsafe_allow_html=True)

def render_footer():
    """Render the footer with contact information."""
    st.markdown("""
        <hr style="margin: 1.5rem 0 1rem 0; border: none; border-top: 1px solid #e2e8f0;">
        <div style="text-align: center; color: #64748b; font-size: 0.875rem; padding-bottom: 0.5rem;">
            <p style="margin-bottom: 0.5rem;">Developed by Vinh Nguyen.</p>
            <p style="margin-bottom: 0;">Found any errors or have suggestions for improvement? <br>Please reach out to: <a href="mailto:vinh.nguyenthanhdn@gmail.com" style="color: #475569; text-decoration: none; font-weight: 500;">vinh.nguyenthanhdn@gmail.com</a></p>
        </div>
    """, unsafe_allow_html=True)

def render_question_header(idx_ptr, total):
    """Render question number and progress."""
    # UI always in English
    t = lambda key: get_text('en', key)
    st.markdown(f"""
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
    <div style="display: flex; align-items: center; gap: 0.75rem;">
        <span style="font-size: 1.5rem; font-weight: 700; color: #232f3e;">{t('question')} #{idx_ptr+1}</span>
    </div>
    <span style="font-size: 0.875rem; color: #64748b; font-weight: 500;">{idx_ptr+1} {t('of')} {total}</span>
</div>
    """, unsafe_allow_html=True)

def render_question_card(question_text, is_multiselect=False):
    """Render question text card."""
    # UI always in English
    t = lambda key: get_text('en', key)
    st.markdown(
        f'<div class="question-card"><div class="question-text">{question_text.replace(chr(10), "<br>")}</div></div>', 
        unsafe_allow_html=True
    )
    
    if is_multiselect:
        st.markdown(
            f'<p style="color: #ff9900; font-weight: 600; font-size: 0.875rem; margin-bottom: 0.5rem;">{t("select_all")}</p>', 
            unsafe_allow_html=True
        )

def render_answer_feedback(ans, correct_answer):
    """Render success or error message for user answer."""
    # UI always in English
    t = lambda key: get_text('en', key)
    
    clean_ans = (ans or "").strip()
    clean_correct = (correct_answer or "").strip()
    
    correct = clean_ans == clean_correct
    
    if correct:
        st.markdown(f'''
            <div class="success-msg">
                <span style="margin-left: 0.5rem;">{t('correct')} <strong>{clean_ans}</strong></span>
            </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
            <div class="error-msg">
                <span style="margin-left: 0.5rem;">
                    {t('incorrect')} <strong>{clean_ans}</strong>. 
                    Correct answer: <strong>{clean_correct}</strong>
                </span>
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
        </script>
    """, unsafe_allow_html=True)

import streamlit.components.v1 as components

def render_scroll_to_top():
    """Scroll to the top of the page using an iframe component to ensure execution."""
    # Inject current index into HTML to make content unique and force re-render
    scroll_id = st.session_state.get('current_index', 0)
    
    components.html(f"""
        <!-- Scroll trigger for question {scroll_id} -->
        <script>
            (function() {{
                var attempts = 0;
                var maxAttempts = 2; // Reduced to avoid scroll lock
                
                function forceScrollToTop() {{
                    try {{
                        console.log("[ScrollToTop] Attempt " + attempts + " for Q{scroll_id}");
                        
                        // Access parent window (Streamlit App Context)
                        var parentDoc = window.parent.document;
                        var win = window.parent;
                        
                        // Method 0: Direct Window Scroll
                        win.scrollTo(0, 0);
                        
                        // Method 1: Target Specific Streamlit Containers
                        var selectors = [
                            '[data-testid="stMain"]', 
                            '.stMain',
                            '[data-testid="stAppViewContainer"]', 
                            '.main',
                            'section.main'
                        ];
                        
                        var scrolled = false;
                        for (var i = 0; i < selectors.length; i++) {{
                            var els = parentDoc.querySelectorAll(selectors[i]);
                            for (var j = 0; j < els.length; j++) {{
                                var el = els[j];
                                if (el && (el.scrollTop > 0 || attempts < 1)) {{ 
                                    // Only force on first attempt
                                    el.scrollTop = 0;
                                    console.log("[ScrollToTop] Scrolled " + selectors[i]);
                                    scrolled = true;
                                }}
                            }}
                        }}
                        
                        // Method 2: Fallback to document properties
                        parentDoc.documentElement.scrollTop = 0;
                        parentDoc.body.scrollTop = 0;
                        
                        attempts++;
                        if (attempts < maxAttempts) {{
                            setTimeout(forceScrollToTop, 150); // Quick retry only
                        }}
                        
                    }} catch (e) {{
                        console.log("[ScrollToTop] Error accessing parent: " + e);
                    }}
                }}
                
                // Execute immediately
                setTimeout(forceScrollToTop, 50);
            }})();
        </script>
    """, height=0, width=0)

def render_ai_explanation(question_id, explanation_text, discussion_link=None, auto_scroll=False):
    """Render AI explanation section with optional auto-scroll."""
    # UI always in English
    t = lambda key: get_text('en', key)
    st.markdown(f'<div id="explanation-{question_id}"></div>', unsafe_allow_html=True)
    with st.expander(t('ai_analysis_title'), expanded=True):
        st.markdown(explanation_text)
        if discussion_link:
            st.caption(f"[{t('see_discussion')}]({discussion_link})")
        
        if auto_scroll:
            st.markdown(f'<script>scrollToElementWithRetry("explanation-{question_id}");</script>', unsafe_allow_html=True)

def render_ai_theory(question_id, theory_text, auto_scroll=False):
    """Render AI theory section with optional auto-scroll."""
    # UI always in English
    t = lambda key: get_text('en', key)
    st.markdown(f'<div id="theory-{question_id}"></div>', unsafe_allow_html=True)
    with st.expander(t('ai_theory_title'), expanded=True):
        st.markdown(theory_text)
        
        if auto_scroll:
            st.markdown(f'<script>scrollToElementWithRetry("theory-{question_id}");</script>', unsafe_allow_html=True)

def render_navigation_buttons(idx_ptr, total, on_prev, on_next, on_jump):
    """Render navigation buttons (Previous, Jump, Next)."""
    # UI always in English
    t = lambda key: get_text('en', key)
    st.divider()
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c1:
        if st.button(t('btn_previous'), use_container_width=True):
            on_prev()
            
    with c2:
        # Center the input and button
        # Using columns [3, 2, 1, 3] to create padding on sides and keep input/btn close in center
        _, mid_input, mid_btn, _ = st.columns([3, 2, 1, 3])
        
        with mid_input:
            new_val = st.number_input(
                t('go_to_question'), 
                min_value=1, 
                max_value=total, 
                value=idx_ptr+1, 
                label_visibility="collapsed"
            )
            if new_val != idx_ptr + 1:
                on_jump(new_val - 1)
                
        with mid_btn:
            if st.button(t('btn_go'), use_container_width=True):
                pass  # Logic handled by number_input
                    
    with c3:
        if st.button(t('btn_next'), use_container_width=True):
            on_next()
