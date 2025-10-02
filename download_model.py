# file: download_model.py
from transformers import AutoTokenizer, AutoModelForCausalLM
import os

# This is the clean, predictable folder where the model will be saved
save_directory = os.path.join("backend", "recommendation_service", "phi-3-local-model")
model_id = "microsoft/phi-3-mini-4k-instruct"

print(f"--- Starting download for {model_id} ---")
print(f"--- Saving to: {save_directory} ---")

# Download the model from the Hub using the compatible attention implementation
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    trust_remote_code=True,
    attn_implementation="eager" # Add this line to solve the warnings
)
tokenizer = AutoTokenizer.from_pretrained(model_id)

# Save the model and tokenizer to our clean local directory
model.save_pretrained(save_directory)
tokenizer.save_pretrained(save_directory)

print(f"✅ Download and save complete! Model is in '{save_directory}'.")