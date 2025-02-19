# -*- coding: utf-8 -*-

# === 1. Montar Google Drive ===
from google.colab import drive
import os

drive.mount('/content/drive')

# Ruta donde están los archivos (cámbiala según tu estructura en Drive)
DATASET_PATH = '/content/drive/MyDrive/cvs'

# === 2. Instalar dependencias ===
!pip install --no-deps bitsandbytes accelerate xformers==0.0.29 peft trl triton
!pip install --no-deps cut_cross_entropy unsloth_zoo
!pip install sentencepiece protobuf datasets huggingface_hub hf_transfer
!pip install --no-deps unsloth
!pip install pymupdf python-docx

# === 3. Importar Librerías ===
import fitz  # PyMuPDF para PDFs
import docx  # python-docx para DOCX
from datasets import Dataset

# === 4. Funciones para extraer texto de documentos ===
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
    except Exception as e:
        print(f"⚠️ Error leyendo {pdf_path}: {e}")
    return text

def extract_text_from_docx(docx_path):
    text = ""
    try:
        doc = docx.Document(docx_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"⚠️ Error leyendo {docx_path}: {e}")
    return text

def load_documents_from_folders(folder_path):
    data = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            print(f"📄 Procesando archivo: {file_path}")  # Debugging
            if file.endswith(".pdf"):
                text = extract_text_from_pdf(file_path)
            elif file.endswith(".docx"):
                text = extract_text_from_docx(file_path)
            else:
                continue  # Ignorar otros archivos
            
            if text.strip():
                formatted_text = f"Below is a document content. Process the text and provide a structured response.\n\n### Content:\n{text}\n\n### Response:\n"
                data.append({"text": formatted_text})
    return Dataset.from_list(data)

# === 5. Cargar los documentos y formatearlos ===
cpt_dataset = load_documents_from_folders(DATASET_PATH)  # Ruta de los archivos en Drive

# Verificar si el dataset tiene datos
if len(cpt_dataset) == 0:
    raise ValueError("❌ Error: No se encontraron datos en el dataset. Verifica la carga de archivos.")

print(f"✅ Dataset cargado con {len(cpt_dataset)} ejemplos")
print(cpt_dataset[:5])

# === 6. Cargar modelo con Unsloth ===
from unsloth import FastLanguageModel
import torch

max_seq_length = 2048
dtype = None
load_in_4bit = True

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Llama-3.2-3B-Instruct",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

# === 7. Configurar LoRA Adapter ===
model = FastLanguageModel.get_peft_model(
    model,
    r = 128,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 32,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
    use_rslora = True,
    loftq_config = None,
)

# === 8. Entrenar modelo ===
from unsloth import UnslothTrainer, UnslothTrainingArguments

cpt_trainer = UnslothTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = cpt_dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 2,
    args = UnslothTrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 8,
        max_steps = 120,
        warmup_steps = 10,
        learning_rate = 5e-5,
        embedding_learning_rate = 1e-5,
        fp16 = True,
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs",
        report_to = "none",
    ),
)

trainer_stats = cpt_trainer.train()

# === 9. Guardar el modelo ===
model.save_pretrained_gguf("model", tokenizer, quantization_method = "f16")
print("✅ Entrenamiento completado y modelo guardado.")
