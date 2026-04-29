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

    def test_view_menu_exists(self):
        if not self.display_available:
            self.skipTest("No display available")
        self.assertIsNotNone(self.editor.view_menu)

    def test_zoom_in(self):
        if not self.display_available:
            self.skipTest("No display available")
        initial_font_size = self.editor.current_font_size
        self.editor._zoom_in()
        self.assertGreater(self.editor.current_font_size, initial_font_size)

    def test_zoom_out(self):
        if not self.display_available:
            self.skipTest("No display available")
        initial_font_size = self.editor.current_font_size
        self.editor._zoom_out()
        self.assertLess(self.editor.current_font_size, initial_font_size)

    def test_reset_zoom(self):
        if not self.display_available:
            self.skipTest("No display available")
        self.editor._zoom_in()
        self.editor._zoom_in()
        self.assertNotEqual(self.editor.current_font_size, 12)
        self.editor._reset_zoom()
        self.assertEqual(self.editor.current_font_size, 12)

    def test_zoom_in_keyboard_shortcut(self):
        if not self.display_available:
            self.skipTest("No display available")
        initial_font_size = self.editor.current_font_size
        self.root.event_generate('<Control-equal>')
        self.root.update()
        self.assertGreater(self.editor.current_font_size, initial_font_size)

    def test_zoom_out_keyboard_shortcut(self):
        if not self.display_available:
            self.skipTest("No display available")
        initial_font_size = self.editor.current_font_size
        self.root.event_generate('<Control-minus>')
        self.root.update()
        self.assertLess(self.editor.current_font_size, initial_font_size)

    def test_zoom_applies_to_all_tabs(self):
        if not self.display_available:
            self.skipTest("No display available")
        # Create multiple tabs
        self.editor._new_file()
        self.editor._new_file()

        # Zoom in
        self.editor._zoom_in()

        # Check all tabs have the same font size
        for tab_id, tab_info in self.editor.tabs.items():
            text_widget = tab_info.get('text_widget')
            if text_widget:
                font = text_widget.cget('font')
                # Font can be returned as a string or tuple, need to parse it
                if isinstance(font, str):
                    # Font is returned as string like "Arial 13"
                    font_size = int(font.split()[-1])
                else:
                    font_size = font[1]
                self.assertEqual(font_size, self.editor.current_font_size)

    def test_zoom_in_limit(self):
        if not self.display_available:
            self.skipTest("No display available")
        # Zoom in multiple times to exceed limit
        for _ in range(50):
            self.editor._zoom_in()
        # Should not exceed 60pt (500% of 12pt)
        self.assertLessEqual(self.editor.current_font_size, 60)

    def test_zoom_out_limit(self):
        if not self.display_available:
            self.skipTest("No display available")
        # Zoom out multiple times to reach minimum
        for _ in range(50):
            self.editor._zoom_out()
        # Should not go below 1pt (can't be 0)
        self.assertGreater(self.editor.current_font_size, 0)

    def test_zoom_in_from_minimum(self):
        if not self.display_available:
            self.skipTest("No display available")
        # Zoom out to minimum
        for _ in range(50):
            self.editor._zoom_out()
        min_size = self.editor.current_font_size
        # Should be able to zoom back in from minimum
        self.editor._zoom_in()
        self.assertGreater(self.editor.current_font_size, min_size)

    def test_find_dialog_opens(self):
        if not self.display_available:
            self.skipTest("No display available")
        self.editor._open_find_dialog()
        self.assertIsNotNone(self.editor.find_dialog)
        self.assertTrue(self.editor.find_dialog.winfo_exists())
        self.editor._close_find_dialog()

    def test_find_dialog_keyboard_shortcut(self):
        if not self.display_available:
            self.skipTest("No display available")
        self.root.event_generate('<Control-f>')
        self.root.update()
        self.assertIsNotNone(self.editor.find_dialog)
        self.assertTrue(self.editor.find_dialog.winfo_exists())
        self.editor._close_find_dialog()

    def test_find_text_basic(self):
        if not self.display_available:
            self.skipTest("No display available")
        test_text = "Hello World\nThis is a test\nHello again"
        self.editor.set_text(test_text)
        self.editor._open_find_dialog()
        self.editor.find_entry.insert(0, "Hello")
        self.editor._find_next()
        text_widget = self.editor._get_current_text_widget()
        # Check that search tag exists
        ranges = text_widget.tag_ranges("search")
        self.assertGreater(len(ranges), 0)
        self.editor._close_find_dialog()

    def test_find_text_case_insensitive(self):
        if not self.display_available:
            self.skipTest("No display available")
        test_text = "Hello World"
        self.editor.set_text(test_text)
        self.editor._open_find_dialog()
        self.editor.find_entry.insert(0, "hello")
        self.editor._find_next()
        text_widget = self.editor._get_current_text_widget()
        ranges = text_widget.tag_ranges("search")
        self.assertGreater(len(ranges), 0)
        self.editor._close_find_dialog()

    def test_find_text_wraps_around(self):
        if not self.display_available:
            self.skipTest("No display available")
        test_text = "First match\nSecond match"
        self.editor.set_text(test_text)
        self.editor._open_find_dialog()
        self.editor.find_entry.insert(0, "match")
        # Find first occurrence
        self.editor._find_next()
        # Find second occurrence
        self.editor._find_next()
        # Should wrap around to first again
        self.editor._find_next()
        text_widget = self.editor._get_current_text_widget()
        ranges = text_widget.tag_ranges("search")
        self.assertGreater(len(ranges), 0)
        self.editor._close_find_dialog()

    def test_find_text_not_found(self):
        if not self.display_available:
            self.skipTest("No display available")
        test_text = "Hello World"
        self.editor.set_text(test_text)
        self.editor._open_find_dialog()
        self.editor.find_entry.insert(0, "NotFound")
        # Should not raise an error
        self.editor._find_next()
        self.editor._close_find_dialog()

    def test_find_previous(self):
        if not self.display_available:
            self.skipTest("No display available")
        test_text = "First match\nSecond match\nThird match"
        self.editor.set_text(test_text)
        self.editor._open_find_dialog()
        self.editor.find_entry.insert(0, "match")
        # Find forward twice
        self.editor._find_next()
        self.editor._find_next()
        # Then go backward
        self.editor._find_previous()
        text_widget = self.editor._get_current_text_widget()
        ranges = text_widget.tag_ranges("search")
        self.assertGreater(len(ranges), 0)
        self.editor._close_find_dialog()

    def test_close_find_dialog_removes_highlight(self):
        if not self.display_available:
            self.skipTest("No display available")
        test_text = "Hello World"
        self.editor.set_text(test_text)
        self.editor._open_find_dialog()
        self.editor.find_entry.insert(0, "Hello")
        self.editor._find_next()
        self.editor._close_find_dialog()
        text_widget = self.editor._get_current_text_widget()
        ranges = text_widget.tag_ranges("search")
        self.assertEqual(len(ranges), 0)

    def test_find_dialog_reopen_brings_to_front(self):
        if not self.display_available:
            self.skipTest("No display available")
        self.editor._open_find_dialog()
        first_dialog = self.editor.find_dialog
        # Try to open again
        self.editor._open_find_dialog()
        # Should be the same dialog
        self.assertIs(self.editor.find_dialog, first_dialog)
        self.editor._close_find_dialog()


if __name__ == '__main__':
    unittest.main()
