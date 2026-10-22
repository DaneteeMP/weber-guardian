import pypdfium2 as pdfium

pdf = pdfium.PdfDocument(r'C:\Users\danma\OneDrive\WeberGuardian\test_output.pdf')
print('pages:', len(pdf))
for i in range(min(3, len(pdf))):
    page = pdf[i]
    text = page.get_textpage().get_text_range(0, page.get_textpage().count_chars())
    print(f'--- Page {i+1} ---')
    print(text[:500])
    print('---')