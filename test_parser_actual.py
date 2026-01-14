
from quiz_parser import parse_markdown_file
from pathlib import Path
import json

try:
    content = Path("SAA_C03.md").read_text(encoding='utf-8')
    questions = parse_markdown_file(content)
    
    # Question 2 (index 1) which describes "Question #: 935"
    q935 = next((q for q in questions if q['id'] == '935'), None)
    
    if q935:
        print(f"ID: {q935['id']}")
        print(f"Correct Answer: '{q935['correct_answer']}'")
        print(f"Correct Answer Type: {type(q935['correct_answer'])}")
        print(f"Length: {len(q935['correct_answer'])}")
        print(f"Matches 'BC': {q935['correct_answer'] == 'BC'}")
    else:
        print("Question 935 not found")
        
    # Also check index 1 just in case
    if len(questions) > 1:
        q_idx_1 = questions[1]
        print(f"Index 1 ID: {q_idx_1['id']}")
        print(f"Index 1 Correct Answer: '{q_idx_1['correct_answer']}'")

except Exception as e:
    print(f"Error: {e}")
