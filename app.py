import streamlit as st
import re
import random
import os

# Set page config
st.set_page_config(
    page_title="AWS SAA-C03 Quiz App",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for aesthetics
st.markdown("""
<style>
    /* Global styles */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    /* Card-like container for the question */
    .question-card {
        background-color: #1f2937;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 2rem;
        border: 1px solid #374151;
    }
    
    /* Text Question Style */
    .question-text {
        font-size: 1.25rem;
        font-weight: 500;
        line-height: 1.6;
        color: #e5e7eb;
        margin-bottom: 1.5rem;
    }
    
    /* Option styling handled by Streamlit widgets, but we can add spacing */
    .stRadio, .stCheckbox {
        margin-bottom: 0.5rem;
    }
    
    /* Success/Error messages */
    .success-msg {
        background-color: rgba(16, 185, 129, 0.2);
        color: #34d399;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #059669;
        margin-top: 1rem;
    }
    
    .error-msg {
        background-color: rgba(239, 68, 68, 0.2);
        color: #f87171;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #b91c1c;
        margin-top: 1rem;
    }
    
    /* Sidebar customization */
    section[data-testid="stSidebar"] {
        background-color: #111827;
    }
    
    /* Highlight the Correct Answer in Explanation */
    .highlight-answer {
        font-weight: bold;
        color: #fbbf24;
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
        
        # Split block into lines to find regions
        lines = block.split('\n')
        
        # Find where metadata ends
        meta_end_idx = 0
        for i, line in enumerate(lines):
            if "[All AWS Certified Solutions Architect" in line:
                meta_end_idx = i + 1
                break
        
        # Find where options start (based on index in the raw string, or just scanning lines again)
        # Using the character index is safer if we just slice the string, but line processing is easier for "Suggested Answer" removal.
        # Let's use lines.
        
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
                # Format: Suggested Answer: C 🗳️ 
                suggested_answer = s_line
                continue
            if s_line.startswith("Question #") or s_line.startswith("Topic #"):
                continue
            if s_line.startswith("Exam question from"):
                continue
            if "Amazon's" == s_line or "AWS Certified Solutions" in s_line:
                 # heuristic to skip header leftovers if meta_end_idx missed
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
            "correct_answer": correct_answer, # e.g. "BE" or "B"
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
    st.title("☁️ AWS SAA-C03 Exam Prep")
    
    # Initialize Session State
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {} # Map q_id -> user_selection
    if 'random_mode' not in st.session_state:
        st.session_state.random_mode = False
    if 'question_order' not in st.session_state:
        st.session_state.question_order = []
    
    # -----------------------------------------------------------
    # Sidebar: Data Loading & Navigation
    # -----------------------------------------------------------
    with st.sidebar:
        st.header("Settings")
        
        # File Source
        local_file_path = "/Users/vinh/Documents/Project/aws-ssa-c03/SAA_C03.md"
        data_content = None
        
        # Text to indicate source
        if os.path.exists(local_file_path):
            st.success(f"Loaded local file: SAA_C03.md")
            try:
                with open(local_file_path, 'r', encoding='utf-8') as f:
                    data_content = f.read()
            except Exception as e:
                st.error(f"Error reading file: {e}")
        
        # Fallback Uploader
        uploaded_file = st.file_uploader("Or upload .md file", type=["md"])
        if uploaded_file is not None:
            stringio = uploaded_file.getvalue().decode("utf-8")
            data_content = stringio
            
        if not data_content:
            st.warning("Please upload a file or ensure SAA_C03.md is in the directory.")
            st.stop()
            
        # Parse Data
        try:
            questions = parse_markdown_file(data_content)
        except Exception as e:
            st.error(f"Error parsing file: {e}")
            st.stop()
            
        total_questions = len(questions)
        st.markdown(f"**Total Questions:** {total_questions}")
        
        # Init question order if needed
        if len(st.session_state.question_order) != total_questions:
             st.session_state.question_order = list(range(total_questions))
        
        st.divider()
        
        # Tools
        st.subheader("Tools")
        
        # Search
        search_query = st.text_input("🔍 Search Keyword")
        
        # Navigation
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔀 Shuffle"):
                st.session_state.random_mode = True
                random.shuffle(st.session_state.question_order)
                st.session_state.current_index = 0
                st.rerun()
        with col2:
            if st.button("🔄 Reset"):
                st.session_state.random_mode = False
                st.session_state.question_order = list(range(total_questions))
                st.session_state.current_index = 0
                st.session_state.user_answers = {}
                st.rerun()

        # Jump to Question
        q_num = st.number_input("Jump to Q#", min_value=1, max_value=total_questions, value=1)
        if st.button("Go"):
            # Find index of this question number in the current order? 
            # Or just jump to that absolute index? 
            # Usually "Jump to Q#" implies absolute index/ID order, but strict index is easier.
            st.session_state.current_index = q_num - 1
            st.rerun()

        # Progress
        answered_count = len(st.session_state.user_answers)
        st.write(f"**Progress:** {answered_count} / {total_questions}")
        st.progress(min(answered_count / total_questions, 1.0))

    # -----------------------------------------------------------
    # Filter Logic (Search)
    # -----------------------------------------------------------
    filtered_indices = st.session_state.question_order
    
    if search_query:
        # Filter indices based on query
        filtered_indices = [
            i for i in st.session_state.question_order 
            if search_query.lower() in questions[i]['question'].lower() 
            or search_query.lower() in str(questions[i]['id'])
        ]
        
        if not filtered_indices:
            st.warning("No questions found matching your query.")
            st.stop()
            
        # Adjust current index logic for filtered view
        # We need a separate state for "filtered_view_index" effectively, 
        # or we just reset to 0 when search changes.
        # For simplicity, we just show the filtered list paginated by current_index logic?
        # A simple approach: If searching, we just override the 'display index' to be local to the filtered list
        # But `current_index` is global. Let's just reset current_index if it's out of bounds of filtered list
        
        # Better UX: Show "Found X results", allow navigating through them.
        # We will use a local index for the filtered results.
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
        # Clear search state if empty
        if 'search_query' in st.session_state:
            del st.session_state['search_query']

    question_data = questions[actual_index]
    
    # -----------------------------------------------------------
    # Main Content Area
    # -----------------------------------------------------------
    
    # Header: Q# and Topic
    st.caption(f"Question {display_idx + 1} of {total_in_view} { '(Filtered)' if is_search_mode else ''}")
    st.markdown(f"### Question #{question_data['id']} (Topic {question_data['topic']})")
    
    # Container for the Question
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
            
            if question_data['is_multiselect']:
                st.write(f"**Select {question_data['expected_count']} options:**")
                for opt in question_data['options']:
                    # Use formatted key to persist state if needed, but form resets on rerun usually
                    # We can pre-select if already answered
                    is_checked = st.checkbox(opt)
                    if is_checked:
                        # Extract the letter 'A', 'B' etc
                        letter = opt.split('.')[0]
                        user_choice.append(letter)
            else:
                # Radio button
                # We need to map options to something selectable
                # If previously answered, index it
                radio_val = st.radio(
                    "Select an answer:",
                    question_data['options'],
                    index=None,
                    key=f"radio_{question_data['id']}"
                )
                if radio_val:
                    user_choice.append(radio_val.split('.')[0])
            
            submit_btn = st.form_submit_button("Submit Answer")
            
        # Logic to handle submission
        feedback_placeholder = st.empty()
        
        # Check if already answered in session state
        already_answered = st.session_state.user_answers.get(question_data['id'])
        
        show_answer = False
        
        if submit_btn:
             # Validate
             if not user_choice:
                 st.warning("Please select an option.")
             else:
                 # Save answer
                 # Sort list for multi-select comparison (e.g. ['A','B'] vs "AB")
                 user_choice.sort()
                 user_val = "".join(user_choice)
                 st.session_state.user_answers[question_data['id']] = user_val
                 already_answered = user_val
        
        if already_answered:
            correct_val = question_data['correct_answer'] or ""
            # Official answer string might be just "B" or "BC"
            # User val is "B" or "BC"
            
            is_correct = (already_answered == correct_val)
            
            if is_correct:
                feedback_placeholder.markdown(f"""
                <div class="success-msg">
                    <strong>✅ Correct!</strong> You chose {already_answered}.
                </div>
                """, unsafe_allow_html=True)
            else:
                feedback_placeholder.markdown(f"""
                <div class="error-msg">
                    <strong>❌ Incorrect.</strong> You chose {already_answered}.
                </div>
                """, unsafe_allow_html=True)
                
            show_answer = True

    # -----------------------------------------------------------
    # Answer & Explanation (Bottom)
    # -----------------------------------------------------------
    if show_answer or st.session_state.user_answers.get(question_data['id']):
        with st.expander("📝 View Official Answer & Suggested Discussion", expanded=False):
            st.markdown(f"#### Official Answer: <span class='highlight-answer'>{question_data['correct_answer']}</span>", unsafe_allow_html=True)
            
            if question_data['suggested_answer_text']:
                st.info(f"**Community Vote/Suggestion:** {question_data['suggested_answer_text']}")
                
            if question_data['discussion_link']:
                st.markdown(f"[🔗 Discuss on ExamTopics]({question_data['discussion_link']})")
            
            st.write("---")
            st.caption("Note: 'Suggested Answer' is often crowd-sourced. The 'Official Answer' is parsed from the bottom of the question block.")

    # -----------------------------------------------------------
    # Navigation Buttons
    # -----------------------------------------------------------
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_prev, col_next = st.columns([1, 1])
    
    with col_prev:
        if st.button("⬅️ Previous Question", use_container_width=True):
            if is_search_mode:
                if st.session_state.search_index > 0:
                    st.session_state.search_index -= 1
                    st.rerun()
            else:
                if st.session_state.current_index > 0:
                    st.session_state.current_index -= 1
                    st.rerun()
                    
    with col_next:
        if st.button("Next Question ➡️", use_container_width=True):
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
