"""
Main entry point for ArtoText application
"""
import tkinter as tk
from text_editor import TextEditor


def main():
    """
    Main function to run the ArtoText application
    """
    root = tk.Tk()
    app = TextEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
