from openai import OpenAI
from pathlib import Path
from typing import List, Dict, Any, Optional
import base64
from PIL import Image
import io
from config import settings
from schemas import Criterion, SubCriterion, BandComment

client = OpenAI(api_key=settings.openai_api_key)


def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """Convert PIL Image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format=format)
    img_bytes = buffered.getvalue()
    return base64.b64encode(img_bytes).decode('utf-8')


def transcribe_audio(audio_path: Path) -> tuple[str, Dict[str, int]]:
    """
    Transcribe audio using Whisper API.
    Returns (transcript, usage_stats)
    """
    with open(audio_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model=settings.whisper_model,
            file=audio_file,
            response_format="text"
        )
    
    # Whisper doesn't return token counts, estimate based on audio duration
    # Rough estimate: 1 minute of audio ≈ 150 words ≈ 200 tokens
    usage = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0  # Unknown for Whisper
    }
    
    return transcript, usage


def grade_with_gpt(
    criteria: List[Criterion],
    report_text: str,
    report_images: List[Image.Image],
    video_transcript: Optional[str] = None,
    video_frames: Optional[List[Image.Image]] = None,
    assignment_brief: str = ""
) -> tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    Grade a submission using GPT-4o.
    
    Returns (grades, usage_stats) where grades is a list of:
    {
        "criterion_name": str,
        "sub_question": str,
        "max_marks": float,
        "suggested_mark": float,
        "suggested_comment": str,
        "source": "report" | "video" | "both"
    }
    """
    
    # Build the grading prompt
    system_prompt = """You are an expert university lecturer grading student assignments.

Your task is to evaluate the student's work against a detailed rubric. For each criterion:

1. Select the most appropriate band score based on the evidence in the submission
2. Use the rubric's pre-written band comment as the foundation for your feedback
3. ADAPT (not replace) the band comment by inserting specific references to what the student actually wrote, showed, or demonstrated
4. Be fair, consistent, and evidence-based

CRITICAL: Do NOT invent new feedback phrasing. Always start with the rubric's band comment and adapt it minimally to reference submission-specific details."""

    user_prompt_parts = []
    
    # Add assignment brief for context
    if assignment_brief:
        user_prompt_parts.append(f"# Assignment Brief\n\n{assignment_brief}\n")
    
    # Add rubric structure
    user_prompt_parts.append("# Rubric\n\n")
    for criterion in criteria:
        user_prompt_parts.append(f"## {criterion.name} ({criterion.max_marks} marks)\n")
        for sub_crit in criterion.sub_criteria:
            user_prompt_parts.append(f"\n**{sub_crit.question}**\n")
            for band in sub_crit.bands:
                user_prompt_parts.append(f"({band.score}) {band.comment}\n")
        user_prompt_parts.append("\n")
    
    # Add report content
    user_prompt_parts.append("# Student's Report\n\n")
    user_prompt_parts.append(report_text[:15000])  # Limit to ~15k chars to manage token count
    
    if len(report_text) > 15000:
        user_prompt_parts.append("\n\n[Report truncated for length...]")
    
    # Add video transcript if available
    if video_transcript:
        user_prompt_parts.append("\n\n# Video Transcript\n\n")
        user_prompt_parts.append(video_transcript[:10000])  # Limit transcript
        
        if len(video_transcript) > 10000:
            user_prompt_parts.append("\n\n[Transcript truncated for length...]")
    
    # Instruction for structured output
    user_prompt_parts.append("""

# Your Task

For EACH sub-criterion in the rubric, provide:
1. The exact band score you're awarding (must match one of the rubric's defined scores)
2. The adapted band comment (start with the rubric comment for that score, then customize with specific evidence)
3. The source of evidence: "report", "video", or "both"

Format your response as a JSON array:
```json
[
  {
    "criterion_name": "Business Problem & Context",
    "sub_question": "Does the student identify...",
    "max_marks": 3,
    "suggested_mark": 2.5,
    "suggested_comment": "Good identification of a specific, complex business problem (supply chain optimization for automotive parts), with strong industry context and clear relevance. Well done!",
    "source": "report"
  },
  ...
]
```
""")
    
    prompt_text = "".join(user_prompt_parts)
    
    # Prepare messages
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Build content array with text and images
    content = [{"type": "text", "text": prompt_text}]
    
    # Add report images
    for i, img in enumerate(report_images[:10]):  # Limit to 10 images to manage cost
        img_base64 = image_to_base64(img)
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{img_base64}",
                "detail": "high"
            }
        })
    
    # Add video frames if available
    if video_frames:
        for i, frame in enumerate(video_frames[:10]):  # Limit to 10 frames
            frame_base64 = image_to_base64(frame)
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{frame_base64}",
                    "detail": "high"
                }
            })
    
    messages.append({"role": "user", "content": content})
    
    # Make API call
    response = client.chat.completions.create(
        model=settings.gpt_model,
        messages=messages,
        temperature=0.3,  # Lower temperature for more consistent grading
        response_format={"type": "json_object"}
    )
    
    # Extract response
    response_text = response.choices[0].message.content
    
    # Parse JSON response
    import json
    try:
        # Handle both direct array and object with "grades" key
        result = json.loads(response_text)
        if isinstance(result, dict) and "grades" in result:
            grades = result["grades"]
        elif isinstance(result, list):
            grades = result
        else:
            # Try to find an array in the response
            grades = []
            for key, value in result.items():
                if isinstance(value, list):
                    grades = value
                    break
    except json.JSONDecodeError as e:
        print(f"Error parsing GPT response: {e}")
        print(f"Response was: {response_text}")
        grades = []
    
    # Extract usage stats
    usage = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens
    }
    
    return grades, usage


def estimate_cost(usage: Dict[str, int], api_type: str) -> float:
    """
    Estimate API cost in USD based on usage.
    Pricing as of 2024 (approximate):
    - GPT-4o: $2.50/1M input tokens, $10.00/1M output tokens
    - Whisper: $0.006/minute (estimated from file size)
    """
    if api_type == "whisper":
        # Rough estimate - actual cost depends on audio duration
        return 0.01  # Approximate per call
    
    elif api_type.startswith("gpt"):
        input_cost = (usage.get("prompt_tokens", 0) / 1_000_000) * 2.50
        output_cost = (usage.get("completion_tokens", 0) / 1_000_000) * 10.00
        return input_cost + output_cost
    
    return 0.0
