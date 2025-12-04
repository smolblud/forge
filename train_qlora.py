from unsloth import FastTrainer
from transformers import AutoTokenizer
from datasets import load_dataset

MODEL_NAME = "microsoft/phi-3-mini-4k-instruct"
DATA_PATH = "data/persona_dataset.json"
OUTPUT_DIR = "qlora_adapter"

# Load dataset
# If your dataset is in JSONL format, change 'json' to 'jsonl' and ensure each line is a JSON object
# If not, this will work for a standard JSON array

dataset = load_dataset("json", data_files=DATA_PATH, split="train")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
trainer = FastTrainer(
    model_name=MODEL_NAME,
    tokenizer=tokenizer,
    output_dir=OUTPUT_DIR,
    bits=4,  # QLoRA 4-bit
    max_length=1024,
    train_dataset=dataset,
    prompt_template="Below is a writing submission. Provide a critique.",
    batch_size=2,
    epochs=3,
    lr=2e-4,
)

trainer.train()
trainer.save_adapter("adapter.safetensors")
