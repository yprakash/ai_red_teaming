import time

import torch
from transformers import pipeline, AutoTokenizer

# model, tokenizer = mlx_lm.load("vectara/hallucination_evaluation_model")
# ERROR:root:Model type HHEMv2Config not supported.
# The mlx-lm library is specifically designed for Causal Language Models (text generators like Llama, Mistral, and Phi).
# The Vectara model is a Sequence Classifier with a custom architecture (HHEMv2). Because mlx-lm doesn't have
# the "blueprint" for Vectara’s specific custom layers, it doesn't know how to build the model in MLX.
#
# Solution: Use "Transformers + MPS": runs directly on Mac's GPU/Neural Engine.

def get_best_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


device = get_best_device()  # "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using device: {device}")

# Create a template. The <pad> token is specific to T5-based models to signal the start of a task.
# It structures the input so the model knows it's performing a "Consistency" check.
prompt = "<pad> Determine if the hypothesis is true given the premise?\n\nPremise: {text1}\n\nHypothesis: {text2}"

model_id = "vectara/hallucination_evaluation_model"
text_pairs = [ # Test data, List[Tuple[str, str]]
    ("The capital of France is Berlin.", "The capital of France is Paris."), # factual but hallucinated
    ('I am in California', 'I am in United States.'), # Consistent
    ('I am in United States', 'I am in California.'), # Hallucinated
    ("A person on a horse jumps over a broken down airplane.", "A person is outdoors, on a horse."),
    ("A boy is jumping on skateboard in the middle of a red bridge.", "The boy skates down the sidewalk on a red bridge"),
    ("A man with blond-hair, and a brown shirt drinking out of a public water fountain.", "A blond man wearing a brown shirt is reading a book."),
    ("Mark Wahlberg was a fan of Manny.", "Manny was a fan of Mark Wahlberg.")
]

# A list comprehension that injects actual premise and hypothesis into the prompt template for every pair in your data.
input_pairs = [prompt.format(text1=pair[0], text2=pair[1]) for pair in text_pairs]

tt = time.time()
# Initializes the model. It uses hallucination_evaluation_model (the brain) and flan-t5-base (the dictionary).
# `trust_remote_code=True` is required because this model uses custom logic not in the standard library.
classifier = pipeline(
    "text-classification",
    model=model_id,
    tokenizer=AutoTokenizer.from_pretrained('google/flan-t5-base'),
    trust_remote_code=True,  # allows the custom Vectara logic to load correctly
    device=device
)
print(f"Time taken to load model: {int(time.time() - tt)} seconds")

full_scores = classifier(input_pairs, top_k=None)  # Runs the actual math. `top_k=None` tells the model
# to return the probability of both labels ("consistent" and "inconsistent") rather than just the winner.

simple_scores = [
    score_dict['score']
    for score_for_both_labels in full_scores
    for score_dict in score_for_both_labels
    if score_dict['label'] == 'consistent'
]

# Set a threshold (0.5 is standard, but you can increase it to be more strict)
threshold = 0.5
# Hallucination detection isn't always black and white; it's a spectrum of probability. Here is how to interpret the scores the model gives you:
# +-------------+-----------------------------------------+-------------------+
# | Score Range | Interpretation                          | Verdict           |
# +-------------+-----------------------------------------+-------------------+
# | 0.0 - 0.3   | High contradiction / No factual overlap | Hallucination     |
# | 0.3 - 0.6   | Uncertain / Partial overlap             | Check Manually    |
# | 0.6 - 1.0   | High factual consistency                | Not Hallucination |
# +-------------+-----------------------------------------+-------------------+

for i, score in enumerate(simple_scores):
    if score < threshold:
        print(f"Verdict: Hallucination (Score: {score:.4f}) : {text_pairs[i]}")
    else:
        print(f"Verdict: Not Hallucination (Score: {score:.4f}) : {text_pairs[i]}")

print(f"Total Time taken: {int(time.time() - tt)} seconds")
