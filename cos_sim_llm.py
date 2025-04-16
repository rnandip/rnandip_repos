import fitz  # PyMuPDF
import google.generativeai as genai
import os

def query_pdf_gemini_match(pdf_path, query, model_name="models/gemini-pro", api_key="YOUR_API_KEY"):
    """
    Uses Gemini (Google Generative AI) to semantically match a query to the best paragraph from a PDF.
    """
    # Configure Gemini

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=GEMINI_API_KEY)

    model=genai.GenerativeModel("gemini-1.5-pro")

    # Extract paragraphs from PDF
    doc = fitz.open(pdf_path)
    chunks = []
    for page in doc:
        text = page.get_text().strip()
        if text:
            chunks.extend([chunk.strip() for chunk in text.split('\n\n') if chunk.strip()])

    if not chunks:
        return {"matched_text": "", "matched_index": -1}

    # Limit chunks to avoid token limit
    max_chunks = 10
    short_chunks = chunks[:max_chunks]

    # Build prompt
    prompt = f"""You are a helpful assistant.

Given the query: "{query}"

Choose the most relevant paragraph from the list below that best answers the query.

Paragraphs:
"""
    for i, chunk in enumerate(short_chunks):
        prompt += f"[{i+1}]: {chunk}\n\n"

    prompt += "Only respond with the number of the most relevant paragraph."

    # Get Gemini's response
    response = model.generate_content(prompt)
    reply = response.text.strip()

    try:
        chosen_index = int(reply) - 1
        return {
            "matched_text": short_chunks[chosen_index],
            "matched_index": chosen_index + 1
        }
    except:
        return {
            "error": "Gemini could not parse a valid index.",
            "raw_response": reply
        }

result=query_pdf_gemini_match("sample-report.pdf", "summarize data analysis")
print(result)
