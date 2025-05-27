import base64
import os
import fitz  # PyMuPDF
from transformers import MarianMTModel, MarianTokenizer

# Optional model cache to avoid reloading
model_cache = {}

def load_model(target_lang="id"):
    model_name = f"Helsinki-NLP/opus-mt-en-{target_lang}"
    if target_lang not in model_cache:
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        model_cache[target_lang] = (model, tokenizer)
    return model_cache[target_lang]

def translate_text(text, model, tokenizer):
    if not text.strip():
        return ""
    batch = tokenizer.prepare_seq2seq_batch([text], return_tensors="pt", truncation=True)
    gen = model.generate(**batch)
    return tokenizer.decode(gen[0], skip_special_tokens=True)

def process_pdf(input_path: str, output_html_path: str, target_lang="id"):
    doc = fitz.open(input_path)
    model, tokenizer = load_model(target_lang)

    image_dir = os.path.splitext(output_html_path)[0] + "_images"
    os.makedirs(image_dir, exist_ok=True)

    html_output = ['<!DOCTYPE html>', '<html>', '<head>',
                   '<meta charset="utf-8">',
                   '<style>',
                   'body { margin: 0; padding: 0; font-family: sans-serif; }',
                   '.page { position: relative; margin-bottom: 20px; border: 1px solid #ccc; }',
                   '.text-span { position: absolute; white-space: pre; }',
                   '.img { position: absolute; }',
                   '</style>',
                   '</head>', '<body>']

    for page_num, page in enumerate(doc):
        width = page.rect.width
        height = page.rect.height
        html_output.append(f'<div class="page" style="width:{width}px; height:{height}px;">')

        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    x, y = span["bbox"][:2]
                    size = span["size"]
                    font = span.get("font", "sans-serif")
                    original_text = span["text"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

                    # Translate
                    translated = translate_text(original_text, model, tokenizer)
                    translated = translated.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

                    html_output.append(
                        f'<span class="text-span" style="left:{x}px; top:{y}px; font-size:{size}px; font-family:\'{font}\'">{translated}</span>'
                    )

        # Extract and embed images
        images = page.get_images(full=True)
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image["ext"]
            img_path = os.path.join(image_dir, f"page{page_num}_img{img_index}.{ext}")
            with open(img_path, "wb") as img_file:
                img_file.write(image_bytes)

            bbox = fitz.Rect(img[1:5])  # (x0, y0, x1, y1)
            width_img = bbox.width
            height_img = bbox.height
            x_img, y_img = bbox.x0, bbox.y0

            # Add <img> tag to HTML
            html_output.append(
                f'<img src="{os.path.relpath(img_path, os.path.dirname(output_html_path))}" class="img" '
                f'style="left:{x_img}px; top:{y_img}px; width:{width_img}px; height:{height_img}px;" />'
            )

        html_output.append('</div>')

    html_output.append('</body></html>')

    # Save to HTML
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_output))

    print(f"✅ Translated HTML saved to: {output_html_path}")
