# EC PDF to TXT Converter — Instructions

This script converts European Commission documents from PDF to clean plain text suitable for import into Taguette. It works with two types of documents:

- **Official Journal (OJ) documents** — Commission Communications, White Papers and similar acts published in the OJ (e.g. COM(2001) 428). These have repeating headers on every page with the date, language tag and journal reference.
- **Standard COM documents** — more recent Commission Communications published as standalone PDFs on EUR-Lex (e.g. COM(2025) 47). These have a cover page language marker and standalone page numbers instead.

In both cases, the script strips the noise, preserves page markers, joins wrapped lines within paragraphs, and marks footnotes clearly.

---

## Requirements

You need Python with the `pymupdf` library installed. If you have not installed it yet, run this in a Jupyter cell:

```python
!pip install pymupdf
```

---

## Setup

Place the script `convert_oj_pdf.py` and your PDF file(s) **in the same folder**. This is the simplest approach and avoids having to type full file paths.

If you prefer to keep them in separate folders, you can instead type the full path when prompted (see below).

---

## How to run it in Jupyter

Open a new cell and run:

```python
%run convert_oj_pdf.py
```

You will be prompted:

```
Enter PDF filename (e.g. COM(2025)47.pdf):
```

Type the filename exactly as it appears, including the `.pdf` extension, and press Enter. The script will save the output as a `.txt` file in the same folder, with the same name as the PDF.

For example: `COM(2025)47.pdf` → `COM(2025)47.txt`

---

## If your PDF is in a different folder

You can type the full path instead of just the filename. For example:

- On Windows: `C:\Users\YourName\Documents\COM(2025)47.pdf`
- On Mac/Linux: `/Users/YourName/Documents/COM(2025)47.pdf`

The output `.txt` file will be saved in the same folder as the PDF.

---

## Checking which folder Jupyter is working from

If you are unsure where Jupyter is currently looking for files, run this in a cell:

```python
import os
os.getcwd()
```

This prints your current working directory. Place your PDFs there, or move the script there, to avoid typing full paths.

---

## Known limitations

- The script is calibrated for Official Journal documents and standard EUR-Lex COM documents. It may not work correctly on PDFs with a substantially different layout (e.g. annexes, staff working documents, impact assessments).
- Footnotes that are split across a page break — where the footnote text sits at the bottom of one page and the sentence that references it continues at the top of the next — will still appear slightly out of place. This is a structural limitation of the PDF format and cannot be fixed automatically.
- The script does not handle scanned PDFs (image-only). The source PDF must have a text layer, which all official EUR-Lex documents do.
