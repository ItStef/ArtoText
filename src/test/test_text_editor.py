"""
Unit tests for the TextEditor class
"""
import unittest
import tkinter as tk
import sys
import os

# Add the main module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'main'))
from text_editor import TextEditor


class TestTextEditor(unittest.TestCase):
    """
    Test cases for the TextEditor class
    """

    def setUp(self):
        try:
            self.root = tk.Tk()
            self.editor = TextEditor(self.root)
            self.display_available = True
        except tk.TclError:
            # No display available, skip GUI tests
            self.display_available = False

    def tearDown(self):
        if self.display_available:
            self.root.destroy()

    def test_initialization(self):
        if not self.display_available:
            self.skipTest("No display available")
        self.assertIsNotNone(self.editor)
        self.assertIsNotNone(self.editor.text_area)
        self.assertIsNotNone(self.editor.menu_bar)
        self.assertEqual(self.root.title(), "ArtoText - Text Editor")

    def test_get_text_empty(self):
        if not self.display_available:
            self.skipTest("No display available")
        text = self.editor.get_text()
        # Note: Tkinter Text widget adds a newline at the end
        self.assertEqual(text, "\n")

    def test_set_and_get_text(self):
        if not self.display_available:
            self.skipTest("No display available")
        test_content = "Hello, ArtoText!"
        self.editor.set_text(test_content)
        retrieved_text = self.editor.get_text()
        # Remove the trailing newline that Tkinter adds
        self.assertEqual(retrieved_text.rstrip('\n'), test_content)

    def test_new_file_clears_text(self):
        if not self.display_available:
            self.skipTest("No display available")
        self.editor.set_text("Some content")
        self.editor._new_file()
        text = self.editor.get_text()
        self.assertEqual(text, "\n")

    def test_menu_bar_exists(self):
        if not self.display_available:
            self.skipTest("No display available")
        self.assertIsNotNone(self.editor.menu_bar)
        self.assertIsNotNone(self.editor.file_menu)
        self.assertIsNotNone(self.editor.edit_menu)

    def test_text_area_properties(self):
        if not self.display_available:
            self.skipTest("No display available")
        self.assertEqual(self.editor.text_area.cget("wrap"), tk.WORD)
        self.assertIsNotNone(self.editor.text_area)


    def test_save_file_writes_content(self):
        if not self.display_available:
            self.skipTest("No display available")
        import tempfile
        import os
        from unittest.mock import patch

        test_content = "Save this content to file."
        self.editor.set_text(test_content)

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with patch("tkinter.filedialog.asksaveasfilename", return_value=tmp_path):
                self.editor._save_file()

            with open(tmp_path, "r", encoding="utf-8") as file_handle:
                saved = file_handle.read()

            self.assertEqual(saved.rstrip('\n'), test_content)
        finally:
            os.unlink(tmp_path)

    def test_save_file_cancelled_does_nothing(self):
        if not self.display_available:
            self.skipTest("No display available")
        from unittest.mock import patch

        with patch("tkinter.filedialog.asksaveasfilename", return_value=""):
            # Should not raise any error when dialog is cancelled
            self.editor._save_file()


if __name__ == '__main__':
    unittest.main()
