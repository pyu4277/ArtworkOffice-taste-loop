# ArtworkOffice-taste-loop

교육용 자료(발표자료·교재·보조자료·영상·보고서·워크시트)를 만들 때마다 **사용자의 취향을 인터뷰로 확인하고, 만든 뒤 배운 것을 저장해 다음 자료를 진화시키는** Claude Code 스킬입니다.

- **인터뷰 앱** (`GUI-Interview.html`, 반응형 단일 HTML): 사이드 트리에서 큰 구분 → 취향 질문을 펼쳐 예시(글 스타일 샘플·화면 그림)를 보고 고릅니다. 지난 프로젝트·지난 답·레퍼런스를 질문에 끌어다 넣고, 「이 양식으로 시작」으로 지난 프로젝트 설정을 한 번에 가져옵니다.
- **레퍼런스 먼저** (1.3.0): 큰 구분을 고르기 전에 레퍼런스 사이트 목록을 둘러보고, 찾은 자료(주소·파일)를 넣으면 Claude가 분석해 기준표를 만들고 그 양식대로 질문지를 채운 페이지를 다시 줍니다(`build_interview.py --prefill`). 질문마다 「레퍼런스대로」를 골라도 됩니다.
- **대화 추천** (1.4.0): 인터뷰 페이지를 만들기 전에 대화로 무엇을·누구에게·왜·어떻게 만들지 알아보고, 그 대화와 지난 기록으로 1·2·3부 답을 미리 골라 둔 채 인터뷰를 엽니다(`build_interview.py --recommend`). 카드마다 「대화 추천」과 한 줄 이유, 바꾸면 「추천 → 바꿈」, 화면 위 요약판과 대시보드 적중률이 보입니다. 추천을 어떻게 바꿨는지(`recommend.py record`)와 제작 중 수정 요청(`recommend.py correct`, 보통 기록의 5배 무게)을 쌓아 규칙을 스스로 배우고, 같은 상황인데 다르게 끝난 것은 작업 여건·상황 차이라는 단서가 통계로 확실할 때만 규칙을 나누고(인터뷰 페이지가 기기·시간대 같은 작업 여건도 함께 기록), 애매하면 그때그때 취향으로 쌓아 한쪽으로 기울 확률이 80%를 넘으면 그쪽을 미리 고릅니다.
- **절차**: 환경 점검 → 실행 모드 → 대화 → 인터뷰 → 계획 → 제작 중 검토 → 버전 비교 → 마무리 갱신. 갱신은 무조건 추가가 아니라 반영·범위 축소·보류·미반영을 판정하고, 확인 질문 없이 기록으로 스스로 진화합니다(모든 변경은 변경이력에 남아 되돌릴 수 있습니다).
- **진화**: 선택지마다 「지금 이 선택을 고르면 이렇게 만든다」(방법·점검·예시·이력)를 버전으로 쌓습니다. 같은 선택을 또 골라도 그 사이 나아진 방법으로 만듭니다.
- **빈 저장소로 시작**: 설치본에는 만든 사람의 개인 데이터가 없습니다. 첫 인터뷰와 마무리에서 내 취향이 쌓입니다.

## 설치

**방법 1 — 플러그인 (권장)**. Claude Code 안에서:

```bash
/plugin marketplace add pyu4277/ArtworkOffice-taste-loop
```

```bash
/plugin install ArtworkOffice-taste-loop@ArtworkOffice
```

Claude Code 2.1.275 이후 버전은 한 줄로도 됩니다.

```bash
/plugin install ArtworkOffice-taste-loop --marketplace pyu4277/ArtworkOffice-taste-loop
```

플러그인으로 설치하면 스킬 이름은 `/ArtworkOffice-taste-loop:ArtworkOffice-taste-loop`이고, 세션 시작 훅(취향 요약·환경 점검 요약을 넣기만 함, 아무것도 막지 않음)이 함께 켜집니다. 서드파티 마켓플레이스는 자동 업데이트가 기본 꺼짐이라 `/plugin marketplace update`로 새 버전을 받습니다.

**방법 2 — 폴더 복사**. `plugins/ArtworkOffice-taste-loop/skills/ArtworkOffice-taste-loop/` 폴더를 통째로 복사합니다.

- 모든 프로젝트에서 쓰기: `~/.claude/skills/ArtworkOffice-taste-loop/`
- 한 프로젝트에서만(팀과 함께): `<프로젝트>/.claude/skills/ArtworkOffice-taste-loop/` 에 두고 커밋

이 방법은 세션 시작 훅이 없습니다. 원하면 프로젝트 `.claude/settings.json`의 `SessionStart`에 `scripts/session_start.sh`를 등록합니다.


## 처음 한 번 — 내 데이터 폴더 만들기

```bash
python3 <스킬 폴더>/scripts/init_store.py
```

- 기본: `<프로젝트>/.claude/ArtworkOffice-taste-loop-data/` (이 프로젝트의 취향)
- `--personal`: `~/.claude/ArtworkOffice-taste-loop-data/` (여러 프로젝트에서 같은 취향)
- 이미 있는 파일은 덮어쓰지 않습니다. 스킬 폴더(특히 플러그인 설치 폴더)에는 데이터를 쓰지 않습니다. 업데이트해도 내 데이터는 그대로입니다.
- 지금 어느 데이터를 쓰는지: `python3 <스킬 폴더>/scripts/store.py`
- **스킬을 업데이트한 뒤**: `python3 <스킬 폴더>/scripts/upgrade_store.py` — 내 데이터 폴더를 새 구조로 올린다(기록은 지우지 않음). 그다음 인터뷰 페이지를 다시 만든다.
- **취향 파일을 고칠 때**: `preferences.json`·`knowledge/choices.json`은 항목마다 줄을 맞춘 손 정렬 형식입니다. `json.dump`로 다시 쓰면 비교가 수천 줄로 불어나므로 `python3 <스킬 폴더>/scripts/store_write.py`(entry-add · entry-set · choice-add · choice-set · fmt)로 고친 항목만 씁니다(1.3.0).
- **인터뷰 구조를 직접 고치기**(목차 → 질문 → 선택지, 「이걸 골랐을 때만 보임」 조건까지): `python3 <스킬 폴더>/scripts/build_interview.py --lecture <작업폴더> --mode edit --out <편집.html>` → 브라우저에서 고치고 JSON 내보내기 → `python3 <스킬 폴더>/scripts/structure_edits.py add <JSON>`(반영 대기로 쌓임, `list`로 기록 보기) → 프로젝트 마무리 때 `structure_edits.py preview` 확인 뒤 `apply --yes`.
- Windows: `python3`가 없거나 마이크로소프트 스토어 바로가기(실행하면 파이썬 대신 오류로 끝남)면 위 명령의 `python3`를 `python`으로 바꿉니다. 세션 시작 훅은 실제로 실행되는 파이썬을 스스로 골라 UTF-8 모드로 돌립니다(1.0.1부터).
- 프로젝트마다 다른 절차(규칙 파일, 파일 이름 규칙, 공유본 만드는 명령, 쓰는 도구, 커밋 형식)는 데이터 폴더에 `PROJECT.md`로 적으면 스킬이 시작할 때 읽고 따릅니다.

## 필요한 것

| 도구 | 용도 | 필수 |
|---|---|---|
| Python 3.8+ | 모든 스크립트 | 예 |
| 브라우저 | 인터뷰 페이지 열기(파일로 열어도 모든 기능 동작, 답은 JSON 내려받기·복사) | 예 |
| Node 20+ · jsdom@24.1.3 | 인터뷰 페이지 자동 검사(`scripts/check_interview.js` — 가짜 예시 데이터로 스스로 돈다) | 아니오 |
| claude.ai 게시 페이지 | 휴대폰에서 답하고 「저장·제출」로 바로 회수 | 아니오 |

## 쓰는 법

Claude Code에서 "새 발표자료 만들자", "인터뷰부터 하자", "이번 프로젝트 마무리하고 교훈 정리해 줘"처럼 말하면 스킬이 절차를 시작합니다. 자세한 절차는 `plugins/ArtworkOffice-taste-loop/skills/ArtworkOffice-taste-loop/SKILL.md`.

## 이 레포에 대해

이 레포는 배포본입니다. 원본은 만든 사람의 작업 레포에서 관리하고, 바뀔 때마다 이 레포로 내보냅니다. 버그·제안은 이 레포의 Issues에 남겨 주세요.

라이선스 파일은 아직 없습니다. 라이선스가 정해지기 전까지 저작권은 만든 사람에게 있습니다.
