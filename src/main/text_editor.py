"""
ArtoText - A simple desktop text editor
"""
import tkinter as tk
from tkinter import scrolledtext


class TextEditor:
    """
    Main text editor class that creates and manages the UI
    """

    def __init__(self, root):
        """
        Initialize the text editor with a root Tkinter window

        Args:
            root: The root Tkinter window
        """
        self.root = root
        self.root.title("ArtoText - Text Editor")
        self.root.geometry("800x600")

        # Create menu bar
        self._create_menu_bar()

        # Create text area
        self._create_text_area()

    def _create_menu_bar(self):
        """
        Create the menu bar with File and Edit menus
        """
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
        """
        Create the main text editing area
        """
        self.text_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            width=100,
            height=30,
            font=("Arial", 12)
        )
        self.text_area.pack(expand=True, fill='both')

    def _new_file(self):
        """
        Create a new file by clearing the text area
        """
        self.text_area.delete(1.0, tk.END)

    def _open_file(self):
        """
        Open a file (placeholder for future implementation)
        """
        pass

    def _save_file(self):
        """
        Save a file (placeholder for future implementation)
        """
        pass

    def _exit_app(self):
        """
        Exit the application
        """
        self.root.quit()

    def _cut_text(self):
        """
        Cut selected text
        """
        try:
            self.text_area.event_generate("<<Cut>>")
        except tk.TclError:
            pass

    def _copy_text(self):
        """
        Copy selected text
        """
        try:
            self.text_area.event_generate("<<Copy>>")
        except tk.TclError:
            pass

    def _paste_text(self):
        """
        Paste text from clipboard
        """
        try:
            self.text_area.event_generate("<<Paste>>")
        except tk.TclError:
            pass

    def get_text(self):
        """
        Get all text from the text area

        Returns:
            str: All text content
        """
        return self.text_area.get(1.0, tk.END)

    def set_text(self, content):
        """
        Set text content in the text area

        Args:
            content: Text content to set
        """
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, content)
