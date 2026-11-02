# 세종빌 홈페이지

사회복지법인 예일 세종빌 홈페이지 (https://sejongvill.github.io)

- `content/` 게시판 글 (글쓰기 화면 `/admin`에서 직원이 올린 글이 여기에 저장됨)
- `static/` 디자인 파일, 사진, 첨부파일
- `build/build.py` 글과 디자인을 합쳐 홈페이지를 만드는 프로그램
- `.github/workflows/deploy.yml` 글이 올라오면 자동으로 홈페이지를 다시 만들어 공개
