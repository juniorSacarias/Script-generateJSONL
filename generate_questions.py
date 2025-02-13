import fitz  # PyMuPDF
import ollama
import os
import re  # Para eliminar números de las preguntas

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join([page.get_text("text") for page in doc])
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

def generate_summary(text):
    """Generates a summary of the text using Ollama with Llama 2."""
    if not text.strip():
        return "No text could be extracted from the document."
    
    prompt = f"Summarize the following text clearly and concisely:\n\n{text}"
    response = ollama.chat(model="llama2", messages=[{"role": "user", "content": prompt}])
    return response['message']['content']

def generate_questions(summary, num_questions=50):
    """Generates unique questions based on the summary using Ollama with Llama 2."""
    if not summary.strip():
        return []

    unique_questions = set()
    
    while len(unique_questions) < num_questions:
        remaining = num_questions - len(unique_questions)
        prompt = f"Generate {remaining} different key questions about the following summary. Do not repeat questions, and do not add numbers or extra characters:\n\n{summary}"
        response = ollama.chat(model="llama2", messages=[{"role": "user", "content": prompt}])
        
        new_questions = set(response['message']['content'].split("\n"))
        unique_questions.update(new_questions)

        # Clean questions: remove leading numbers and whitespace
        unique_questions = {re.sub(r'^\d+\.\s*', '', q).strip() for q in unique_questions if q.strip()}

    return list(unique_questions)[:num_questions]

def process_pdfs_in_directory(input_dir, output_dir):
    """Processes all PDFs in a directory and saves only the questions in text files."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # Create output directory if it doesn't exist

    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print("No PDF files found in the directory.")
        return

    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_dir, pdf_file)
        output_txt_path = os.path.join(output_dir, f"{os.path.splitext(pdf_file)[0]}_questions.txt")

        print(f"\n📄 Processing: {pdf_file}...")
        text = extract_text_from_pdf(pdf_path)

        print("📝 Generating summary...")
        summary = generate_summary(text)

        print("❓ Generating unique questions based on the summary...")
        questions = generate_questions(summary, num_questions=50)

        with open(output_txt_path, "w", encoding="utf-8") as f:
            for question in questions:
                f.write(f"{question}\n")

        print(f"✅ Questions saved in: {output_txt_path}")

# 📂 Directory configuration
input_dir = "train_pdf"  # Folder where PDFs are located
output_dir = "questions_txt"  # Folder where text files will be saved

process_pdfs_in_directory(input_dir, output_dir)
