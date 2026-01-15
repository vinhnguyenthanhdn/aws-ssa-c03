import streamlit as st
import json
import time
from pathlib import Path

import os

# Import custom modules
from page_setup import setup_page_config, inject_seo, hide_streamlit_branding, load_custom_css
from ai_service import init_ai_session_state, get_ai_explanation, get_ai_theory
from ui_components import (
    render_page_header, render_question_header, render_question_card,
    render_answer_feedback, render_auto_scroll_script, render_ai_explanation,
    render_ai_theory, render_navigation_buttons, render_language_selector,
    render_footer, render_scroll_to_top
)
from parser_service import parse_markdown_file

# Setup page configuration
setup_page_config()
inject_seo()
hide_streamlit_branding()
load_custom_css()

@st.cache_data
def load_data(mtime):
    """Handles file loading logic. Cache invalidated if mtime changes."""
    fpath = Path(__file__).parent / "SAA_C03.md"
    if fpath.exists():
        content = fpath.read_text(encoding='utf-8')
        return parse_markdown_file(content)
    return None

def init_session_state(localS):
    """Initialize all session state variables."""
    # Load state from Local Storage/URL if session is fresh
    if 'data_loaded' not in st.session_state:
        # Restore Index from URL Query Params
        try:
            qp = st.query_params
            q_idx = int(qp.get("q", 1)) - 1
            st.session_state.current_index = max(0, q_idx)
        except:
            st.session_state.current_index = 0
             
        # Restore Answers from Local Storage
        try:
            saved_ans = localS.getItem("saa_c03_user_answers")
            if saved_ans:
                st.session_state.user_answers = json.loads(saved_ans)
        except:
            pass
            
        st.session_state.data_loaded = True

    # Ensure Session State Initialization
    if 'current_index' not in st.session_state: 
        st.session_state.current_index = 0
    if 'user_answers' not in st.session_state: 
        st.session_state.user_answers = {}
    if 'question_order' not in st.session_state: 
        st.session_state.question_order = []
    if 'active_ai_section' not in st.session_state:
        st.session_state.active_ai_section = None  # Can be 'theory', 'explanation', or None
    if 'language' not in st.session_state:
        st.session_state.language = 'vi'  # Default to Vietnamese
    if 'scroll_to_top' not in st.session_state:
        st.session_state.scroll_to_top = False
    if 'is_loading_ai' not in st.session_state:
        st.session_state.is_loading_ai = False  # Track if AI is currently loading
    
    # Initialize AI session state
    init_ai_session_state()

def handle_navigation(idx_ptr, total_indices, total_questions):
    """Handle navigation button clicks."""
    def on_prev():
        if st.session_state.current_index > 0:
            st.session_state.current_index -= 1
            st.session_state.scroll_to_top = True
            st.query_params["q"] = str(st.session_state.current_index + 1)
            st.rerun()
    
    def on_next():
        if st.session_state.current_index < total_questions - 1:
            st.session_state.current_index += 1
            st.session_state.scroll_to_top = True
            st.query_params["q"] = str(st.session_state.current_index + 1)
            st.rerun()
    
    def on_jump(new_idx):
        st.session_state.current_index = new_idx
        st.session_state.scroll_to_top = True
        st.query_params["q"] = str(st.session_state.current_index + 1)
        st.rerun()
    
    render_navigation_buttons(idx_ptr, total_indices, on_prev, on_next, on_jump)

def get_current_question_index(questions):
    """Determine current question index."""
    indices = st.session_state.question_order
    idx_ptr = st.session_state.current_index
    real_idx = indices[idx_ptr]
    
    return indices, idx_ptr, real_idx

def render_question_form(q, localS):
    """Render the question form and handle submissions."""
    # Get language for AI generation (User preference)
    ai_lang = st.session_state.get('language', 'vi')
    
    # UI always in English
    from translations import get_text
    t = lambda key: get_text('en', key)
    
    with st.form(key=f"q_{q['id']}"):
        user_ch = []
        
        # Render options
        if q['is_multiselect']:
            for opt in q['options']:
                if st.checkbox(opt):
                    user_ch.append(opt.split('.')[0])
        else:
            sel = st.radio(t('select_answer'), q['options'], index=None, label_visibility="collapsed")
            if sel:
                user_ch.append(sel.split('.')[0])
        
        
        # Action buttons
        f1, f2, f3 = st.columns([1, 1, 1])
        
        with f1:
            theory_req = st.form_submit_button(t('btn_theory'), use_container_width=True)
        with f2:
            explain_req = st.form_submit_button(t('btn_explain'), use_container_width=True)
        with f3:
            sub = st.form_submit_button(t('btn_submit'), type="primary", use_container_width=True)
    
    # Handle answer submission
    if sub and user_ch:
        ans = "".join(sorted(user_ch))
        st.session_state.user_answers[q['id']] = ans
        localS.setItem("saa_c03_user_answers", json.dumps(st.session_state.user_answers))
    
    return theory_req, explain_req

def main():
    # Import here to avoid module load errors
    from streamlit_local_storage import LocalStorage
    
    # Initialize Local Storage
    localS = LocalStorage()
    init_session_state(localS)
    
    # Handle Scroll To Top
    if st.session_state.get('scroll_to_top', False):
        render_scroll_to_top()
        st.session_state.scroll_to_top = False
    
    # Load questions
    fpath = Path(__file__).parent / "SAA_C03.md"
    mtime = os.path.getmtime(fpath) if fpath.exists() else 0
    questions = load_data(mtime)
    from translations import get_text
    
    if questions is None:
        # UI English
        st.header(get_text('en', 'settings'))
        uploaded = st.file_uploader(get_text('en', 'upload_file'), type=["md"])
        if uploaded:
            content = uploaded.getvalue().decode("utf-8")
            questions = parse_markdown_file(content)
        else:
            st.stop()
    total = len(questions)
    
    # Init question order
    if len(st.session_state.question_order) != total:
        st.session_state.question_order = list(range(total))
    
    # Render UI headers
    render_language_selector()  # Add language selector at the top
    render_page_header()
    
    # Check Drive Configuration
    if "GDRIVE_FOLDER_ID" not in st.secrets:
        st.warning("⚠️ **Lưu ý:** Bạn chưa cấu hình `GDRIVE_FOLDER_ID`. File cache đang được lưu trong bộ nhớ riêng của Bot (bạn sẽ không thấy trên Drive). Vui lòng thêm Folder ID vào Secrets.", icon="📂")
    
    # Get current question
    indices, idx_ptr, real_idx = get_current_question_index(questions)
    q = questions[real_idx]
    
    # Render question header
    render_question_header(idx_ptr, len(indices))
    
    with st.container():
        render_question_card(q["question"], q['is_multiselect'])
        
        # Only render form if not currently loading AI content
        if not st.session_state.is_loading_ai:
            # Render form and handle actions
            theory_req, explain_req = render_question_form(q, localS)
        else:
            theory_req = False
            explain_req = False
        
        # Handle AI Requests (Moved from render_question_form to fix UI issues)
        if theory_req or explain_req:
            # Determine lang for AI content
            ai_lang = st.session_state.get('language', 'vi')
            
            if theory_req:
                # Set loading flag and pending request type, then rerun to hide form
                st.session_state.is_loading_ai = True
                st.session_state.pending_ai_request = 'theory'
                st.rerun()
            
            if explain_req:
                # Set loading flag and pending request type, then rerun to hide form
                st.session_state.is_loading_ai = True
                st.session_state.pending_ai_request = 'explanation'
                st.rerun()
        
        # Handle AI loading state (after rerun with is_loading_ai = True)
        if st.session_state.is_loading_ai:
            ai_lang = st.session_state.get('language', 'vi')
            theory_cache_key = f"{q['id']}_{ai_lang}"
            explanation_cache_key = f"{q['id']}_{ai_lang}"
            pending_request = st.session_state.get('pending_ai_request')
            
            if pending_request == 'theory':
                with st.status(get_text('en', 'loading_theory'), expanded=True) as status:
                    start_time = time.time()
                    if theory_cache_key not in st.session_state.theories:
                        opts_text = "\n".join(q['options'])
                        st.session_state.theories[theory_cache_key] = get_ai_theory(q['question'], opts_text, q['id'], ai_lang)
                    elapsed = time.time() - start_time
                    if elapsed < 1.0: time.sleep(1.0 - elapsed)
                    status.update(label="✅ Done!", state="complete")
                st.session_state.active_ai_section = 'theory'
                
            elif pending_request == 'explanation':
                with st.status(get_text('en', 'loading_explanation'), expanded=True) as status:
                    start_time = time.time()
                    if explanation_cache_key not in st.session_state.explanations:
                        opts_text = "\n".join(q['options'])
                        explanation = get_ai_explanation(q['question'], opts_text, q['correct_answer'], q['id'], ai_lang)
                        st.session_state.explanations[explanation_cache_key] = explanation
                    elapsed = time.time() - start_time
                    if elapsed < 1.0: time.sleep(1.0 - elapsed)
                    status.update(label="✅ Done!", state="complete")
                st.session_state.active_ai_section = 'explanation'
            
            # Clear loading state and pending request
            st.session_state.is_loading_ai = False
            st.session_state.pending_ai_request = None
            time.sleep(0.3)  # Brief pause to show completion status
            st.rerun()
        
        # Display answer feedback
        ans = st.session_state.user_answers.get(q['id'])
        if ans:
            render_answer_feedback(ans, q['correct_answer'])
        
        # Render auto-scroll script
        render_auto_scroll_script()
        
        # Get current language for cache keys
        lang = st.session_state.get('language', 'vi')
        theory_cache_key = f"{q['id']}_{lang}"
        explanation_cache_key = f"{q['id']}_{lang}"
        
        # Only display one AI section at a time based on active_ai_section
        # Display AI explanation (only if active)
        if explanation_cache_key in st.session_state.explanations and st.session_state.active_ai_section == 'explanation':
            render_ai_explanation(
                q['id'],
                st.session_state.explanations[explanation_cache_key],
                q.get('discussion_link'),
                auto_scroll=explain_req
            )
        
        # Display AI theory (only if active)
        if theory_cache_key in st.session_state.theories and st.session_state.active_ai_section == 'theory':
            render_ai_theory(
                q['id'],
                st.session_state.theories[theory_cache_key],
                auto_scroll=theory_req
            )
    
    # Navigation
    handle_navigation(idx_ptr, len(indices), total)
    
    # Render Footer
    render_footer()

if __name__ == "__main__":
    main()
