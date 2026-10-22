import pypdfium2 as pdfium
import sys

# Force UTF-8 output
import sys
sys.stdout.reconfigure(encoding='utf-8')

pdf = pdfium.PdfDocument('app/weber/templates/guardian_master_template.pdf')
print('Pages:', len(pdf))
for i in range(len(pdf)):
    page = pdf[i]
    text = page.get_textpage().get_text_range(0, page.get_textpage().count_chars())
    print(f'--- Page {i+1} ({len(text)} chars) ---')
    print(text[:2000])
    print('---')