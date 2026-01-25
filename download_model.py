# Download German BERT model
# This only needs to run once

from transformers import AutoTokenizer, AutoModel

print("Downloading German BERT model...")
print("(This may take 2-5 minutes...)")

model_name = "distilbert-base-german-cased"

# Download tokenizer
print("\nDownloading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Download model
print("Downloading model...")
model = AutoModel.from_pretrained(model_name)

print("\n✅ Success! Model downloaded and cached.")
print(f"Model: {model_name}")
print("You can now use it offline!")
