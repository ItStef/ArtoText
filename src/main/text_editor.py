"""
ArtoText - A simple desktop text editor
"""
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, ttk
import os


class TextEditor:
    """
    Main text editor class that creates and manages the UI
    """

    def __init__(self, root):
        self.root = root
        self.root.title("ArtoText - Text Editor")
        self.root.geometry("800x600")

        # Tab tracking: maps tab_id -> {'text_widget': widget, 'file_path': path, 'modified': bool}
        self.tabs = {}
        self.tab_counter = 0

        # Find functionality state
        self.find_dialog = None
        self.find_text = ""
        self.last_search_index = "1.0"
        self.find_status_label = None

        # Create menu bar
        self._create_menu_bar()

        # Create notebook for tabs
        self._create_notebook()

        # Create initial tab
        self._create_new_tab()

        # Set up keyboard shortcuts
        self._setup_keybindings()

    def _create_menu_bar(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self._new_file)
        self.file_menu.add_command(label="Open", command=self._open_file)
        self.file_menu.add_command(label="Save", command=self._save_file)
        self.file_menu.add_command(label="Close Tab", command=self._close_tab)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self._exit_app)

        # Edit menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Cut", command=self._cut_text)
        self.edit_menu.add_command(label="Copy", command=self._copy_text)
        self.edit_menu.add_command(label="Paste", command=self._paste_text)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Find", command=self._open_find_dialog)

        # View menu
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Zoom In", command=self._zoom_in)
        self.view_menu.add_command(label="Zoom Out", command=self._zoom_out)
        self.view_menu.add_command(label="Reset Zoom", command=self._reset_zoom)

    def _create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')
        self.notebook.enable_traversal()

        # Bind button clicks to handle tab selection and close button
        self.notebook.bind('<ButtonRelease-1>', self._on_tab_click)
        # Bind middle-click to close tab
        self.notebook.bind('<Button-2>', self._on_tab_middle_click)

    def _create_new_tab(self, content="", file_path=None):
        # Generate unique tab ID first
        tab_id = f"tab_{self.tab_counter}"
        self.tab_counter += 1

        tab_frame = tk.Frame(self.notebook)

        text_widget = scrolledtext.ScrolledText(
            tab_frame,
            wrap=tk.WORD,
            width=100,
            height=30,
            font=("Arial", self.current_font_size),
            undo=True,
            maxundo=-1
        )
        text_widget.pack(expand=True, fill='both')

        if content:
            text_widget.insert(1.0, content)

        # Track modified state
        text_widget.bind('<<Modified>>', lambda e, tid=tab_id: self._on_text_modified(tid))

        # Store tab info
        self.tabs[tab_id] = {
            'text_widget': text_widget,
            'file_path': file_path,
            'modified': False,
            'frame': tab_frame
        }

        # Add tab to notebook with close button in title
        tab_title = self._get_tab_title_with_close(tab_id)
        self.notebook.add(tab_frame, text=tab_title)
        self.notebook.select(tab_frame)

        return tab_id

    def _create_empty_state_tab(self):
        tab_id = f"tab_{self.tab_counter}"
        self.tab_counter += 1

        tab_frame = tk.Frame(self.notebook)

        # Create a centered label instead of text editor
        message_label = tk.Label(
            tab_frame,
            text="No Files Are Currently Open",
            font=("Arial", 14),
            fg="gray"
        )
        message_label.pack(expand=True)

        # Store tab info (no text_widget for empty state)
        self.tabs[tab_id] = {
            'text_widget': None,
            'file_path': None,
            'modified': False,
            'frame': tab_frame,
            'is_empty_state': True
        }

        # Add tab to notebook without close button
        self.notebook.add(tab_frame, text="No Files Open")
        self.notebook.select(tab_frame)

        return tab_id

    def _remove_empty_state_if_exists(self):
        for tab_id, tab_info in list(self.tabs.items()):
            if tab_info.get('is_empty_state', False):
                frame = tab_info['frame']
                for idx in range(self.notebook.index('end')):
                    if self.notebook.nametowidget(self.notebook.tabs()[idx]) == frame:
                        self.notebook.forget(idx)
                        break
                del self.tabs[tab_id]
                break

    def _get_tab_title_with_close(self, tab_id):
        title = self._get_tab_title(tab_id)
        return f"{title}  ✕"

    def _on_tab_click(self, event):
        # Check if click was on a tab
        try:
            clicked = self.notebook.tk.call(self.notebook._w, "identify", "tab", event.x, event.y)
            if clicked == "":
                return

            # Get the clicked tab
            tab_frame = self.notebook.nametowidget(self.notebook.tabs()[int(clicked)])

            # Find the tab_id for this frame
            for tab_id, tab_info in self.tabs.items():
                if tab_info['frame'] == tab_frame:
                    # Get tab text and check if click was on close button area
                    # Approximate: check if click is on right ~15% of tab
                    tab_bbox = self.notebook.bbox(int(clicked))
                    if tab_bbox:
                        tab_x, tab_y, tab_width, tab_height = tab_bbox
                        # If click is in the rightmost portion (where X is), close the tab
                        if event.x > tab_x + tab_width - 25:  # Approximate X button area
                            self._close_tab(tab_id)
                            # Prevent default tab selection when closing
                            return "break"
                    break
        except (tk.TclError, ValueError, IndexError):
            pass

    def _on_tab_middle_click(self, event):
        # Find which tab was clicked
        clicked = self.notebook.tk.call(self.notebook._w, "identify", "tab", event.x, event.y)
        if clicked != "":
            # Get the frame at that index
            tab_frame = self.notebook.nametowidget(self.notebook.tabs()[int(clicked)])
            # Find the tab_id for this frame
            for tab_id, tab_info in self.tabs.items():
                if tab_info['frame'] == tab_frame:
                    self._close_tab(tab_id)
                    break

    def _get_tab_title(self, tab_id):
        tab_info = self.tabs[tab_id]
        if tab_info['file_path']:
            title = os.path.basename(tab_info['file_path'])
        else:
            title = "Untitled"

        if tab_info['modified']:
            title = f"*{title}"

        return title

    def _on_text_modified(self, tab_id):
        if tab_id in self.tabs:
            widget = self.tabs[tab_id]['text_widget']
            if widget.edit_modified():
                self.tabs[tab_id]['modified'] = True
                self._update_tab_title(tab_id)
                widget.edit_modified(False)

    def _update_tab_title(self, tab_id):
        tab_info = self.tabs[tab_id]
        frame = tab_info['frame']
        new_title = self._get_tab_title_with_close(tab_id)

        for idx in range(self.notebook.index('end')):
            if self.notebook.nametowidget(self.notebook.tabs()[idx]) == frame:
                self.notebook.tab(idx, text=new_title)
                break

    def _get_current_tab_id(self):
        try:
            current_frame = self.notebook.select()
            if not current_frame:
                return None
            current_frame_widget = self.notebook.nametowidget(current_frame)
            for tab_id, tab_info in self.tabs.items():
                if tab_info['frame'] == current_frame_widget:
                    return tab_id
        except tk.TclError:
            pass
        return None

    def _get_current_text_widget(self):
        tab_id = self._get_current_tab_id()
        if tab_id:
            return self.tabs[tab_id]['text_widget']
        return None

    def _new_file(self):
        self._remove_empty_state_if_exists()
        self._create_new_tab()

    def _open_file(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file_handle:
                    content = file_handle.read()
                    self._remove_empty_state_if_exists()
                    self._create_new_tab(content=content, file_path=file_path)
            except OSError as error:
                messagebox.showerror("Open Error", f"Could not open file:\n{error}")

    def _save_file(self):
        tab_id = self._get_current_tab_id()
        if not tab_id:
            return

        tab_info = self.tabs[tab_id]

        # Don't save empty state tab
        if tab_info.get('is_empty_state', False):
            return

        file_path = tab_info['file_path']

        if not file_path:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )

        if file_path:
            try:
                text_widget = tab_info['text_widget']
                content = text_widget.get(1.0, tk.END)
                with open(file_path, "w", encoding="utf-8") as file_handle:
                    file_handle.write(content)

                tab_info['file_path'] = file_path
                tab_info['modified'] = False
                self._update_tab_title(tab_id)
            except OSError as error:
                messagebox.showerror("Save Error", f"Could not save file:\n{error}")

    def _close_tab(self, tab_id=None):
        if tab_id is None:
            tab_id = self._get_current_tab_id()

        if not tab_id or tab_id not in self.tabs:
            return

        tab_info = self.tabs[tab_id]

        # Don't allow closing empty state tab
        if tab_info.get('is_empty_state', False):
            return

        # Check if modified
        if tab_info['modified']:
            file_name = os.path.basename(tab_info['file_path']) if tab_info['file_path'] else "Untitled"
            response = messagebox.askyesnocancel(
                "Save Changes",
                f"Do you want to save changes to {file_name}?"
            )

            if response is None:  # Cancel
                return
            elif response:  # Yes - save
                # Save the file
                file_path = tab_info['file_path']
                if not file_path:
                    file_path = filedialog.asksaveasfilename(
                        defaultextension=".txt",
                        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
                    )

                if file_path:
                    try:
                        text_widget = tab_info['text_widget']
                        content = text_widget.get(1.0, tk.END)
                        with open(file_path, "w", encoding="utf-8") as file_handle:
                            file_handle.write(content)
                    except OSError as error:
                        messagebox.showerror("Save Error", f"Could not save file:\n{error}")
                        return
                else:
                    return  # User cancelled save dialog

        # Remove tab from notebook
        frame = tab_info['frame']
        for idx in range(self.notebook.index('end')):
            if self.notebook.nametowidget(self.notebook.tabs()[idx]) == frame:
                self.notebook.forget(idx)
                break

        # Remove from tracking
        del self.tabs[tab_id]

        # If no tabs left, create an empty state tab
        if len(self.tabs) == 0:
            self._create_empty_state_tab()

    def _exit_app(self):
        # Check all tabs for unsaved changes
        for tab_id in list(self.tabs.keys()):
            if self.tabs[tab_id]['modified']:
                # Select the tab with unsaved changes
                self.notebook.select(self.tabs[tab_id]['frame'])
                # Try to close it (will prompt for save)
                self._close_tab(tab_id)
                # If tab still exists, user cancelled
                if tab_id in self.tabs:
                    return
        self.root.quit()

    def _cut_text(self):
        text_widget = self._get_current_text_widget()
        if text_widget:
            try:
                text_widget.event_generate("<<Cut>>")
            except tk.TclError:
                pass

    def _copy_text(self):
        text_widget = self._get_current_text_widget()
        if text_widget:
            try:
                text_widget.event_generate("<<Copy>>")
            except tk.TclError:
                pass

    def _paste_text(self):
        text_widget = self._get_current_text_widget()
        if text_widget:
            try:
                text_widget.event_generate("<<Paste>>")
            except tk.TclError:
                pass

    def _undo_text(self):
        text_widget = self._get_current_text_widget()
        if text_widget:
            try:
                text_widget.edit_undo()
            except tk.TclError:
                pass

    def _redo_text(self):
        text_widget = self._get_current_text_widget()
        if text_widget:
            try:
                text_widget.edit_redo()
            except tk.TclError:
                pass

    def _open_find_dialog(self):
        text_widget = self._get_current_text_widget()
        if not text_widget:
            return

        if self.find_dialog is not None and self.find_dialog.winfo_exists():
            self.find_dialog.lift()
            self.find_dialog.focus()
            return

        self.find_dialog = tk.Toplevel(self.root)
        self.find_dialog.title("Find")
        self.find_dialog.geometry("400x120")
        self.find_dialog.resizable(False, False)

        # Make it stay on top
        self.find_dialog.transient(self.root)

        # Center the dialog relative to the main window
        self.find_dialog.update_idletasks()
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        dialog_width = 400
        dialog_height = 120
        x = main_x + (main_width - dialog_width) // 2
        y = main_y + (main_height - dialog_height) // 2
        self.find_dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        # Create frame for find controls
        find_frame = tk.Frame(self.find_dialog)
        find_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Search entry
        tk.Label(find_frame, text="Find:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.find_entry = tk.Entry(find_frame, width=30)
        self.find_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky='ew')
        self.find_entry.focus()

        # Bind Enter to find next and Shift+Enter to find previous
        self.find_entry.bind('<Return>', lambda e: self._find_next())
        self.find_entry.bind('<Shift-Return>', lambda e: self._find_previous())

        # Bind Escape to close dialog and clear highlighting
        self.find_dialog.bind('<Escape>', lambda e: self._close_find_dialog())
        self.find_entry.bind('<Escape>', lambda e: self._close_find_dialog())

        # Navigation buttons
        prev_button = tk.Button(find_frame, text="↑ Previous", command=self._find_previous)
        prev_button.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        next_button = tk.Button(find_frame, text="↓ Next", command=self._find_next)
        next_button.grid(row=1, column=2, padx=5, pady=5, sticky='ew')

        # Status label for "No instance found"
        self.find_status_label = tk.Label(find_frame, text="", fg="red", font=("Arial", 9))
        self.find_status_label.grid(row=2, column=0, columnspan=3, pady=(5, 0))

        find_frame.columnconfigure(1, weight=1)
        find_frame.columnconfigure(2, weight=1)

    def _close_find_dialog(self):
        text_widget = self._get_current_text_widget()
        if text_widget:
            text_widget.tag_remove("highlight", "1.0", tk.END)

        if self.find_dialog is not None and self.find_dialog.winfo_exists():
            self.find_dialog.destroy()
            self.find_dialog = None

        self.find_text = ""
        self.last_search_index = "1.0"

    def _find_next(self):
        text_widget = self._get_current_text_widget()
        if not text_widget:
            return

        if self.find_dialog is None or not self.find_dialog.winfo_exists():
            self._open_find_dialog()
            return

        search_term = self.find_entry.get()
        if not search_term:
            return

        # Clear status message
        if self.find_status_label:
            self.find_status_label.config(text="")

        # Clear previous highlighting
        text_widget.tag_remove("highlight", "1.0", tk.END)

        # If search term changed, start from beginning
        if search_term != self.find_text:
            self.find_text = search_term
            self.last_search_index = "1.0"

        # Search for the text starting from last position
        start_pos = self.last_search_index
        pos = text_widget.search(search_term, start_pos, tk.END)

        if pos:
            # Calculate end position
            end_pos = f"{pos}+{len(search_term)}c"

            # Highlight the found text
            text_widget.tag_configure("highlight", background="yellow", foreground="black")
            text_widget.tag_add("highlight", pos, end_pos)

            # Scroll to make the text visible
            text_widget.see(pos)

            # Update last search position for next search
            self.last_search_index = end_pos
        else:
            # No match found, wrap around to beginning
            pos = text_widget.search(search_term, "1.0", tk.END)
            if pos:
                end_pos = f"{pos}+{len(search_term)}c"
                text_widget.tag_configure("highlight", background="yellow", foreground="black")
                text_widget.tag_add("highlight", pos, end_pos)
                text_widget.see(pos)
                self.last_search_index = end_pos
            else:
                # No match found at all
                self.last_search_index = "1.0"
                if self.find_status_label:
                    self.find_status_label.config(text="No instance found")

    def _find_previous(self):
        text_widget = self._get_current_text_widget()
        if not text_widget:
            return

        if self.find_dialog is None or not self.find_dialog.winfo_exists():
            self._open_find_dialog()
            return

        search_term = self.find_entry.get()
        if not search_term:
            return

        # Clear status message
        if self.find_status_label:
            self.find_status_label.config(text="")

        # Clear previous highlighting
        text_widget.tag_remove("highlight", "1.0", tk.END)

        # If search term changed, start from end
        if search_term != self.find_text:
            self.find_text = search_term
            self.last_search_index = tk.END

        # Search backwards from current position
        if self.last_search_index == "1.0":
            start_pos = tk.END
        else:
            # Move back to start of current match, then search backwards
            start_pos = f"{self.last_search_index}-{len(search_term)}c"

        pos = text_widget.search(search_term, start_pos, "1.0", backwards=True)

        if pos:
            # Calculate end position
            end_pos = f"{pos}+{len(search_term)}c"

            # Highlight the found text
            text_widget.tag_configure("highlight", background="yellow", foreground="black")
            text_widget.tag_add("highlight", pos, end_pos)

            # Scroll to make the text visible
            text_widget.see(pos)

            # Update last search position
            self.last_search_index = pos
        else:
            # No match found, wrap around to end
            pos = text_widget.search(search_term, tk.END, "1.0", backwards=True)
            if pos:
                end_pos = f"{pos}+{len(search_term)}c"
                text_widget.tag_configure("highlight", background="yellow", foreground="black")
                text_widget.tag_add("highlight", pos, end_pos)
                text_widget.see(pos)
                self.last_search_index = pos
            else:
                # No match found at all
                self.last_search_index = tk.END
                if self.find_status_label:
                    self.find_status_label.config(text="No instance found")

    def _setup_keybindings(self):
        self.root.bind('<Control-s>', lambda e: self._save_file())
        self.root.bind('<Control-n>', lambda e: self._new_file())
        self.root.bind('<Control-x>', lambda e: self._close_tab())
        self.root.bind('<Control-z>', lambda e: self._undo_text())
        self.root.bind('<Control-y>', lambda e: self._redo_text())
        self.root.bind('<Control-f>', lambda e: self._open_find_dialog())

    def get_text(self):
        text_widget = self._get_current_text_widget()
        if text_widget:
            return text_widget.get(1.0, tk.END)
        return "\n"

    def set_text(self, content):
        text_widget = self._get_current_text_widget()
        if text_widget:
            text_widget.delete(1.0, tk.END)
            text_widget.insert(1.0, content)
