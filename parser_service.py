import re
import streamlit as st
# Force refresh for Streamlit Cloud - 2026-01-15


@st.cache_data
def parse_markdown_file(content):
    """Parses the Markdown content into a list of question dictionaries."""
    questions = []
    blocks = content.split('----------------------------------------')
    
    for block in blocks:
        block = block.strip()
        if not block: continue
            
        id_match = re.search(r'## Exam .* question (\d+) discussion', block)
        if not id_match: continue
        
        suggested_match = re.search(r'Suggested Answer:\s+([A-Z]+)', block)
        official_match = re.search(r'\*\*Answer:\s+([A-Z]+)\*\*', block)
        topic_match = re.search(r'Topic #:\s+(\d+)', block)
        link_match = re.search(r'\[View on ExamTopics\]\((.*?)\)', block)
        
        # Options extraction
        lines = block.split('\n')
        # Find start of options
        opt_start = len(lines)
        for i, line in enumerate(lines):
            if re.match(r'^[A-F]\.\s+', line):
                opt_start = i
                break
                
        # Parse options
        options = []
        for line in lines[opt_start:]:
            if re.match(r'^[A-F]\.\s+', line):
                # Clean up option line
                options.append(line.strip())
        
        # Meta end for Body extraction
        meta_end = 0
        for i, line in enumerate(lines):
            if "[All AWS Certified Solutions Architect" in line:
                meta_end = i + 1
                break
                
        # Body extraction
        clean_body = []
        suggested_answer = None
        for line in lines[meta_end:opt_start]:
            s = line.strip()
            if not s or s.startswith(("Question #", "Topic #", "Exam question from", "Amazon's", "AWS Certified")):
                continue
            if s.startswith("Suggested Answer:"):
                suggested_answer = s
                continue
            clean_body.append(s)
            
        q_text = "\n".join(clean_body)
        is_multi = "(Choose two" in q_text or "(Choose three" in q_text
        
        questions.append({
            "id": id_match.group(1),
            "topic": topic_match.group(1) if topic_match else "Unknown",
            "question": q_text,
            "options": options,
            "correct_answer": suggested_match.group(1) if suggested_match else (official_match.group(1) if official_match else None),
            "suggested_answer_text": suggested_answer,
            "discussion_link": link_match.group(1) if link_match else None,
            "is_multiselect": is_multi,
            "expected_count": 3 if "(Choose three" in q_text else (2 if is_multi else 1)
        })
        
    return questions
