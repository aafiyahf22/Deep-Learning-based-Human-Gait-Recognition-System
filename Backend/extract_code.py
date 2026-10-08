import json

with open("BiLSTM .ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

code_cells = [
    "".join(cell["source"])
    for cell in nb["cells"]
    if cell["cell_type"] == "code"
]

with open("BiLSTM.py", "w", encoding="utf-8") as f:
    f.write("\n\n".join(code_cells))
