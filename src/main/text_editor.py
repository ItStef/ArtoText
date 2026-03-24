"""
ArtoText - A simple desktop text editor
"""
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox


class TextEditor:
    """
    Main text editor class that creates and manages the UI
    """

    def __init__(self, root):
        self.root = root
        self.root.title("ArtoText - Text Editor")
        self.root.geometry("800x600")

        # Create menu bar
        self._create_menu_bar()

        # Create text area
        self._create_text_area()

    def _create_menu_bar(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self._new_file)
        self.file_menu.add_command(label="Open", command=self._open_file)
        self.file_menu.add_command(label="Save", command=self._save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self._exit_app)

        # Edit menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Cut", command=self._cut_text)
        self.edit_menu.add_command(label="Copy", command=self._copy_text)
        self.edit_menu.add_command(label="Paste", command=self._paste_text)

    def _create_text_area(self):
        self.text_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            width=100,
            height=30,
            font=("Arial", 12)
        )
        self.text_area.pack(expand=True, fill='both')

    def _new_file(self):
        self.text_area.delete(1.0, tk.END)

    def _open_file(self):
        pass

    def _save_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file_handle:
                    file_handle.write(self.get_text())
            except OSError as error:
                messagebox.showerror("Save Error", f"Could not save file:\n{error}")

    def _exit_app(self):
        self.root.quit()

    def _cut_text(self):
        try:
            self.text_area.event_generate("<<Cut>>")
        except tk.TclError:
            pass

    def _copy_text(self):
        try:
            self.text_area.event_generate("<<Copy>>")
        except tk.TclError:
            pass

    def _paste_text(self):
        try:
            self.text_area.event_generate("<<Paste>>")
        except tk.TclError:
            pass

    def get_text(self):
        return self.text_area.get(1.0, tk.END)

    def set_text(self, content):
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, content)
