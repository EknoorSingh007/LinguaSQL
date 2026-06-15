from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig
from peft import PeftModel
from fastapi import FastAPI, Request
import torch
import uvicorn

app = FastAPI()

base_model_name = "gpt2"
adapter_name    = "eknoorsingh007/linguasql-sql-finetuned"
hf_token        = None

has_cuda = torch.cuda.is_available()

if has_cuda:
    bnb_config = BitsAndBytesConfig(
        load_in_8bit=True,
        bnb_8bit_use_double_quant=True,
        bnb_8bit_quant_type="nf4",
        bnb_8bit_compute_dtype=torch.bfloat16
    )
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        quantization_config=bnb_config,
        device_map={"": 0},
        token=hf_token
    )
else:
    print("[LinguaSQL] No CUDA GPU detected. Loading model on CPU (no 8-bit quantization).")
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.float32,
        token=hf_token
    )

# Load the LoRA adapter on top of the base model, then merge for faster inference
model = PeftModel.from_pretrained(base_model, adapter_name, token=hf_token)
model = model.merge_and_unload()

# Clear GPT-2's default max_length=50 so max_new_tokens is respected cleanly
model.generation_config.max_length = None

tokenizer = AutoTokenizer.from_pretrained(adapter_name, token=hf_token)
tokenizer.pad_token = tokenizer.eos_token

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    return_full_text=False,
    clean_up_tokenization_spaces=True,
    device=-1 if not has_cuda else 0
)

@app.post("/generate")
async def generate(req: Request):
    body = await req.json()
    prompt = body["inputs"]
    params = body.get("parameters", {"max_new_tokens": 300, "temperature": 0.7})
    if "temperature" in params and params["temperature"] <= 0:
        params["temperature"] = 0.7

    output = pipe(prompt, **params)
    return {"generated_text": output[0]["generated_text"]}

if __name__ == "__main__":
    uvicorn.run("llm_server:app", port=8080, reload=True)
