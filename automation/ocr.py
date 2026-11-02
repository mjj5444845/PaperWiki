# -*- coding: utf-8 -*-
"""Optional machine OCR for bitmap figures; original PDF text is kept separately."""
import json,platform,shutil,subprocess,tempfile
from pathlib import Path

def supplement_pdf(path,pages,job):
    import fitz
    if platform.system()!='Darwin' or not shutil.which('swift'):
        return pages
    directory=Path(job)/'ocr-images';directory.mkdir(exist_ok=True)
    images=[]
    with fitz.open(path) as doc:
        for i,page in enumerate(doc):
            if not page.get_images():continue
            target=directory/('page-%03d.png'%(i+1))
            page.get_pixmap(matrix=fitz.Matrix(2000/page.rect.width,2000/page.rect.width)).save(str(target))
            images.append((i,target))
    if not images:return pages
    script=Path(__file__).with_suffix('.swift')
    with tempfile.TemporaryDirectory(prefix='paperwiki-swift-') as cache:
        run=subprocess.run(['swift','-module-cache-path',cache,str(script)]+[str(p) for _,p in images],capture_output=True,text=True,timeout=180)
    if run.returncode:raise ValueError('图像OCR失败，不能伪称图内文字已抽取')
    extracted=json.loads(run.stdout)
    (Path(job)/'machine-ocr.json').write_text(json.dumps(extracted,ensure_ascii=False,indent=2)+'\n')
    for i,picture in images:
        text='\n'.join(line['text'] for line in extracted[str(picture)])
        if not text.strip():continue
        pages[i]['pdf_text']=pages[i]['text'];pages[i]['ocr_text']=text
        pages[i]['text']+='\n\n[Machine OCR of this physical page image; verify numbers against the attached PDF image]\n'+text
    return pages
