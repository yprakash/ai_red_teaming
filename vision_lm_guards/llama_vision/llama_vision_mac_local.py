import os
import time

from mlx_vlm import convert, load, generate

model_id = "meta-llama/Llama-3.2-11B-Vision"
local_model_path = "~/mlx_converted/llamavision_11b_4bit"

if os.path.exists(local_model_path):
    print(f"Model already converted at {local_model_path}. Using it")
else:
    tt = time.time()
    convert(
        hf_path=model_id,
        mlx_path=local_model_path,
        quantize=True,
        q_group_size=64,
        q_bits=4,
        dtype="float16"
    )
    print(f"Time taken to convert {model_id}: {int(time.time() - tt)} seconds")

tt = time.time()
model, processor = load(local_model_path)
print(f"Time taken to load local model: {int(time.time() - tt)} seconds")


def model_disk_size_gb(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            # if f.endswith((".safetensors", ".bin")):
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)

    print(f"Model disk size: {total_size / 1e9:,.2f} GB")
    return total_size / 1e9


def get_model_details():
    out = f"{model_id} Local path: {local_model_path}\n"
    # print(f"Memory footprint: {AutoModelForCausalLM.from_pretrained().get_memory_footprint() / 1e9:,.1f} GB")
    out += f"Disk size: {model_disk_size_gb(local_model_path):,.2f} GB\n"
    # out += f"Quantization: {??}, Group size: {??}\n"
    return out

def probe(prompt):
    tt = time.time()
    response = generate(
        model,
        processor,
        prompt,
        max_tokens=256
    )
    print(f"{int(time.time() - tt)} seconds taken to generate response: {response}")
    return response


while True:
    user_input = input("Enter your prompt (or 'exit' to quit): ")
    user_input = user_input.strip()
    if not user_input:
        continue
    if user_input.lower() == 'exit':
        break
    probe(user_input)
