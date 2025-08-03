import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from transformers import pipeline
from textblob import TextBlob
import threading
import nltk
import random

from dotenv import load_dotenv
load_dotenv()  # loads environment variables from .env

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Suppress info & warnings
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Download required data for TextBlob
# This only needs to be run once.
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    nltk.download('punkt')

# --- Start of New Humanizer Logic ---

# Dictionary for common contractions
CONTRACTIONS = {
    "is not": "isn't", "are not": "aren't", "cannot": "can't", "could not": "couldn't",
    "did not": "didn't", "does not": "doesn't", "do not": "don't", "had not": "hadn't",
    "has not": "hasn't", "have not": "haven't", "he is": "he's", "he will": "he'll",
    "how is": "how's", "i am": "I'm", "i have": "I've", "i will": "I'll", "i would": "I'd",
    "it is": "it's", "it will": "it'll", "must not": "mustn't", "she is": "she's",
    "she will": "she'll", "should not": "shouldn't", "that is": "that's", "there is": "there's",
    "they are": "they're", "they have": "they've", "they will": "they'll", "was not": "wasn't",
    "we are": "we're", "we have": "we've", "we will": "we'll", "were not": "weren't",
    "what is": "what's", "where is": "where's", "who is": "who's", "who will": "who'll",
    "will not": "won't", "would not": "wouldn't", "you are": "you're", "you have": "you've",
    "you will": "you'll", "you would": "you'd"
}

# Dictionary for simplifying formal/AI-like words
WORD_REPLACEMENTS = {
    "utilize": "use", "facilitate": "help", "in order to": "to",
    "as a result of": "because of", "subsequently": "later", "furthermore": "also",
    "nevertheless": "but", "in conclusion": "so", "it is imperative": "we need to",
    "it is important to note": "remember", "one must consider": "think about"
}

# List of conversational openers to add personality
CONVERSATIONAL_OPENERS = [
    "Honestly, ", "Well, ", "You see, ", "Basically, ", "Look, ", 
    "The thing is, ", "Alright, so ", "To be fair, "
]

def apply_human_touch(text):
    """
    Applies a set of rules to make text sound more human.
    This is where the techniques you described are implemented.
    """
    # 1. Replace formal words with simpler ones
    for old, new in WORD_REPLACEMENTS.items():
        text = text.replace(old, new)

    # 2. Add contractions
    for old, new in CONTRACTIONS.items():
        # Use case-insensitive replacement for broader matching
        text = text.replace(f" {old.capitalize()} ", f" {new.capitalize()} ")
        text = text.replace(f" {old} ", f" {new} ")

    # 3. Add a conversational opener (with a 50% chance)
    if random.random() < 0.5:
        opener = random.choice(CONVERSATIONAL_OPENERS)
        # Avoid adding if the text already starts conversationally
        if not text.lstrip().lower().startswith(tuple(o.lower() for o in CONVERSATIONAL_OPENERS)):
            text = opener + text

    return text

# --- End of New Humanizer Logic ---


# Function to humanize text
def humanize_text():
    user_input = input_text.get("1.0", tk.END).strip()
    if not user_input:
        messagebox.showwarning("Empty Input", "Please enter some text first!")
        return

    humanize_button.config(state=tk.DISABLED, text="⏳ Processing...")

    def process():
        try:
            # Step 1: Paraphrase using the T5 model for major restructuring
            paraphraser = pipeline(
                "text2text-generation",
                model="Vamsi/T5_Paraphrase_Paws",
                framework="pt",
                from_pt=True
            )

            paraphrased_result = paraphraser("paraphrase: " + user_input + " </s>", max_length=512, num_return_sequences=1)
            paraphrased_text = paraphrased_result[0]['generated_text']

            # Step 2: Apply specific humanizing rules
            humanized_text = apply_human_touch(paraphrased_text)

            # Step 3: (Optional) Correct grammar if the user selected it
            if correct_grammar_var.get():
                blob = TextBlob(humanized_text)
                humanized_text = str(blob.correct())

            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, humanized_text)
        except Exception as e:
            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, f"❌ Error: Could not process text. Please check your internet connection or try again.\n\nDetails: {e}")
        finally:
            humanize_button.config(state=tk.NORMAL, text="✨ Humanize")

    threading.Thread(target=process, daemon=True).start()

# Copy text
def copy_text():
    app.clipboard_clear()
    app.clipboard_append(output_text.get("1.0", tk.END).strip())
    messagebox.showinfo("Copied", "Text copied to clipboard!")

# Cut text
def cut_text():
    copy_text()
    output_text.delete("1.0", tk.END)

# Download text
def download_text():
    content = output_text.get("1.0", tk.END).strip()
    if not content:
        messagebox.showwarning("Empty Text", "There's no text to download!")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        messagebox.showinfo("Saved", f"Text saved to {file_path}")

# --- GUI Setup (Mostly unchanged, with one addition) ---

# Create main window
app = tk.Tk()
app.title("✨ AI Text Humanizer")
app.geometry("800x650") # Increased height slightly for the new checkbox
app.config(bg="#1e1e2f")

# Title Label
title_label = tk.Label(app, text="✨ AI Text Humanizer", font=("Helvetica", 26, "bold"),
                       bg="#1e1e2f", fg="#81ecec")
title_label.pack(pady=20)

# Input Text Field
input_text = scrolledtext.ScrolledText(app, height=7, font=("Arial", 14),
                                       bg="#2d2d44", fg="#f5f6fa",
                                       insertbackground="#81ecec",
                                       relief=tk.FLAT, wrap=tk.WORD)
input_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
input_text.insert(tk.END, "Enter AI-generated text here...")


# Frame for button and options
humanize_frame = tk.Frame(app, bg="#1e1e2f")
humanize_frame.pack(pady=10)

# Humanize Button
humanize_button = tk.Button(humanize_frame, text="✨ Humanize", font=("Helvetica", 16, "bold"),
                            bg="#00cec9", fg="#1e1e2f",
                            activebackground="#81ecec", activeforeground="#1e1e2f",
                            relief=tk.FLAT, padx=15, pady=8, command=humanize_text)
humanize_button.pack(side=tk.LEFT, padx=10)

# ** NEW ** Optional Grammar Correction Checkbox
correct_grammar_var = tk.BooleanVar()
correct_grammar_check = tk.Checkbutton(humanize_frame, text="Correct Grammar Post-Humanizing",
                                       variable=correct_grammar_var, font=("Helvetica", 10),
                                       bg="#1e1e2f", fg="#f5f6fa", selectcolor="#2d2d44",
                                       activebackground="#1e1e2f", activeforeground="#81ecec")
correct_grammar_check.pack(side=tk.LEFT, padx=10)


# Output Text Field
output_text = scrolledtext.ScrolledText(app, height=7, font=("Arial", 14),
                                        bg="#2d2d44", fg="#f5f6fa",
                                        insertbackground="#81ecec",
                                        relief=tk.FLAT, wrap=tk.WORD)
output_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

# Button Group Frame
button_frame = tk.Frame(app, bg="#1e1e2f")
button_frame.pack(pady=10)

# Small attractive buttons
def styled_button(master, text, command):
    btn = tk.Button(master, text=text, font=("Helvetica", 12, "bold"),
                    bg="#6c5ce7", fg="#ffffff",
                    activebackground="#81ecec", activeforeground="#1e1e2f",
                    relief=tk.FLAT, padx=12, pady=6, command=command)
    btn.pack(side=tk.LEFT, padx=8)
    
    # Hover effects
    def on_enter(e):
        btn.config(bg="#00cec9", fg="#1e1e2f")
    def on_leave(e):
        btn.config(bg="#6c5ce7", fg="#ffffff")
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn

copy_btn = styled_button(button_frame, "📋 Copy", copy_text)
cut_btn = styled_button(button_frame, "✂️ Cut", cut_text)
download_btn = styled_button(button_frame, "💾 Download", download_text)

# Run the App
app.mainloop()