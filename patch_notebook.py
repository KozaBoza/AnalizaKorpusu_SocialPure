import json

notebook_path = 'analiza_polsl.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# 1. Update pip install cell
found_pip = False
for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        for i, line in enumerate(cell['source']):
            if 'pip install' in line and 'kaleido' not in line:
                cell['source'][i] = line.replace('google-generativeai', 'google-generativeai kaleido')
                found_pip = True
                print("Updated pip install cell.")
    if found_pip:
        break

# 2. Update imports cell
found_imports = False
for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        source_text = "".join(cell['source'])
        if 'import plotly.graph_objects as go' in source_text and 'pio.renderers.default' not in source_text:
            # Add configuration at the end of this cell
            extra_lines = [
                "\n",
                "# Konfiguracja Plotly dla eksportu do PDF/LaTeX (statyczne obrazy)\n",
                "import plotly.io as pio\n",
                "pio.renderers.default = \"png\"\n",
                "print(\"Plotly renderer set to: 'png'\")"
            ]
            cell['source'].extend(extra_lines)
            found_imports = True
            print("Updated imports cell with renderer config.")
    if found_imports:
        break

if not found_pip:
    print("Warning: Could not find pip install cell to update.")
if not found_imports:
    print("Warning: Could not find imports cell to update.")

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print("Notebook patched successfully.")
