import tkinter as tk
from tkinter import messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import pandas as pd

class CSVDropApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Loader (Click or Drag & Drop)")
        self.root.geometry("700x500")
        self.root.configure(bg="#f5f5f7")

        # --- Dual-Purpose Button (Click OR Drag & Drop) ---
        self.drop_button = tk.Button(
            root, 
            text="📥 Click to Browse or Drag & Drop CSV here", 
            bg="#ffffff", 
            fg="#333333",
            font=("Helvetica", 12, "bold"),
            relief="groove", 
            bd=2,
            cursor="hand2",
            command=self.open_file_dialog  # Triggers when clicked
        )
        self.drop_button.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Register the button as a drag-and-drop target
        self.drop_button.drop_target_register(DND_FILES)
        self.drop_button.dnd_bind('<<Drop>>', self.handle_drop)

        # --- Data Preview UI ---
        self.preview_label = tk.Label(
            root, 
            text="Data Preview (First 5 Rows):", 
            font=("Helvetica", 11, "bold"), 
            bg="#f5f5f7", 
            fg="#333333"
        )
        self.preview_label.pack(anchor="w", padx=20, pady=(10, 2))
        
        self.text_area = tk.Text(root, height=12, state='disabled', wrap='none', font=("Consolas", 10))
        self.text_area.pack(padx=20, pady=(0, 20), fill=tk.BOTH, expand=True)

    def open_file_dialog(self):
        """Handles the click event to browse files manually."""
        file_path = filedialog.askopenfilename(
            title="Select a CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:  # Proceed only if the user didn't cancel the dialog
            self.validate_and_load(file_path)

    def handle_drop(self, event):
        """Handles the event when a file is dragged and dropped onto the button."""
        files = self.root.tk.splitlist(event.data)
        if files:
            self.validate_and_load(files[0])

    def validate_and_load(self, file_path):
        """Validates that the file is a CSV and updates the UI."""
        if file_path.lower().endswith('.csv'):
            file_name = file_path.split('/')[-1]
            # Visual feedback on successful load
            self.drop_button.config(
                text=f"✅ Loaded: {file_name}\n(Click or drop another to replace)", 
                bg="#e8f5e9", 
                fg="#2e7d32"
            )
            self.process_csv(file_path)
        else:
            messagebox.showerror("Invalid File Type", "Please select or drop a valid .csv file.")

    def process_csv(self, file_path):
        """Reads the CSV file and displays it in the preview text area."""
        try:
            df = pd.read_csv(file_path)
            
            self.text_area.config(state='normal')
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, df.head(5).to_string(index=False))
            self.text_area.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Error Reading File", f"Could not read the CSV file.\n\nDetails: {e}")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = CSVDropApp(root)
    root.mainloop()