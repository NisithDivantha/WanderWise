from transformers import pipeline

summarizer = pipeline("text-generation", model="EleutherAI/gpt-neo-1.3B")

def generate_friendly_summary(day: str, pois: list) -> str:
    """
    Generate a friendly paragraph for a day's itinerary.
    """
    prompt = f"""
    Write a friendly travel summary for this day:
    Day: {day}
    Places:
    """
    for poi in pois:
        prompt += f"- {poi['name']} ({poi['category']})\n"

    prompt += "\nTone: fun and engaging."

    try:
        result = summarizer(prompt, max_length=150, do_sample=True, temperature=0.7)[0]["generated_text"]
        return result.replace(prompt, "").strip()
    except Exception as e:
        return f"[LLM Error: {e}]"
