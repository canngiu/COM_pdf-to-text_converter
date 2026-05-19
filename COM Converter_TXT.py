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
    text = text.replace('\u2013', ' - ').replace('\u2014', ' — ')
    text = text.replace('\ufffd', '—')
    text = text.replace('•', '—').replace('▪', '—').replace('\uf0b7', '—')
    text = re.sub(r'—\n', '— ', text)
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
    if re.match(r'^(EN\s*)+$', t):
        return True
    if re.match(
        r'(C \d+/\d+\s*\n|\d{1,2}\.\d{1,2}\.\d{4}\s*\n).*Official Journal',
        t, re.DOTALL
    ):
        return True
    if re.match(r'^\d+$', t) and page_height and page_height > 0:
        return True
    if not t:
        return True
    return False

def mark_footnotes(text):
    text = re.sub(r'\((\d{1,2})\)\s+(?=[a-z\'\"])', r'\n[FOOTNOTE \1] ', text)
    text = re.sub(r'(?<=[a-zA-Z\'\u2019])(\d{1,2})(?=[\s,\.;:\)\]]|$)', r'[\1]', text)
    return text

def should_join(last, next_line):
    """Return True only if last line is a wrapped sentence continuation."""
    if not last or not next_line:
        return False
    if last.startswith('[') or next_line.startswith('['):
        return False
    if re.search(r'[.!?]$', last):
        return False
    if last.isupper():
        return False
    if re.match(r'^[IVX]+[\.\d]', last):
        return False
    # Don't join short lines (headings) to anything
    if len(last) < 60:
        return False
    # Don't join if the next line starts a new bullet
    if next_line.startswith('—'):
        return False
    return True

for page in doc:
    raw_blocks = page.get_text('blocks')
    page_height = page.rect.height
    page_lines = [f"[Page {page.number + 1}]"]

    # Merge standalone dash/bullet blocks with the block that follows
    merged_blocks = []
    pending_bullet = False
    for b in raw_blocks:
        t = b[4].strip()
        if t == '—':
            pending_bullet = True
            continue
        if pending_bullet:
            merged_blocks.append((b[0], b[1], b[2], b[3], '— ' + b[4], b[5], b[6]))
            pending_bullet = False
        else:
            merged_blocks.append(b)

    for b in merged_blocks:
        text = b[4]
        if is_noise_block(text, page_height):
            continue
        text = clean_block(text)
        if text:
            text = mark_footnotes(text)
            page_lines.append(text)

    output.append('\n\n'.join(page_lines))

full_text = '\n\n'.join(output)

# Rejoin section numbers with their titles — must run BEFORE the line joiner
full_text = re.sub(
    r'^((?:I{1,3}V?|VI{0,3}|I{0,3}V)(?:\.\d+)?)\.(\n)',
    r'\1. ',
    full_text,
    flags=re.MULTILINE
)

# Rejoin wrapped sentences split across block boundaries (not across page breaks)
lines = full_text.split('\n')
rejoined = []
i = 0
while i < len(lines):
    line = lines[i]
    if not line.strip():
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        last = rejoined[-1].strip() if rejoined else ''
        next_line = lines[j].strip() if j < len(lines) else ''
        if (
            j < len(lines)
            and not lines[j].startswith('[')
            and should_join(last, next_line)
            and '[Page 1]' not in '\n'.join(rejoined[-10:])
        ):
            rejoined[-1] = rejoined[-1].rstrip() + ' ' + lines[j].strip()
            i = j + 1
            continue
    last = rejoined[-1].strip() if rejoined else ''
    if should_join(last, line.strip()):
        rejoined[-1] = rejoined[-1].rstrip() + ' ' + line.strip()
    else:
        rejoined.append(line)
    i += 1
full_text = '\n'.join(rejoined)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(full_text)

print(f"Done — saved to {output_path}")
