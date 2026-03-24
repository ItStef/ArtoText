# ArtoText
Text Editor App

This app is a practice project for learning about Github Copilot Agent system.

## Features

- Basic text editing with a scrollable text area
- Menu bar with File and Edit menus
- New, Open, Save operations (Save opens a file dialog to choose location; Open to be implemented)
- Cut, Copy, Paste functionality
- Clean and simple UI built with Tkinter

## Requirements

- Python 3.x
- Tkinter (usually comes with Python)

## Installation

No external dependencies required. Tkinter is included with most Python installations.

## Running the Application

To run the ArtoText editor:

```bash
cd src/main
python3 main.py
```

## Running Tests

To run the unit tests:

```bash
cd src/test
python3 test_text_editor.py
```

## Project Structure

- `src/main/` — All main application source code
  - `main.py` — Application entry point
  - `text_editor.py` — Main TextEditor class
- `src/test/` — All unit tests
  - `test_text_editor.py` — Tests for TextEditor class
- `resources/` — Icons, stylesheets, config files (to be added)