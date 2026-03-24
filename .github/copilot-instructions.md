# ArtoText — Copilot Instructions

## What this project is
ArtoText is a desktop text editor application. It allows users to open, edit, and save text files.

## Language & Framework
- Language: [Python]
- UI Framework: [Tkinter]
- Build Tool: [pip]

## Code Style Rules
- Use meaningful variable names — no single letters except loop counters
- Every new feature must have at least one unit test
- Keep methods short (under 30 lines if possible)
- Add a comment above every public method explaining what it does
- Only write comments when the code itself is not self-explanatory or the name of the method is not self-explanatory
- Write short comments for things that a reader out of context would not be able to guess, only when it isnt self-explanatory

## Project Structure
- `src/main/` — All main application source code
- `src/test/` — All unit tests
- `resources/` — Icons, stylesheets, config files

## Things you must NEVER do
- Do not delete or rename existing public methods without asking
- Do not change the `config/` directory
- Do not add external dependencies without noting them in the PR description or asking