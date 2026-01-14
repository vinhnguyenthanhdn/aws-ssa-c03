import streamlit as st
import random
import json
from pathlib import Path

# Import custom modules
from config import setup_page_config, inject_seo, hide_streamlit_branding, load_custom_css
from ai_service import init_ai_session_state, get_ai_explanation, get_ai_theory
from ui_components import (
    render_page_header, render_question_header, render_question_card,
    render_answer_feedback, render_auto_scroll_script, render_ai_explanation,
    render_ai_theory, render_navigation_buttons, render_sidebar_tools,
    render_language_selector
)
from quiz_parser import parse_markdown_file

# Setup page configuration
setup_page_config()
inject_seo()
hide_streamlit_branding()
load_custom_css()

@st.cache_data
def load_data():
    """Handles file loading logic."""
    fpath = Path(__file__).parent / "SAA_C03.md"
    if fpath.exists():
        return fpath.read_text(encoding='utf-8')
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
    if 'random_mode' not in st.session_state: 
        st.session_state.random_mode = False
    if 'question_order' not in st.session_state: 
        st.session_state.question_order = []
    if 'active_ai_section' not in st.session_state:
        st.session_state.active_ai_section = None  # Can be 'theory', 'explanation', or None
    if 'language' not in st.session_state:
        st.session_state.language = 'vi'  # Default to Vietnamese
    
    # Initialize AI session state
    init_ai_session_state()

def handle_navigation(is_search, idx_ptr, total_indices, total_questions):
    """Handle navigation button clicks."""
    def on_prev():
        if is_search and st.session_state.search_idx > 0:
            st.session_state.search_idx -= 1
            st.rerun()
        elif not is_search and st.session_state.current_index > 0:
            st.session_state.current_index -= 1
            st.query_params["q"] = str(st.session_state.current_index + 1)
            st.rerun()
    
    def on_next():
        if is_search and st.session_state.search_idx < total_indices - 1:
            st.session_state.search_idx += 1
            st.rerun()
        elif not is_search and st.session_state.current_index < total_questions - 1:
            st.session_state.current_index += 1
            st.query_params["q"] = str(st.session_state.current_index + 1)
            st.rerun()
    
    def on_jump(new_idx):
        if is_search:
            st.session_state.search_idx = new_idx
        else:
            st.session_state.current_index = new_idx
            st.query_params["q"] = str(st.session_state.current_index + 1)
        st.rerun()
    
    render_navigation_buttons(idx_ptr, total_indices, is_search, on_prev, on_next, on_jump)

def handle_sidebar(questions, localS):
    """Handle sidebar rendering and actions."""
    total = len(questions)
    
    with st.sidebar:
        search, shuffle_clicked, reset_clicked = render_sidebar_tools(
            total, 
            len(st.session_state.user_answers)
        )
        
        # Handle shuffle
        if shuffle_clicked:
            st.session_state.random_mode = True
            random.shuffle(st.session_state.question_order)
            st.session_state.current_index = 0
            st.rerun()
        
        # Handle reset
        if reset_clicked:
            st.session_state.random_mode = False
            st.session_state.question_order = list(range(total))
            st.session_state.current_index = 0
            st.session_state.user_answers = {}
            st.rerun()
    
    return search

def get_current_question_index(search, questions):
    """Determine current question index based on search state."""
    indices = st.session_state.question_order
    is_search = False
    
    if search:
        indices = [
            i for i in st.session_state.question_order 
            if search.lower() in questions[i]['question'].lower() 
            or search in questions[i]['id']
        ]
        if not indices:
            from translations import get_text
            lang = st.session_state.get('language', 'vi')
            st.warning(get_text(lang, 'no_matches'))
            st.stop()
        
        if 'search_query' not in st.session_state or st.session_state.search_query != search:
            st.session_state.search_query = search
            st.session_state.search_idx = 0
        
        idx_ptr = st.session_state.search_idx if st.session_state.search_idx < len(indices) else 0
        real_idx = indices[idx_ptr]
        is_search = True
    else:
        idx_ptr = st.session_state.current_index
        real_idx = indices[idx_ptr]
    
    return indices, idx_ptr, real_idx, is_search

def render_question_form(q, localS):
    """Render the question form and handle submissions."""
    # Get language and translations at the beginning
    from translations import get_text
    lang = st.session_state.get('language', 'vi')
    t = lambda key: get_text(lang, key)
    
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
    
    # Get current language
    lang = st.session_state.get('language', 'vi')
    from translations import get_text
    t = lambda key: get_text(lang, key)
    
    # Handle theory request
    if theory_req:
        if q['id'] not in st.session_state.theories:
            with st.spinner(t('loading_theory')):
                opts_text = "\n".join(q['options'])
                st.session_state.theories[q['id']] = get_ai_theory(q['question'], opts_text, q['id'], lang)
        # Set active section to theory, hide explanation
        st.session_state.active_ai_section = 'theory'
    
    # Handle explanation request
    if explain_req:
        if q['id'] not in st.session_state.explanations:
            with st.spinner(t('loading_explanation')):
                opts_text = "\n".join(q['options'])
                explanation = get_ai_explanation(q['question'], opts_text, q['correct_answer'], q['id'], lang)
                st.session_state.explanations[q['id']] = explanation
        # Set active section to explanation, hide theory
        st.session_state.active_ai_section = 'explanation'
    
    return theory_req, explain_req

def main():
    # Import here to avoid module load errors
    from streamlit_local_storage import LocalStorage
    
    # Initialize Local Storage
    localS = LocalStorage()
    init_session_state(localS)
    
    # Load questions
    content = load_data()
    from translations import get_text
    lang = st.session_state.get('language', 'vi')
    
    if not content:
        with st.sidebar:
            st.header(get_text(lang, 'settings'))
            uploaded = st.file_uploader(get_text(lang, 'upload_file'), type=["md"])
            if uploaded:
                content = uploaded.getvalue().decode("utf-8")
            else:
                st.stop()
    
    questions = parse_markdown_file(content)
    total = len(questions)
    
    # Init question order
    if len(st.session_state.question_order) != total:
        st.session_state.question_order = list(range(total))
    
    # Handle sidebar
    search = handle_sidebar(questions, localS)
    
    # Get current question
    indices, idx_ptr, real_idx, is_search = get_current_question_index(search, questions)
    q = questions[real_idx]
    
    # Render UI
    render_language_selector()  # Add language selector at the top
    render_page_header()
    render_question_header(idx_ptr, len(indices))
    
    with st.container():
        render_question_card(q["question"], q['is_multiselect'])
        
        # Render form and handle actions
        theory_req, explain_req = render_question_form(q, localS)
        
        # Display answer feedback
        ans = st.session_state.user_answers.get(q['id'])
        if ans:
            render_answer_feedback(ans, q['correct_answer'])
        
        # Render auto-scroll script
        render_auto_scroll_script()
        
        # Only display one AI section at a time based on active_ai_section
        # Display AI explanation (only if active)
        if q['id'] in st.session_state.explanations and st.session_state.active_ai_section == 'explanation':
            render_ai_explanation(
                q['id'],
                st.session_state.explanations[q['id']],
                q.get('discussion_link'),
                auto_scroll=explain_req
            )
        
        # Display AI theory (only if active)
        if q['id'] in st.session_state.theories and st.session_state.active_ai_section == 'theory':
            render_ai_theory(
                q['id'],
                st.session_state.theories[q['id']],
                auto_scroll=theory_req
            )
    
    # Navigation
    handle_navigation(is_search, idx_ptr, len(indices), total)

if __name__ == "__main__":
    main()
