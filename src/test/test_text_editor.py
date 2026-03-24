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
        self.assertIsNotNone(self.editor.notebook)
        self.assertIsNotNone(self.editor.menu_bar)
        self.assertEqual(self.root.title(), "ArtoText - Text Editor")
        # Should have one initial tab
        self.assertEqual(len(self.editor.tabs), 1)

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
        initial_tab_count = len(self.editor.tabs)
        self.editor._new_file()
        # Should create a new tab instead of clearing
        self.assertEqual(len(self.editor.tabs), initial_tab_count + 1)

    def test_menu_bar_exists(self):
        if not self.display_available:
            self.skipTest("No display available")
        self.assertIsNotNone(self.editor.menu_bar)
        self.assertIsNotNone(self.editor.file_menu)
        self.assertIsNotNone(self.editor.edit_menu)

    def test_text_area_properties(self):
        if not self.display_available:
            self.skipTest("No display available")
        text_widget = self.editor._get_current_text_widget()
        self.assertIsNotNone(text_widget)
        self.assertEqual(text_widget.cget("wrap"), tk.WORD)


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

    def test_open_file_loads_content(self):
        if not self.display_available:
            self.skipTest("No display available")
        import tempfile
        import os
        from unittest.mock import patch

        test_content = "This is the content from the opened file."
        initial_tab_count = len(self.editor.tabs)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
            tmp.write(test_content)
            tmp_path = tmp.name

        try:
            with patch("tkinter.filedialog.askopenfilename", return_value=tmp_path):
                self.editor._open_file()

            # Should create a new tab
            self.assertEqual(len(self.editor.tabs), initial_tab_count + 1)
            loaded_text = self.editor.get_text()
            self.assertEqual(loaded_text.rstrip('\n'), test_content)
        finally:
            os.unlink(tmp_path)

    def test_open_file_cancelled_does_nothing(self):
        if not self.display_available:
            self.skipTest("No display available")
        from unittest.mock import patch

        self.editor.set_text("Original content")
        initial_tab_count = len(self.editor.tabs)

        with patch("tkinter.filedialog.askopenfilename", return_value=""):
            # Should not raise any error when dialog is cancelled
            self.editor._open_file()

        # Should not create a new tab
        self.assertEqual(len(self.editor.tabs), initial_tab_count)
        # Content should remain unchanged
        loaded_text = self.editor.get_text()
        self.assertEqual(loaded_text.rstrip('\n'), "Original content")

    def test_multiple_tabs(self):
        if not self.display_available:
            self.skipTest("No display available")
        # Should start with one tab
        self.assertEqual(len(self.editor.tabs), 1)

        # Create new tabs
        self.editor._new_file()
        self.assertEqual(len(self.editor.tabs), 2)

        self.editor._new_file()
        self.assertEqual(len(self.editor.tabs), 3)

    def test_close_tab(self):
        if not self.display_available:
            self.skipTest("No display available")
        # Create multiple tabs
        self.editor._new_file()
        self.editor._new_file()
        self.assertEqual(len(self.editor.tabs), 3)

        # Close one tab
        tab_id = self.editor._get_current_tab_id()
        self.editor._close_tab(tab_id)
        self.assertEqual(len(self.editor.tabs), 2)

    def test_close_last_tab_creates_new_one(self):
        if not self.display_available:
            self.skipTest("No display available")
        # Close the only tab
        tab_id = self.editor._get_current_tab_id()
        self.editor._close_tab(tab_id)

        # Should create an empty state tab
        self.assertEqual(len(self.editor.tabs), 1)
        # Check that it's an empty state tab
        remaining_tab_id = list(self.editor.tabs.keys())[0]
        self.assertTrue(self.editor.tabs[remaining_tab_id].get('is_empty_state', False))

    def test_keyboard_shortcut_save(self):
        if not self.display_available:
            self.skipTest("No display available")
        import tempfile
        import os
        from unittest.mock import patch

        test_content = "Test content for Ctrl+S"
        self.editor.set_text(test_content)

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with patch("tkinter.filedialog.asksaveasfilename", return_value=tmp_path):
                # Simulate Ctrl+S
                self.root.event_generate('<Control-s>')
                self.root.update()

            with open(tmp_path, "r", encoding="utf-8") as file_handle:
                saved = file_handle.read()

            self.assertEqual(saved.rstrip('\n'), test_content)
        finally:
            os.unlink(tmp_path)

    def test_keyboard_shortcut_new_file(self):
        if not self.display_available:
            self.skipTest("No display available")
        initial_tab_count = len(self.editor.tabs)
        # Simulate Ctrl+N
        self.root.event_generate('<Control-n>')
        self.root.update()
        self.assertEqual(len(self.editor.tabs), initial_tab_count + 1)

    def test_keyboard_shortcut_close_tab(self):
        if not self.display_available:
            self.skipTest("No display available")
        # Create extra tabs
        self.editor._new_file()
        self.editor._new_file()
        self.assertEqual(len(self.editor.tabs), 3)

        # Simulate Ctrl+X
        self.root.event_generate('<Control-x>')
        self.root.update()
        self.assertEqual(len(self.editor.tabs), 2)

    def test_keyboard_shortcut_undo(self):
        if not self.display_available:
            self.skipTest("No display available")
        text_widget = self.editor._get_current_text_widget()
        # Type some text
        text_widget.insert(1.0, "First line\n")
        text_widget.insert(tk.END, "Second line\n")
        content_before_undo = text_widget.get(1.0, tk.END)

        # Simulate Ctrl+Z (undo)
        self.root.event_generate('<Control-z>')
        self.root.update()

        content_after_undo = text_widget.get(1.0, tk.END)
        # Content should be different after undo
        self.assertNotEqual(content_before_undo, content_after_undo)

    def test_keyboard_shortcut_redo(self):
        if not self.display_available:
            self.skipTest("No display available")
        text_widget = self.editor._get_current_text_widget()
        # Type some text
        text_widget.insert(1.0, "Test text")
        content_after_insert = text_widget.get(1.0, tk.END)

        # Undo
        self.root.event_generate('<Control-z>')
        self.root.update()
        content_after_undo = text_widget.get(1.0, tk.END)

        # Redo (Ctrl+Y)
        self.root.event_generate('<Control-y>')
        self.root.update()
        content_after_redo = text_widget.get(1.0, tk.END)

        # After redo, content should match the state after insert
        self.assertEqual(content_after_insert, content_after_redo)


if __name__ == '__main__':
    unittest.main()
