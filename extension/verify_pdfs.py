"""Audit and render every page of both v2 PDFs without touching v1 QA."""
import json
from pathlib import Path
import pymupdf as fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa-v2'
OUT.mkdir(exist_ok=True)
reports = []
for lang in ['es','en']:
    document = fitz.open(ROOT / 'paper-v2' / lang / 'build/article.pdf')
    assert document.metadata['author'] == 'Cristhian Egoavil'
    assert document.xref_get_key(document.pdf_catalog(), 'Lang')[1] == lang
    images, texts = [], []
    for index, page in enumerate(document):
        text = page.get_text()
        assert 'creado por Cristhian Egoavil' in text, (lang,index,'footer')
        assert 'CREH Labs' in text, (lang,index,'brand')
        assert not any(s in text for s in ['???','@@','TODO','fictitious data','Datos ficticios'])
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    x0,y0,x1,y1 = span['bbox']
                    assert x0>=0 and y0>=0 and x1<=page.rect.width+1 and y1<=page.rect.height+1, (lang,index,span['text'])
        image = OUT / f'{lang}-{index+1:02}.png'
        page.get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False).save(image)
        images.append(image)
        texts.append(text)
    for start in range(0,len(images),4):
        pictures = [Image.open(p).convert('RGB') for p in images[start:start+4]]
        w,h = pictures[0].size
        sheet = Image.new('RGB',(2*(w+16),2*(h+40)),'#dfe5e1')
        draw = ImageDraw.Draw(sheet)
        for offset,picture in enumerate(pictures):
            x,y = (offset%2)*(w+16)+8,(offset//2)*(h+40)+28
            sheet.paste(picture,(x,y))
            draw.text((x,y-20),f'{lang.upper()} | page {start+offset+1}',fill='#262b2d')
        sheet.save(OUT / f'{lang}-contact-{start//4+1}.png')
    (OUT / f'{lang}-text.txt').write_text('\n\f\n'.join(texts))
    reports.append(dict(language=lang,pages=len(document),author=document.metadata['author'],
                        footers_all_pages=True,brand_all_pages=True,page_bounds=True,
                        visual_review='Separate visual inspection of rendered contact sheets required'))
    document.close()
(OUT / 'pdf-audit.json').write_text(json.dumps(reports,indent=2))
print(json.dumps(reports,indent=2))
