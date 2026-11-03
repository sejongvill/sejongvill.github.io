"""금주의 식단·주요 일정에 엑셀/PDF 파일만 올라온 글에, 파일 내용을 그림(PNG)으로 만들어 붙인다.
그림은 static/files/preview/ 에 저장하고 글의 previews 항목에 적는다 (홈페이지에서 그림으로 바로 보이게).
--need : 그림이 필요한 글 수만 출력 (LibreOffice 설치가 필요한지 판단용)"""
import glob, os, re, subprocess, sys, tempfile, shutil
from PIL import Image, ImageChops

BOARDS = ('menu', 'schedule')
EXTS = ('.xlsx', '.xls', '.pdf', '.ods', '.docx')

def todo():
    out = []
    for b in BOARDS:
        for md in sorted(glob.glob(f'content/{b}/*.md')):
            t = open(md, encoding='utf-8').read()
            m = re.match(r'---\n(.*?)\n---', t, re.S)
            if not m or re.search(r'^previews:', m.group(1), re.M):
                continue
            files = re.findall(r'^\s+file:\s*(\S+)', m.group(1), re.M)
            files = [f for f in files if os.path.splitext(f)[1].lower() in EXTS]
            if files and not re.search(r'^images:\s*\n\s*-', m.group(1), re.M):
                out.append((md, files))
    return out

def trim(im, pad=24):
    bg = Image.new(im.mode, im.size, (255, 255, 255))
    box = ImageChops.difference(im, bg).getbbox()
    if not box:
        return im
    l, t, r, b = box
    return im.crop((max(0, l - pad), max(0, t - pad), min(im.width, r + pad), min(im.height, b + pad)))

def convert(src, dst_base):
    tmp = tempfile.mkdtemp()
    try:
        pdf = src
        if not src.lower().endswith('.pdf'):
            subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', tmp, src], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
            pdf = os.path.join(tmp, os.path.splitext(os.path.basename(src))[0] + '.pdf')
        subprocess.run(['pdftoppm', '-png', '-r', '130', '-f', '1', '-l', '3', pdf, os.path.join(tmp, 'p')], check=True, timeout=120)
        outs = []
        for i, p in enumerate(sorted(glob.glob(os.path.join(tmp, 'p*.png'))), 1):
            im = trim(Image.open(p).convert('RGB'))
            im.thumbnail((1600, 2400))
            name = f'{dst_base}.png' if i == 1 else f'{dst_base}-{i}.png'
            im.save(os.path.join('static/files/preview', name), optimize=True)
            outs.append('/files/preview/' + name)
        return outs
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == '__main__':
    jobs = todo()
    if '--need' in sys.argv:
        print(len(jobs)); sys.exit(0)
    os.makedirs('static/files/preview', exist_ok=True)
    for md, files in jobs:
        prev = []
        for f in files:
            src = 'static' + f
            if os.path.exists(src):
                try:
                    prev += convert(src, os.path.splitext(os.path.basename(f))[0])
                except Exception as ex:
                    print('그림 만들기 실패', src, ex)
        if prev:
            t = open(md, encoding='utf-8').read()
            t = t.replace('\n---', '\npreviews:\n' + ''.join(f'- {x}\n' for x in prev).rstrip('\n') + '\n---', 1)
            open(md, 'w', encoding='utf-8').write(t)
            print(md, '->', prev)
