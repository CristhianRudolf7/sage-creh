"""Check metadata, footers and page bounds; render every page for visual review."""
from pathlib import Path
import json
import pymupdf as fitz
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "qa"
QA.mkdir(exist_ok=True)
reports = []
for language in ["es", "en"]:
    path = ROOT / "paper" / language / "build/article.pdf"
    document = fitz.open(path)
    if document.metadata.get("author") != "Cristhian Egoavil":
        raise SystemExit("Unexpected PDF author")
    if document.xref_get_key(document.pdf_catalog(), "Lang")[1] != language:
        raise SystemExit("Incorrect PDF language metadata")
    images, all_text = [], []
    for index, page in enumerate(document):
        text = page.get_text()
        all_text.append(text)
        if "creado por Cristhian Egoavil" not in text:
            raise SystemExit(f"Missing author footer: {language} page {index+1}")
        if any(token in text for token in ["Datos ficticios", "fictitious data", "manning2008", "???"]):
            raise SystemExit("Template or unresolved-reference text remains")
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    x0, y0, x1, y1 = span["bbox"]
                    if x0 < -1 or y0 < -1 or x1 > page.rect.width+1 or y1 > page.rect.height+1:
                        raise SystemExit(f"Text extends outside page: {language} {index+1}")
        image_path = QA / f"{language}-{index+1:02}.png"
        page.get_pixmap(matrix=fitz.Matrix(1.3,1.3), alpha=False).save(image_path)
        images.append(image_path)
    (QA / f"{language}-text.txt").write_text("\n\f\n".join(all_text))
    for batch in range(0, len(images), 4):
        opened = [Image.open(path).convert("RGB") for path in images[batch:batch+4]]
        width, height = opened[0].size
        sheet = Image.new("RGB", (2*(width+16), 2*(height+40)), "#dfe5e1")
        draw = ImageDraw.Draw(sheet)
        for offset, picture in enumerate(opened):
            x, y = (offset%2)*(width+16)+8, (offset//2)*(height+40)+28
            sheet.paste(ImageOps.expand(picture, border=1, fill="#b5bdb7"), (x,y))
            draw.text((x,y-20), f"{language.upper()} — page {batch+offset+1}", fill="#262b2d")
        sheet.save(QA / f"{language}-contact-{batch//4+1}.png")
    reports.append(dict(language=language, pages=len(document), footer_verified_every_page=True,
                        page_bounds_valid=True, metadata=document.metadata))
    document.close()
(QA / "pdf-audit.json").write_text(json.dumps(reports, ensure_ascii=False, indent=2))
print(json.dumps(reports, ensure_ascii=False, indent=2))
