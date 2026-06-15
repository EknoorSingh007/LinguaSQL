# LinguaSQL — Fine-tuning Script
# Run on Google Colab: Runtime > Change runtime type > GPU (T4)

import subprocess, sys

subprocess.run([
    sys.executable, "-m", "pip", "install", "-U", "-q",
    "bitsandbytes", "peft", "datasets", "accelerate",
    "huggingface_hub", "transformers"
], check=True)

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from huggingface_hub import login

hf_token    = "YOUR_HF_TOKEN"
hf_username = "YOUR_HF_USERNAME"
model_name  = "gpt2"
output_repo = f"{hf_username}/linguasql-sql-finetuned"

login(hf_token)

raw_dataset = load_dataset("gretelai/synthetic_text_to_sql", split="train")
print(f"Dataset loaded: {len(raw_dataset)} samples")

bnb_config = BitsAndBytesConfig(
    load_in_8bit=True,
    bnb_8bit_use_double_quant=True,
    bnb_8bit_quant_type="nf4",
    bnb_8bit_compute_dtype=torch.bfloat16
)

tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)
tokenizer.pad_token = tokenizer.eos_token

base_model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map={"": 0},
    token=hf_token
)

base_model.gradient_checkpointing_enable()
base_model = prepare_model_for_kbit_training(base_model)

config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["c_attn", "c_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

base_model = get_peft_model(base_model, config)

def print_trainable_parameters(model):
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    all_param = sum(p.numel() for p in model.parameters())
    print(f"trainable params: {trainable_params} || all params: {all_param} || "
          f"trainable%: {100 * trainable_params / all_param:.2f}")

print_trainable_parameters(base_model)

def format_and_tokenize(example):
    text = (
        "You are a helpful assistant that converts natural language into valid SQLite SQL queries.\n\n"
        f"Prompt: {example['sql_prompt']}\n"
        f"SQL: {example['sql']}"
    )
    return tokenizer(
        text,
        max_length=512,
        truncation=True,
        padding="max_length",
        return_tensors="np"
    )

tokenized_dataset = raw_dataset.map(format_and_tokenize, batched=False)
print(f"Train data size: {len(tokenized_dataset)}")

trainer = transformers.Trainer(
    model=base_model,
    train_dataset=tokenized_dataset,
    args=transformers.TrainingArguments(
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        max_steps=1000,
        learning_rate=1.5e-4,
        fp16=True,
        logging_steps=50,
        output_dir="outputs",
        optim="adafactor"
    ),
    data_collator=transformers.DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

base_model.config.use_cache = False
trainer.train()

trainer.model.push_to_hub(output_repo)
tokenizer.push_to_hub(output_repo)

print(f"\nModel live at: https://huggingface.co/{output_repo}")
