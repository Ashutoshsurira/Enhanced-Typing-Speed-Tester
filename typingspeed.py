import tkinter as tk, time, threading, random, winsound, pyttsx3

# Load categorized paragraphs
def load_paragraphs_by_level(file="paragraphs.txt"):
    levels = {"Easy": [], "Medium": [], "Hard": []}
    try:
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                for key in levels:
                    if line.startswith(f"{key}:"):
                        levels[key].append(line[len(key)+1:].strip())
    except FileNotFoundError:
        levels["Easy"] = ["The sun is bright today."]
        levels["Medium"] = ["The quick brown fox jumps over the lazy dog."]
        levels["Hard"] = ["Artificial intelligence is transforming technology."]
    return levels

# Setup
tts = pyttsx3.init(); tts.setProperty('rate', 110)
tool = language_tool_python.LanguageTool('en-US')
def speak(text): threading.Thread(target=lambda: (tts.say(text), tts.runAndWait())).start()
def normalize(text): return ' '.join(text.lower().strip().split())

class TypingSpeedTester:
    def __init__(self, root):
        self.root, self.levels = root, load_paragraphs_by_level()
        self.level = tk.StringVar(value="Easy")
        self.start_time, self.timer_running = None, False
        self.setup_ui()
        self.set_paragraph()

    def setup_ui(self):
        self.root.title("Enhanced Typing Speed Tester")
        self.root.geometry("800x750")
        tk.Label(self.root, text="Enhanced Typing Speed Tester", font=("Arial", 20, "bold")).pack(pady=10)
        frame = tk.Frame(self.root)
        tk.Label(frame, text="Select Level:", font=("Arial", 12)).pack(side=tk.LEFT)
        [tk.Radiobutton(frame, text=lvl, variable=self.level, value=lvl, command=self.set_paragraph).pack(side=tk.LEFT) for lvl in self.levels]
        frame.pack(pady=5)
        self.timer_lbl = tk.Label(self.root, text="Timer: 0.0 sec", font=("Arial", 12, "bold")); self.timer_lbl.pack()
        tk.Button(self.root, text="🔊 Dictate", command=lambda: speak(self.text)).pack(pady=5)
        self.text_lbl = tk.Label(self.root, wraplength=750, font=("Arial", 14)); self.text_lbl.pack(pady=15)
        self.input = tk.Text(self.root, height=6, font=("Arial", 14)); self.input.pack(pady=10)
        self.input.bind("<KeyRelease>", self.key_events)
        self.input.bind("<Return>", self.enter_submit)
        bframe = tk.Frame(self.root)
        tk.Button(bframe, text="Submit", command=self.submit).pack(side=tk.LEFT, padx=10)
        tk.Button(bframe, text="Next Paragraph", command=self.set_paragraph).pack(side=tk.LEFT, padx=10)
        bframe.pack(pady=5)
        self.result_lbl = tk.Label(self.root, font=("Arial", 12)); self.result_lbl.pack(pady=5)
        self.suggest_lbl = tk.Label(self.root, font=("Arial", 11, "italic")); self.suggest_lbl.pack()
        self.feedback = tk.Text(self.root, height=5, font=("Arial", 11), fg="darkred"); self.feedback.pack(pady=5)

    def set_paragraph(self):
        level_texts = self.levels[self.level.get()]
        self.text = random.choice(level_texts) if level_texts else "No paragraph available."
        self.text_lbl.config(text=self.text)
        self.input.delete("1.0", tk.END)
        self.feedback.delete("1.0", tk.END)
        self.input.tag_remove("mistake", "1.0", tk.END)
        self.result_lbl.config(text=""); self.suggest_lbl.config(text="")
        self.elapsed = 0; self.timer_lbl.config(text="Timer: 0.0 sec")

    def start_timer(self):
        if not self.timer_running:
            self.start_time = time.time()
            self.timer_running = True
            self.update_timer()
            winsound.Beep(1000, 200)

    def update_timer(self):
        if self.timer_running:
            self.elapsed = time.time() - self.start_time
            self.timer_lbl.config(text=f"Timer: {self.elapsed:.1f} sec")
            self.root.after(100, self.update_timer)

    def key_events(self, event):
        if event.keysym == "space": self.start_timer()
        self.highlight_errors()
        if normalize(self.input.get("1.0", tk.END)) == normalize(self.text):
            self.timer_running = False
            winsound.Beep(600, 300)
            self.show_results()

    def enter_submit(self, _): self.submit(); return "break"
    def submit(self): self.timer_running = False; winsound.Beep(600, 300); self.show_results()

    def highlight_errors(self):
        self.input.tag_remove("mistake", "1.0", tk.END)
        typed, ref = self.input.get("1.0", tk.END).strip().split(), self.text.strip().split()
        for i, word in enumerate(typed):
            if i >= len(ref) or word != ref[i]:
                start = f"1.0 + {sum(len(w)+1 for w in typed[:i])} chars"
                end = f"1.0 + {sum(len(w)+1 for w in typed[:i+1])} chars"
                self.input.tag_add("mistake", start, end)
        self.input.tag_config("mistake", foreground="red")

    def show_results(self):
        typed = self.input.get("1.0", tk.END).strip()
        words = typed.split(); time_taken = self.elapsed
        speed = len(words) / (time_taken / 60) if time_taken else 0
        matches = tool.check(typed); errors = len(matches)
        accuracy = max(0, 100 - (errors / max(1, len(words))) * 100)
        self.result_lbl.config(text=f"Time: {time_taken:.1f}s | Speed: {speed:.2f} WPM | Accuracy: {accuracy:.2f}% | Errors: {errors}")
        self.feedback.delete("1.0", tk.END)
        self.feedback.insert(tk.END, "Grammar Feedback:\n" if errors else "Great! No grammar issues found.\n")
        [self.feedback.insert(tk.END, f"- {m.message}\n") for m in matches[:5]]

        lvl, suggestion = self.level.get(), "Keep practicing to improve your skills!"
        if lvl == "Easy" and accuracy > 90 and speed > 30:
            suggestion = "Good job! Try Medium level."
            self.level.set("Medium")
        elif lvl == "Medium" and accuracy > 90 and speed > 35:
            suggestion = "Great! Try Hard level."
            self.level.set("Hard")
        elif lvl == "Hard" and accuracy < 70:
            suggestion = "Consider practicing Medium level."
            self.level.set("Medium")
        self.suggest_lbl.config(text=suggestion)

# Run the app
if __name__ == '__main__':
    root = tk.Tk()
    TypingSpeedTester(root)
    root.mainloop()