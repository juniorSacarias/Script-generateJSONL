import fitz  # PyMuPDF
import json
import os
import re
import ollama
import pdfplumber
import pytesseract
import time
import sys
from pdf2image import convert_from_path
from PIL import Image
from tqdm import tqdm

def print_banner():
    """Prints a nice banner in the console."""
    print("=" * 50)
    print("📄✨ Welcome to the PDF and CV Processor ✨📄")
    print("=" * 50)

def progress_bar(task, total=100):
    """Simulates a progress bar for tasks."""
    for _ in tqdm(range(total), desc=task, bar_format="{l_bar}{bar} [Remaining time: {remaining}]"):
        time.sleep(0.02)

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    print(f"📄 Extracting text from: {pdf_path}")
    progress_bar("Extracting text")
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text("text") for page in doc])
    print(f"✅ Extraction completed ({len(text)} characters)")
    return text

def summarize_text_with_ollama(text):
    """Generates a summary of the text using Ollama."""
    print("📜 Generating summary...")
    progress_bar("Summarizing content")
    response = ollama.chat(model="llama2", messages=[{"role": "user", "content": f"Summarize the following text:\n{text}"}])
    return response.get('message', {}).get('content', 'Summary not available.')

def generate_questions_with_ollama(summary, num_questions):
    """Generates questions based on the summary using Ollama."""
    print(f"❓ Generating {num_questions} questions...")
    progress_bar("Generating questions")
    prompt = f"Generate {num_questions} questions based on the following summary:\n{summary}"
    response = ollama.chat(model="llama2", messages=[{"role": "user", "content": prompt}])
    return response.get('message', {}).get('content', 'Questions not generated.')

def process_questions_with_ollama(question, context):
    """Generates answers based on the context using Ollama."""
    print(f"💡 Answering: {question}")
    progress_bar("Generating answer")
    response = ollama.chat(model="llama2", messages=[{"role": "user", "content": f"Context: {context}\nQuestion: {question}\nAnswer:"}])
    return response.get('message', {}).get('content', 'Answer not available.')

def process_cv(pdf_path, results_folder, num_questions):
    """Processes a CV and saves summary, questions, and answers."""
    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    output_dir = os.path.join(results_folder, filename)
    os.makedirs(output_dir, exist_ok=True)
    
    text = extract_text_from_pdf(pdf_path)
    summary = summarize_text_with_ollama(text)
    questions = generate_questions_with_ollama(summary, num_questions)
    
    summary_file = os.path.join(output_dir, f"{filename}_summary.txt")
    questions_file = os.path.join(output_dir, f"{filename}_questions.txt")
    responses_file = os.path.join(output_dir, f"{filename}_responses.jsonl")
    
    with open(summary_file, "w", encoding="utf-8") as txt_file:
        txt_file.write(summary)
    
    with open(questions_file, "w", encoding="utf-8") as txt_file:
        txt_file.write(questions)
    
    with open(responses_file, "w", encoding="utf-8") as jsonl_file:
        for question in questions.split("\n"):
            if question.strip():
                answer = process_questions_with_ollama(question, summary)
                json_entry = {"Instruction": question, "Input": summary, "Response": answer}
                jsonl_file.write(json.dumps(json_entry) + "\n")
    
    print(f"✅ Summary saved in: {summary_file}")
    print(f"✅ Questions saved in: {questions_file}")
    print(f"✅ Answers saved in: {responses_file}")

def main():
    """Application menu to execute different functions."""
    print_banner()
    pdf_folder = input("📂 Enter the folder where the PDFs are located: ")
    use_same_folder = input("📂 Are the CVs in the same folder? (y/n): ").strip().lower()
    
    if use_same_folder == "n":
        cv_folder = input("📂 Enter the folder where the CVs are located: ")
    else:
        cv_folder = pdf_folder
    
    results_folder = input("📂 Enter the folder where you want to save the results: ")
    os.makedirs(results_folder, exist_ok=True)
    
    while True:
        print("\n✨ Options Menu ✨")
        print("1️⃣  Summarize PDFs and generate questions")
        print("2️⃣  Answer questions based on PDFs")
        print("3️⃣  Process all CVs in the folder")
        print("4️⃣  🚪 Exit")
        
        option = input("👉 Enter the option number: ")
        
        if option == "1":
            num_questions = int(input("🎯 Enter the number of questions to generate per PDF: "))
            for filename in os.listdir(pdf_folder):
                if filename.endswith(".pdf"):
                    pdf_path = os.path.join(pdf_folder, filename)
                    process_cv(pdf_path, results_folder, num_questions)
        elif option == "2":
            print("🔍 Function under development...")
        elif option == "3":
            num_questions = int(input("🎯 Enter the number of questions to generate per CV: "))
            for filename in os.listdir(cv_folder):
                if filename.endswith(".pdf"):
                    pdf_path = os.path.join(cv_folder, filename)
                    process_cv(pdf_path, results_folder, num_questions)
        elif option == "4":
            print("👋 Thank you for using the PDF processor. Goodbye!")
            break
        else:
            print("⚠️ Invalid option, please try again.")

if __name__ == "__main__":
    main()
