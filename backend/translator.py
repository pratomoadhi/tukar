import fitz  # PyMuPDF
from transformers import MarianMTModel, MarianTokenizer

model_cache = {}

def load_model(target_lang="id"):
    model_name = f"Helsinki-NLP/opus-mt-en-{target_lang}"
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    return model, tokenizer

def translate_text(text, model, tokenizer):
    if not text.strip():
        return ""
    batch = tokenizer.prepare_seq2seq_batch([text], return_tensors="pt", truncation=True)
    gen = model.generate(**batch)
    return tokenizer.decode(gen[0], skip_special_tokens=True)

def translate_pdf_file(input_path, output_path, target_lang="id"):
    model, tokenizer = model_cache.get(target_lang) or load_model(target_lang)
    model_cache[target_lang] = (model, tokenizer)

    input_doc = fitz.open(input_path)
    output_doc = fitz.open()

    for page in input_doc:
        # Get the page width and height
        page_width = page.rect.width
        page_height = page.rect.height

        new_page = output_doc.new_page(width=page_width, height=page_height)

        # Extract text and its position from the PDF
        text_instances = page.get_text("dict")['blocks']

        for block in text_instances:
            for line in block['lines']:
                for span in line['spans']:
                    text = span['text']
                    if not text.strip():
                        continue
                    
                    # Translate the line of text
                    translated = translate_text(text, model, tokenizer)
                    # print(f"Original: {text}, Translated: {translated}")  # Debugging

                    # Ensure the translated text is not empty
                    if translated.strip() == "":
                        continue

                    # Get the starting coordinates of the text
                    x0, y0 = span['bbox'][:2]  # Only use x0, y0

                    # Insert the translated text at the start of the original text position
                    new_page.insert_text(
                        (x0, y0),  # Use the starting position
                        translated,
                        fontsize=span['size'],  # Keep the same font size
                        fontname="helv",  # Use a basic font
                    )

    # Save the output PDF
    output_doc.save(output_path)
    output_doc.close()
