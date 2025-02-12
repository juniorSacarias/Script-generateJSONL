import fitz  # PyMuPDF
import json
import os
import ollama  # Ollama library for interacting with the model

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    print(f"Extracting text from: {pdf_path}")
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text("text") for page in doc])
    print(f"Text extracted from {pdf_path}, text length: {len(text)} characters.")
    return text

def summarize_text_with_ollama(text):
    """Generate a summary of the text using Ollama."""
    print("Generating summary with Ollama...")
    response = ollama.chat(model="llama2", messages=[{"role": "user", "content": f"Summarize the following text:\n{text}"}])

    # Debug: print the response to inspect the structure
    print("Ollama response:", response)

    # Access the content of the response
    if 'message' in response:
        summary = response['message']['content'].strip()
        print("Summary generated successfully.")
        return summary
    else:
        print("Error: 'message' key not found in Ollama response.")
        return "Summary could not be generated."

def process_questions_with_ollama(question, context):
    """Generate an answer to the question using Ollama based on the summary."""
    print(f"Processing question: {question}")
    response = ollama.chat(model="llama2", messages=[{"role": "user", "content": f"Context: {context}\nQuestion: {question}\nAnswer:"}])

    # Debug: print the response to inspect the structure
    print("Ollama response:", response)

    # Access the content of the response
    if 'message' in response:
        answer = response['message']['content'].strip()
        print(f"Answer generated: {answer}")
        return answer
    else:
        print("Error: 'message' key not found in Ollama response.")
        return "Answer could not be generated."

def generate_jsonl_from_pdfs_and_questions(pdf_folder, txt_folder, jsonl_output_folder):
    """Generate JSONL files with PDF summaries and questions processed by Ollama."""
    print(f"Starting the generation of JSONL from PDFs and questions in TXT.")
    os.makedirs(jsonl_output_folder, exist_ok=True)

    # Loop through all PDF files
    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            print(f"Processing PDF file: {filename}")
            pdf_path = os.path.join(pdf_folder, filename)
            
            # Extract and summarize text from the PDF
            print(f"Extracting text from {filename}...")
            text = extract_text_from_pdf(pdf_path)
            print(f"Summarizing extracted text for {filename}...")
            summary = summarize_text_with_ollama(text)
            
            # Read questions from TXT files
            for txt_filename in os.listdir(txt_folder):
                if txt_filename.endswith(".txt"):
                    print(f"Processing TXT file: {txt_filename}")
                    txt_path = os.path.join(txt_folder, txt_filename)
                    
                    with open(txt_path, "r", encoding="utf-8") as txt_file:
                        questions = txt_file.readlines()
                        
                        # Generate the JSONL file
                        jsonl_filename = f"{os.path.splitext(filename)[0]}.jsonl"
                        jsonl_path = os.path.join(jsonl_output_folder, jsonl_filename)
                        
                        with open(jsonl_path, "a", encoding="utf-8") as jsonl_file:
                            for question in questions:
                                question = question.strip()  # Clean the question
                                if question:
                                    print(f"Processing question: {question}")
                                    # Process the question with Ollama
                                    answer = process_questions_with_ollama(question, summary)
                                    
                                    # Generate the entry in JSONL format
                                    jsonl_entry = {
                                        "instruction": "Summarize the following question concisely.",
                                        "input": question,
                                        "output": answer
                                    }
                                    jsonl_file.write(json.dumps(jsonl_entry) + "\n")
                        print(f"JSONL file saved at: {jsonl_path}")

if __name__ == "__main__":
    pdf_folder = "./train_pdf"  # Replace with the path to your PDF folder
    txt_folder = "./questions_txt"  # Replace with the path to your TXT folder with questions
    jsonl_output_folder = "./jsonl_output"

    # Generate JSONL files from PDFs and questions in TXT files
    print("Starting the conversion process...")
    generate_jsonl_from_pdfs_and_questions(pdf_folder, txt_folder, jsonl_output_folder)
    print("Conversion process completed.")
