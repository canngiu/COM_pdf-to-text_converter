import pymupdf
import re
from pathlib import Path

pdf_path = input("Enter PDF filename (e.g. COM(2025)47.pdf): ").strip()

doc = pymupdf.open(pdf_path)
output_path = Path(pdf_path).with_suffix('.txt')
output = []

def clean_block(text):
    text = text.replace('\r\n', '\n')
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = re.sub(r'—\n', '— ', text)
    # Join wrapped lines within the block repeatedly until stable
    prev = None
    while prev != text:
        prev = text
        lines = text.split('\n')
        joined = []
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            if (
                line
                and i + 1 < len(lines)
                and lines[i + 1].strip()
                and not re.search(r'[.!?]$', line)
            ):
                joined.append(line + ' ' + lines[i + 1].strip())
                i += 2
            else:
                joined.append(line)
                i += 1
        text = '\n'.join(joined)
    return text.strip()

def is_noise_block(text, page_height):
    t = text.strip()
    # Standalone EN / EN EN (language marker on cover page)
    if re.match(r'^(EN\s*)+$', t):
        return True
    # OJ header: date + EN + C 287/X + Official Journal (2001-era documents)
    if re.match(
        r'(C \d+/\d+\s*\n|\d{1,2}\.\d{1,2}\.\d{4}\s*\n).*Official Journal',
        t, re.DOTALL
    ):
        return True
    # Standalone page number at the bottom of the page (non-OJ documents)
    if re.match(r'^\d+$', t) and page_height and page_height > 0:
        return True
    # Empty or whitespace-only block
    if not t:
        return True
    return False

def mark_footnotes(text):
    # Mark footnote text at bottom of page: (1) followed by lowercase
    text = re.sub(r'\((\d{1,2})\)\s+(?=[a-z\'\"])', r'\n[FOOTNOTE \1] ', text)
    # Mark inline refs: number glued to end of a word, e.g. "report2" or "standards33"
    text = re.sub(r'(?<=[a-zA-Z])(\d{1,2})(?=[\s,\.;:\)\]]|$)', r'[\1]', text)
    return text

for page in doc:
    blocks = page.get_text('blocks')
    page_height = page.rect.height
    page_lines = [f"[Page {page.number + 1}]"]

    for b in blocks:
        text = b[4]
        if is_noise_block(text, page_height):
            continue
        text = clean_block(text)
        if text:
            text = mark_footnotes(text)
            page_lines.append(text)

    output.append('\n\n'.join(page_lines))

full_text = '\n\n'.join(output)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(full_text)

print(f"Done — saved to {output_path}")
