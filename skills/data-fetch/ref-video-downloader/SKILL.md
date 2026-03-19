---
name: ref-video-downloader
triggers:
  - "ref video downloader"
description: 동영상을 다운로드하여 로컬에 저장한다. 품질 선택, 메타데이터 캡처, 배치 다운로드를 지원한다. yt-dlp가 없으면 자동 설치 후 진행한다.
argument-hint: "[video-url] [--quality 720p] [--audio-only] [--playlist]"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Bash
  - Write
  - AskUserQuestion
model: claude-sonnet-4-6[1m]
context: 동영상 다운로드 스킬이다. yt-dlp를 사용하여 YouTube, Vimeo 등에서 동영상을 다운로드한다. ref-video-transcript와 연계하여 트랜스크립트도 함께 저장 가능하다.
agent: 당신은 미디어 다운로드 전문가입니다. 동영상을 효율적으로 다운로드하고 메타데이터를 정리합니다.
hooks:
  pre_execution: []
  post_execution: []
category: 레퍼런스/시나리오
skill-type: Atomic
references: []
referenced-by:
  - "@skills/ref-workflow/SKILL.md"

---
# ref-video-downloader

동영상을 다운로드하여 로컬에 저장하는 스킬.

## 목적

- YouTube, Vimeo 등 동영상 플랫폼에서 동영상 다운로드
- 품질/포맷 선택 지원
- 메타데이터 (제목, 설명, 썸네일) 자동 저장
- 배치 다운로드 (플레이리스트) 지원
- [@skills/ref-video-transcript/SKILL.md]와 연계하여 트랜스크립트 동시 저장

## 사용법

```
/ref-video-downloader https://www.youtube.com/watch?v=xxxxx
/ref-video-downloader https://www.youtube.com/watch?v=xxxxx --quality 1080p
/ref-video-downloader https://www.youtube.com/watch?v=xxxxx --audio-only
/ref-video-downloader https://www.youtube.com/playlist?list=xxxxx --playlist
```

## 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--quality` | 동영상 품질 (480p, 720p, 1080p, 4K) | 720p |
| `--format` | 출력 포맷 (mp4, webm) | mp4 |
| `--audio-only` | 오디오만 추출 (mp3) | false |
| `--playlist` | 플레이리스트 전체 다운로드 | false |
| `--with-transcript` | 트랜스크립트 함께 저장 | false |
| `--lang` | 자막 언어 (ko, en, ja 등) | ko |

## 프로세스

```mermaid
flowchart TD
    Start["/ref-video-downloader<br/>[video-url] [options]"]

    S1["Step 1: 환경 확인"]
    S1_1["yt-dlp 설치 여부 확인"]
    S1_2["미설치 시 자동 설치"]

    S2["Step 2: URL 분석"]
    S2_1["플랫폼 감지<br/>(YouTube, Vimeo 등)"]
    S2_2["동영상 ID 추출"]
    S2_3["플레이리스트 여부 확인"]

    S3["Step 3: 다운로드 옵션 설정"]
    S3_1["품질 선택 (--quality)"]
    S3_2["포맷 선택 (--format)"]
    S3_3["오디오 전용 (--audio-only)"]

    S4["Step 4: 메타데이터 수집"]
    S4_1["제목, 설명"]
    S4_2["썸네일 이미지"]
    S4_3["info.json 저장"]

    S5["Step 5: 동영상 다운로드"]
    S5_1["yt-dlp 실행"]
    S5_2["진행률 표시"]

    S6["Step 6: 트랜스크립트 연계<br/>(옵션)"]
    S6_1["--with-transcript 시<br/>ref-video-transcript 호출"]
    S6_2["동일 폴더에<br/>transcript.md 저장"]

    End([완료])

    Start --> S1
    S1 --> S1_1
    S1 --> S1_2

    S1 --> S2
    S2 --> S2_1
    S2 --> S2_2
    S2 --> S2_3

    S2 --> S3
    S3 --> S3_1
    S3 --> S3_2
    S3 --> S3_3

    S3 --> S4
    S4 --> S4_1
    S4 --> S4_2
    S4 --> S4_3

    S4 --> S5
    S5 --> S5_1
    S5 --> S5_2

    S5 --> S6
    S6 --> S6_1
    S6 --> S6_2

    S6 --> End

    style Start fill:#e1f5ff
    style S1 fill:#fff4e1
    style S2 fill:#e1ffe1
    style S3 fill:#ffe1f5
    style S4 fill:#f5e1ff
    style S5 fill:#e1f5ff
    style S6 fill:#fff4e1
    style End fill:#90EE90
```

## 출력 구조

```
docs/references/videos/
├── {sanitized-title}/
│   ├── video.mp4            # 다운로드된 동영상
│   ├── info.json            # 메타데이터 (제목, 설명, URL, 날짜)
│   ├── thumbnail.jpg        # 썸네일 이미지
│   └── transcript.md        # (선택) ref-video-transcript 연계 시
```

## 핵심 명령어

### yt-dlp 설치 확인 및 자동 설치

```bash
# 설치 확인
which yt-dlp || pip install yt-dlp

# 버전 확인
yt-dlp --version
```

### 품질별 다운로드

```bash
# 720p 다운로드
yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
  --merge-output-format mp4 \
  -o "docs/references/videos/%(title)s/video.%(ext)s" \
  "VIDEO_URL"

# 1080p 다운로드
yt-dlp -f "bestvideo[height<=1080]+bestaudio/best[height<=1080]" \
  --merge-output-format mp4 \
  -o "docs/references/videos/%(title)s/video.%(ext)s" \
  "VIDEO_URL"

# 4K 다운로드
yt-dlp -f "bestvideo[height<=2160]+bestaudio/best[height<=2160]" \
  --merge-output-format mp4 \
  -o "docs/references/videos/%(title)s/video.%(ext)s" \
  "VIDEO_URL"
```

### 오디오 전용 추출

```bash
yt-dlp -x --audio-format mp3 --audio-quality 0 \
  -o "docs/references/videos/%(title)s/audio.%(ext)s" \
  "VIDEO_URL"
```

### 메타데이터 저장

```bash
yt-dlp --write-info-json --write-thumbnail \
  --skip-download \
  -o "docs/references/videos/%(title)s/info" \
  "VIDEO_URL"
```

### 플레이리스트 다운로드

```bash
yt-dlp --yes-playlist \
  -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
  --merge-output-format mp4 \
  -o "docs/references/videos/playlist/%(playlist_index)s-%(title)s/video.%(ext)s" \
  "PLAYLIST_URL"
```

## 메타데이터 템플릿 (info.json)

```json
{
  "title": "동영상 제목",
  "description": "동영상 설명",
  "url": "원본 URL",
  "uploader": "채널명",
  "upload_date": "YYYYMMDD",
  "duration": 3600,
  "view_count": 10000,
  "downloaded_at": "2026-01-21T10:00:00Z",
  "quality": "720p",
  "format": "mp4"
}
```

## 예제

```
User: /ref-video-downloader https://www.youtube.com/watch?v=xyz123

Claude:
=== 동영상 다운로드 ===

URL: https://www.youtube.com/watch?v=xyz123

[1/5] 환경 확인 중...
  - yt-dlp 버전: 2026.01.15

[2/5] 동영상 정보 수집 중...
  - 제목: "FastAPI 완전 정복 2026"
  - 채널: TechTutorials
  - 길이: 1:23:45
  - 품질: 720p (기본값)

[3/5] 메타데이터 저장 중...
  - info.json 저장 완료
  - thumbnail.jpg 저장 완료

[4/5] 동영상 다운로드 중...
  [████████████████████] 100%
  - video.mp4 (512MB)

[5/5] 완료

=== 다운로드 완료 ===

저장 위치: docs/references/videos/fastapi-complete-2026/
├── video.mp4 (512MB)
├── info.json
└── thumbnail.jpg

💡 트랜스크립트도 필요하시면:
   /ref-video-transcript https://www.youtube.com/watch?v=xyz123
```

## 오디오 추출 예제

```
User: /ref-video-downloader https://www.youtube.com/watch?v=xyz123 --audio-only

Claude:
=== 오디오 추출 ===

URL: https://www.youtube.com/watch?v=xyz123

[1/3] 동영상 정보 확인...
  - 제목: "Podcast Episode 42"
  - 길이: 45:30

[2/3] 오디오 추출 중...
  [████████████████████] 100%

[3/3] MP3 변환 중...
  - audio.mp3 (42MB)

=== 완료 ===

저장 위치: docs/references/videos/podcast-episode-42/audio.mp3
```

## 플레이리스트 예제

```
User: /ref-video-downloader https://www.youtube.com/playlist?list=PLxxx --playlist

Claude:
=== 플레이리스트 다운로드 ===

URL: https://www.youtube.com/playlist?list=PLxxx

플레이리스트 정보:
- 제목: "Python 기초 강의"
- 동영상 수: 10개
- 총 길이: 약 5시간

계속 진행할까요? (Y/n)
→ Y

[1/10] 다운로드: "01. Python 소개" ✓
[2/10] 다운로드: "02. 변수와 타입" ✓
...
[10/10] 다운로드: "10. 마무리" ✓

=== 완료 ===

저장 위치: docs/references/videos/playlist/python-basics/
├── 01-python-intro/video.mp4
├── 02-variables-types/video.mp4
...
└── 10-conclusion/video.mp4
```

## 오류 처리

| 오류 | 원인 | 해결 |
|------|------|------|
| `yt-dlp not found` | yt-dlp 미설치 | 자동 설치 진행 |
| `Video unavailable` | 지역 제한/비공개 | VPN 또는 다른 영상 선택 |
| `Format not available` | 요청 품질 없음 | 낮은 품질로 자동 대체 |
| `Disk full` | 저장공간 부족 | 저장공간 확보 후 재시도 |

## 관련 스킬

| 스킬명 | 관계 | 설명 |
|--------|------|------|
| [@skills/ref-video-transcript/SKILL.md] | 연계 | 트랜스크립트 추출 |
| [@skills/prd-workflow/SKILL.md] | 부모 | 레퍼런스 수집 단계 |
| [@skills/markdown-converter/SKILL.md] | 관련 | 변환 도구 |

## Changelog

| 날짜 | 변경 내용 |
|------|----------|
| 2026-01-21 | 초기 스킬 생성 |
