import streamlit as st
import re
import random
import os
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="Professional Prep | AWS SAA-C03",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Bright & Beautiful" UI
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global styles */
    .stApp {
        background-color: #f3f4f6; /* Light gray background */
        color: #1f2937;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: #111827;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
    }
    
    /* Card-like container for the question */
    .question-card {
        background-color: #ffffff;
        padding: 2.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 2rem;
        border: 1px solid #e5e7eb;
    }
    
    /* Text Question Style */
    .question-text {
        font-size: 1.15rem;
        font-weight: 500;
        line-height: 1.7;
        color: #374151;
        margin-bottom: 1.5rem;
    }
    
    /* Option styling - handled by widgets but adding container spacing */
    .stRadio, .stCheckbox {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #f3f4f6;
        transition: all 0.2s;
        margin-bottom: 0.5rem;
    }
    
    .stRadio:hover, .stCheckbox:hover {
        background-color: #f9fafb;
        border-color: #d1d5db;
    }
    
    /* Success/Error messages */
    .success-msg {
        background-color: #ecfdf5;
        color: #047857;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid #a7f3d0;
        margin-top: 1rem;
        font-weight: 500;
        display: flex;
        align-items: center;
    }
    
    .error-msg {
        background-color: #fef2f2;
        color: #b91c1c;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid #fecaca;
        margin-top: 1rem;
        font-weight: 500;
        display: flex;
        align-items: center;
    }
    
    /* Sidebar customization */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }
    div[data-testid="stSidebarNav"] {
        padding-top: 1rem;
    }
    
    /* Button Customization */
    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        border: none;
        transition: transform 0.1s;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    div.stButton > button:active {
        transform: scale(0.98);
    }

    /* Highlight the Correct Answer in Explanation */
    .highlight-answer {
        background-color: #fef3c7;
        color: #d97706;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-weight: bold;
    }
    
    /* Tags for metadata */
    .meta-tag {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 1rem;
    }
    .topic-tag {
        background-color: #e0e7ff;
        color: #4338ca;
    }
    .id-tag {
        background-color: #e5e7eb;
        color: #374151;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Parsing Logic
# -----------------------------------------------------------------------------

@st.cache_data
def parse_markdown_file(content):
    """
    Parses the Markdown content into a list of question dictionaries.
    Optimized with Regex for performance.
    """
    questions = []
    
    # Split by separator
    # The file uses '----------------------------------------'
    blocks = content.split('----------------------------------------')
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
            
        # 1. Extract Question ID
        # Format: ## Exam AWS ... question [ID] discussion
        id_match = re.search(r'## Exam .* question (\d+) discussion', block)
        if not id_match:
            continue
        q_id = id_match.group(1)
        
        # 2. Extract Official Answer
        # Format: **Answer: [Letters]**
        # Sometimes there might be whitespace
        answer_match = re.search(r'\*\*Answer:\s+([A-Z]+)\*\*', block)
        correct_answer = answer_match.group(1) if answer_match else None
        
        # 3. Extract Topic # (Optional, for context)
        topic_match = re.search(r'Topic #:\s+(\d+)', block)
        topic_id = topic_match.group(1) if topic_match else "Unknown"
        
        # 4. Extract Discussion Link
        link_match = re.search(r'\[View on ExamTopics\]\((.*?)\)', block)
        discussion_link = link_match.group(1) if link_match else None
        
        # 5. Extract Options (A., B., C., etc.)
        # We look for lines starting with A. or A) etc, but spec says A.
        option_pattern = re.compile(r'^([A-F])\.\s+(.*)', re.MULTILINE)
        options_matches = list(option_pattern.finditer(block))
        
        options = []
        if options_matches:
            first_option_start_index = options_matches[0].start()
            for m in options_matches:
                options.append(f"{m.group(1)}. {m.group(2)}")
        else:
            first_option_start_index = len(block) # Fallback if no options found
        
        # 6. Extract Question Body
        # Text between metadata end and first option
        # Metadata end is usually "[All AWS ... Questions]"
        # or checking lines.
        
        lines = block.split('\n')
        
        # Find where metadata ends
        meta_end_idx = 0
        for i, line in enumerate(lines):
            if "[All AWS Certified Solutions Architect" in line:
                meta_end_idx = i + 1
                break
        
        # Find where options start
        option_start_line_idx = len(lines)
        for i in range(meta_end_idx, len(lines)):
            if re.match(r'^[A-F]\.\s+', lines[i]):
                option_start_line_idx = i
                break
        
        raw_body_lines = lines[meta_end_idx:option_start_line_idx]
        
        # Clean up body lines
        clean_body = []
        suggested_answer = None
        
        for line in raw_body_lines:
            s_line = line.strip()
            if not s_line:
                continue
            # Extract Suggested Answer if present
            if s_line.startswith("Suggested Answer:"):
                suggested_answer = s_line
                continue
            if s_line.startswith("Question #") or s_line.startswith("Topic #"):
                continue
            if s_line.startswith("Exam question from"):
                continue
            if "Amazon's" == s_line or "AWS Certified Solutions" in s_line:
                 continue
            
            clean_body.append(s_line)
            
        question_text = "\n".join(clean_body)
        
        # 7. Determine parsing mode (Multi-select)
        is_multiselect = False
        if "(Choose two)" in question_text or "(Choose two.)" in question_text:
            is_multiselect = True
            expected_count = 2
        elif "(Choose three)" in question_text or "(Choose three.)" in question_text:
            is_multiselect = True
            expected_count = 3
        else:
            expected_count = 1
            
        questions.append({
            "id": q_id,
            "topic": topic_id,
            "question": question_text,
            "options": options,
            "correct_answer": correct_answer, 
            "suggested_answer_text": suggested_answer,
            "discussion_link": discussion_link,
            "is_multiselect": is_multiselect,
            "expected_count": expected_count
        })
        
    return questions

# -----------------------------------------------------------------------------
# Main App Logic
# -----------------------------------------------------------------------------

def main():
    # -----------------------------------------------------------
    # Sidebar: Settings & Nav
    # -----------------------------------------------------------
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # --- File Loading (Cloud Optimized) ---
        default_filename = "SAA_C03.md"
        # Look for file in the same directory as this script
        file_path = Path(__file__).parent / default_filename
        
        data_content = None
        
        if file_path.exists():
            st.success(f"✅ Loaded: {default_filename}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data_content = f.read()
            except Exception as e:
                st.error(f"Error reading file: {e}")
        else:
            st.warning(f"File `{default_filename}` not found locally.")
            uploaded_file = st.file_uploader("Upload .md file", type=["md"])
            if uploaded_file is not None:
                data_content = uploaded_file.getvalue().decode("utf-8")
        
        if not data_content:
            st.info("System expects `SAA_C03.md` in the directory.")
            st.stop()
            
        # Parse Data
        try:
            questions = parse_markdown_file(data_content)
        except Exception as e:
            st.error(f"Error parsing file: {e}")
            st.stop()
            
        total_questions = len(questions)
        st.markdown(f"**Total Questions:** {total_questions}")
        
        # Initialize Session State
        if 'current_index' not in st.session_state:
            st.session_state.current_index = 0
        if 'user_answers' not in st.session_state:
            st.session_state.user_answers = {} 
        if 'question_order' not in st.session_state:
            st.session_state.question_order = list(range(total_questions))
        if 'random_mode' not in st.session_state:
            st.session_state.random_mode = False

        # Reset check
        if len(st.session_state.question_order) != total_questions:
             st.session_state.question_order = list(range(total_questions))
        
        st.divider()
        
        # --- Tools ---
        st.subheader("Tools")
        search_query = st.text_input("🔍 Search Keyword")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔀 Shuffle", use_container_width=True):
                st.session_state.random_mode = True
                random.shuffle(st.session_state.question_order)
                st.session_state.current_index = 0
                st.rerun()
        with col2:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.random_mode = False
                st.session_state.question_order = list(range(total_questions))
                st.session_state.current_index = 0
                st.session_state.user_answers = {}
                st.rerun()

        q_num = st.number_input("Go to Question #", min_value=1, max_value=total_questions, value=1)
        if st.button("Jump", use_container_width=True):
             # Logic to jump to specific question index
             # Note: This jumps to the Nth question in the CURRENT order (shuffled or not)
             # To jump to specific ID would require lookup, but Nth is standard for "Go to page X"
             st.session_state.current_index = q_num - 1
             st.rerun()

        # Progress
        answered_count = len(st.session_state.user_answers)
        st.markdown(f"**Progress:** {answered_count} / {total_questions}")
        st.progress(min(answered_count / total_questions, 1.0))

    # -----------------------------------------------------------
    # Main Content
    # -----------------------------------------------------------
    
    # 1. Title Section
    st.title("☁️ AWS Solutions Architect Associate")
    st.markdown("Master the SAA-C03 exam with this interactive practice tool.")
    st.divider()

    # 2. Filtering/Search Logic
    filtered_indices = st.session_state.question_order
    is_search_mode = False
    
    if search_query:
        filtered_indices = [
            i for i in st.session_state.question_order 
            if search_query.lower() in questions[i]['question'].lower() 
            or search_query.lower() in str(questions[i]['id'])
        ]
        
        if not filtered_indices:
            st.warning("No questions found matching your query.")
            st.stop()
            
        if 'search_query' not in st.session_state or st.session_state.search_query != search_query:
            st.session_state.search_query = search_query
            st.session_state.search_index = 0
            
        display_idx = st.session_state.search_index
        if display_idx >= len(filtered_indices):
            display_idx = 0
            st.session_state.search_index = 0
            
        actual_index = filtered_indices[display_idx]
        is_search_mode = True
        total_in_view = len(filtered_indices)
    else:
        # Normal Mode
        if st.session_state.current_index >= len(st.session_state.question_order):
            st.session_state.current_index = 0
            
        actual_index = st.session_state.question_order[st.session_state.current_index]
        display_idx = st.session_state.current_index
        is_search_mode = False
        total_in_view = total_questions
        if 'search_query' in st.session_state:
            del st.session_state['search_query']

    question_data = questions[actual_index]
    
    # 3. Question Display
    # Metadata Badge
    st.markdown(f"""
    <div>
        <span class="meta-tag id-tag">Question #{question_data['id']}</span>
        <span class="meta-tag topic-tag">Topic {question_data['topic']}</span>
        <span class="meta-tag" style="background-color: #f3f4f6; color: #6b7280; float: right;">
            {display_idx + 1} / {total_in_view}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Card
    with st.container():
        st.markdown(f"""
        <div class="question-card">
            <div class="question-text">
                {question_data['question'].replace(chr(10), '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Options Form
        with st.form(key=f"q_form_{question_data['id']}"):
            user_choice = []
            
            # Label
            st.markdown(f"**Select Answer ({'Multiple Choice' if question_data['is_multiselect'] else 'Single Choice'}):**")
            
            if question_data['is_multiselect']:
                for opt in question_data['options']:
                    is_checked = st.checkbox(opt)
                    if is_checked:
                        letter = opt.split('.')[0]
                        user_choice.append(letter)
            else:
                radio_val = st.radio(
                    "Select an answer:",
                    question_data['options'],
                    index=None,
                    label_visibility="collapsed",
                    key=f"radio_{question_data['id']}"
                )
                if radio_val:
                    user_choice.append(radio_val.split('.')[0])
            
            st.markdown("---")
            submit_btn = st.form_submit_button("Submit Answer", type="primary")
            
        # Feedback Section
        feedback_placeholder = st.empty()
        already_answered = st.session_state.user_answers.get(question_data['id'])
        show_answer = False
        
        if submit_btn:
             if not user_choice:
                 st.warning("⚠️ Please select an option.")
             else:
                 user_choice.sort()
                 user_val = "".join(user_choice)
                 st.session_state.user_answers[question_data['id']] = user_val
                 already_answered = user_val
        
        if already_answered:
            correct_val = question_data['correct_answer'] or ""
            is_correct = (already_answered == correct_val)
            
            if is_correct:
                feedback_placeholder.markdown(f"""
                <div class="success-msg">
                    ✅ Correct! Output: {already_answered}
                </div>
                """, unsafe_allow_html=True)
            else:
                feedback_placeholder.markdown(f"""
                <div class="error-msg">
                    ❌ Incorrect. Your answer: {already_answered}
                </div>
                """, unsafe_allow_html=True)
            show_answer = True

    # 4. Explanation Section (Expanded)
    if show_answer or st.session_state.user_answers.get(question_data['id']):
        with st.expander("📘 View Official Answer & Discussion", expanded=True):
            st.markdown(f"#### Official Answer: <span class='highlight-answer'>{question_data['correct_answer']}</span>", unsafe_allow_html=True)
            
            if question_data['suggested_answer_text']:
                 st.info(f"**Community Vote/Suggestion:** {question_data['suggested_answer_text']}")
            
            if question_data['discussion_link']:
                st.markdown(f"[🔗 Open Discussion on ExamTopics]({question_data['discussion_link']})")

    # 5. Nav Buttons
    st.markdown("<br>", unsafe_allow_html=True)
    col_prev, _, col_next = st.columns([1, 2, 1])
    
    with col_prev:
        if st.button("⬅️ Previous", use_container_width=True):
            if is_search_mode:
                if st.session_state.search_index > 0:
                    st.session_state.search_index -= 1
                    st.rerun()
            else:
                if st.session_state.current_index > 0:
                    st.session_state.current_index -= 1
                    st.rerun()
                    
    with col_next:
        if st.button("Next ➡️", use_container_width=True):
             if is_search_mode:
                if st.session_state.search_index < len(filtered_indices) - 1:
                    st.session_state.search_index += 1
                    st.rerun()
             else:
                if st.session_state.current_index < total_questions - 1:
                    st.session_state.current_index += 1
                    st.rerun()

if __name__ == "__main__":
    main()
