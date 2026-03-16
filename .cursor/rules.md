# Project Rules

This is a Python Streamlit project with a modular architecture.

## Project Structure

app.py
Main Streamlit interface.

services/
Contains business logic modules:
- lectores.py → reads Excel files
- conciliacion.py → reconciliation logic
- exportador.py → export results

utils.py
Utility helper functions.

config.py
Configuration constants.

requirements.txt
Project dependencies.

## Architecture Rules

1. Do not restructure the project unless explicitly requested.
2. Keep business logic inside the `services` folder.
3. `app.py` should only orchestrate UI and call services.
4. Do not move functions between modules unless necessary.
5. Maintain backward compatibility with existing imports.

## Coding Rules

1. Avoid unnecessary refactoring.
2. Only change files required for the requested feature.
3. Prefer small incremental changes.
4. Keep functions readable and modular.

## Safety Rules

Before modifying code:

- Explain which files will be affected.
- Explain why the change is needed.
- Avoid breaking imports.

## Performance Rules

The application processes large Excel files (100k+ rows).

Prefer:
- pandas vectorized operations
- avoiding loops when possible
- memory-efficient operations.

## Streamlit Rules

- UI logic stays in `app.py`
- heavy processing must stay in `services`
