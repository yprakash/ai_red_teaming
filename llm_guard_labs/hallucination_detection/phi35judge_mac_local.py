import os
import time
from pathlib import Path

from mlx_lm import convert, generate, load

model_id = "grounded-ai/phi3.5-hallucination-judge-merge"
local_model_path = "mlx_models/phi35_4bit"
local_model_path = str(Path("~/" + local_model_path).expanduser())


def model_disk_size_gb(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)

    print(f"Disk size({path}): {total_size / 1e9:,.2f} GB")
    return total_size / 1e9


def get_model_details():
    out = f"{model_id} Local path: {local_model_path}\n"
    # print(f"Memory footprint: {AutoModelForCausalLM.from_pretrained().get_memory_footprint() / 1e9:,.1f} GB")
    out += f"Disk size: {model_disk_size_gb(local_model_path):,.2f} GB\n"
    return out


if os.path.exists(local_model_path):
    print(f"Using the already converted model at {local_model_path}")
    # print(f"HF cache size: {model_disk_size_gb(str(Path("~/.cache/huggingface/hub").expanduser())):.2f} GB")
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
model, tokenizer = load(local_model_path)
print(f"Time taken to load local model: {int(time.time() - tt)} seconds")

get_model_details()

base_prompt = """Your job is to evaluate whether a machine learning model has hallucinated or not.
A hallucination occurs when the response is coherent but factually incorrect or nonsensical
outputs that are not grounded in the provided context.
You are given the following information:
####INFO####
[Knowledge]: Walrus are the largest mammal
[User Input]: What is the smallest mammal?
[Model Response]: Walrus
####END INFO####
Based on the information provided is the model output a hallucination? Respond with only "yes" or "no"
"""

response = generate(
    model,
    tokenizer,
    prompt=base_prompt,
    max_tokens=4
)

print(f"{model_id} Hallucination response: {response}")
