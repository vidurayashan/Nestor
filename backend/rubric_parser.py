import re
from typing import List, Tuple
from schemas import Criterion, SubCriterion, BandComment, RubricStructure


def parse_rubric_markdown(markdown: str) -> RubricStructure:
    """
    Parse a markdown rubric into structured JSON.
    
    Expected format:
    ## Criterion Name (X marks)
    
    **Question text**
    
    (score) Band comment
    (score) Band comment
    ...
    (0) Band comment
    
    Multiple questions can exist under one criterion heading.
    """
    criteria = []
    
    # Split into criterion sections by ## headers
    criterion_sections = re.split(r'\n## ', markdown)
    
    for section in criterion_sections:
        if not section.strip():
            continue
            
        lines = section.strip().split('\n')
        
        # Parse criterion header: "Criterion Name (X marks)" or "## Criterion Name (X marks)"
        header = lines[0].strip()
        if header.startswith('## '):
            header = header[3:].strip()
        
        # Extract criterion name and marks
        match = re.match(r'^(.+?)\s*\((\d+(?:\.\d+)?)\s*marks?\)', header)
        if not match:
            continue
        
        criterion_name = match.group(1).strip()
        max_marks = float(match.group(2))
        
        # Parse sub-criteria (each bolded question with its bands)
        sub_criteria = []
        current_question = None
        current_bands = []
        
        for line in lines[1:]:
            line = line.strip()
            
            # Check if this is a bolded question
            bold_match = re.match(r'^\*\*(.+?)\*\*$', line)
            if bold_match:
                # Save previous sub-criterion if exists
                if current_question and current_bands:
                    sub_criteria.append(SubCriterion(
                        question=current_question,
                        bands=current_bands
                    ))
                
                # Start new sub-criterion
                current_question = bold_match.group(1).strip()
                current_bands = []
                continue
            
            # Check if this is a band comment: (score) comment
            band_match = re.match(r'^\((\d+(?:\.\d+)?)\)\s*(.+)$', line)
            if band_match and current_question:
                score = float(band_match.group(1))
                comment = band_match.group(2).strip()
                current_bands.append(BandComment(score=score, comment=comment))
        
        # Save last sub-criterion
        if current_question and current_bands:
            sub_criteria.append(SubCriterion(
                question=current_question,
                bands=current_bands
            ))
        
        if sub_criteria:
            criteria.append(Criterion(
                name=criterion_name,
                max_marks=max_marks,
                sub_criteria=sub_criteria
            ))
    
    return RubricStructure(criteria=criteria)


def validate_rubric_structure(rubric: RubricStructure) -> Tuple[bool, List[str]]:
    """Validate that the parsed rubric is well-formed"""
    errors = []
    
    if not rubric.criteria:
        errors.append("No criteria found in rubric")
        return False, errors
    
    total_max_marks = 0
    for criterion in rubric.criteria:
        if not criterion.sub_criteria:
            errors.append(f"Criterion '{criterion.name}' has no sub-criteria")
        
        total_max_marks += criterion.max_marks
        
        for sub_criterion in criterion.sub_criteria:
            if not sub_criterion.bands:
                errors.append(
                    f"Sub-criterion '{sub_criterion.question[:50]}...' has no band comments"
                )
            
            # Check that bands are in descending order
            scores = [band.score for band in sub_criterion.bands]
            if scores != sorted(scores, reverse=True):
                errors.append(
                    f"Band scores for '{sub_criterion.question[:50]}...' should be in descending order"
                )
    
    return len(errors) == 0, errors
