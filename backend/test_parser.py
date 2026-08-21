"""
Test script for rubric parser.
Run with: python test_parser.py
"""

from pathlib import Path
from rubric_parser import parse_rubric_markdown, validate_rubric_structure

def test_rubric_parser():
    # Read the sample rubric
    rubric_path = Path("../uploads/BUS1004_Assessment1_Rubric_802b.md")
    
    if not rubric_path.exists():
        print("Error: Sample rubric file not found at", rubric_path)
        return
    
    with open(rubric_path, 'r', encoding='utf-8') as f:
        rubric_markdown = f.read()
    
    print("=" * 60)
    print("Testing Rubric Parser")
    print("=" * 60)
    print()
    
    # Parse
    try:
        rubric = parse_rubric_markdown(rubric_markdown)
        print(f"✓ Successfully parsed rubric")
        print(f"  Found {len(rubric.criteria)} criteria")
        print()
        
        # Validate
        is_valid, errors = validate_rubric_structure(rubric)
        
        if is_valid:
            print("✓ Rubric structure is valid")
        else:
            print("✗ Rubric validation errors:")
            for error in errors:
                print(f"  - {error}")
        print()
        
        # Display parsed structure
        total_marks = 0
        for criterion in rubric.criteria:
            print(f"Criterion: {criterion.name} ({criterion.max_marks} marks)")
            total_marks += criterion.max_marks
            
            for i, sub_crit in enumerate(criterion.sub_criteria, 1):
                print(f"  Sub-criterion {i}:")
                print(f"    Question: {sub_crit.question[:60]}...")
                print(f"    Bands: {len(sub_crit.bands)} score levels")
                
                # Show score range
                scores = [b.score for b in sub_crit.bands]
                print(f"    Score range: {min(scores)} - {max(scores)}")
                print()
        
        print("=" * 60)
        print(f"Total marks: {total_marks}")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ Error parsing rubric: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rubric_parser()
