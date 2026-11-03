"""저장소에 올라온 큰 사진을 가로·세로 최대 1280px로 줄여 저장 (홈페이지 용량 관리).
직원 글쓰기는 올릴 때 이미 줄이지만, 관리 화면(/admin) 등으로 원본이 올라온 경우를 대비한다."""
import glob, os
from PIL import Image, ImageOps
MAX, LIMIT = 1280, 450_000
changed = []
for f in glob.glob('static/files/uploads/**/*', recursive=True):
    low = f.lower()
    if not low.endswith(('.jpg', '.jpeg', '.png', '.webp')):
        continue
    try:
        im = ImageOps.exif_transpose(Image.open(f))
        if max(im.size) <= MAX and os.path.getsize(f) <= LIMIT:
            continue
        before = os.path.getsize(f)
        im.thumbnail((MAX, MAX), Image.LANCZOS)
        if low.endswith('.png'):
            im.save(f, optimize=True)
        elif low.endswith('.webp'):
            im.save(f, quality=80)
        else:
            im.convert('RGB').save(f, quality=80, optimize=True, progressive=True, format='JPEG')
        changed.append(f'{f}: {before // 1024}KB -> {os.path.getsize(f) // 1024}KB')
    except Exception as ex:
        print('건너뜀', f, ex)
print('\n'.join(changed) or '줄일 사진 없음')
