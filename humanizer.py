import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from transformers import pipeline
from textblob import TextBlob
import threading
import nltk

# Download required data for TextBlob
nltk.download('punkt')

# Function to humanize text
def humanize_text():
    user_input = input_text.get("1.0", tk.END).strip()
    if not user_input:
        messagebox.showwarning("Empty Input", "Please enter some text first!")
        return

    humanize_button.config(state=tk.DISABLED, text="⏳ Processing...")

    def process():
        try:
            paraphraser = pipeline("text2text-generation", model="ramsrigouthamg/t5_paraphraser")
            paraphrased = paraphraser("paraphrase: " + user_input + " </s>", max_length=200, num_return_sequences=1)
            paraphrased_text = paraphrased[0]['generated_text']

            blob = TextBlob(paraphrased_text)
            corrected_text = str(blob.correct())

            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, corrected_text)
        except Exception as e:
            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, f"❌ Error: {e}")
        finally:
            humanize_button.config(state=tk.NORMAL, text="✨ Humanize")

    threading.Thread(target=process).start()

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

# Create main window
app = tk.Tk()
app.title("✨ AI Text Humanizer")
app.geometry("800x600")
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

# Humanize Button
humanize_button = tk.Button(app, text="✨ Humanize", font=("Helvetica", 16, "bold"),
                            bg="#00cec9", fg="#1e1e2f",
                            activebackground="#81ecec", activeforeground="#1e1e2f",
                            relief=tk.FLAT, padx=15, pady=8, command=humanize_text)
humanize_button.pack(pady=10)

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