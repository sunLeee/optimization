# criteria-pattern.md — 품질 체크 스크립트 패턴 가이드

> ADR-043 참조

## 개요

두 계층으로 구성된 품질 체크 시스템:

| 파일 | 위치 | 역할 | 항목 수 |
|------|------|------|---------|
| `common-criteria.sh` | `.claude/` | 모든 프로젝트 공통 기준 | 4개 |
| `project-criteria.sh` | `.claude/` (선택) | 프로젝트 특화 기준 | 자유 |
| `check-criteria.sh` | `.claude/` | orchestrator | common + project 실행 |

## 새 프로젝트에 적용하기

### 최소 설정 (common만)

```bash
# setup.sh가 common-criteria.sh를 자동 배포함
bash .claude/setup.sh
# Stop hook이 4개 공통 기준으로 gate
```

### 프로젝트 기준 추가

`.claude/project-criteria.sh` 파일을 생성하라:

```bash
#!/usr/bin/env bash
pass=0; total=0
_COUNTS_ONLY=false
[ "$1" = "--counts" ] && _COUNTS_ONLY=true

chk() {
  # ... (common-criteria.sh와 동일한 chk 함수)
}

# 프로젝트 특화 체크 추가
chk PRJ-01 "README.md 존재" "test -f README.md && echo 0 || echo 1" "=" "0"
chk PRJ-02 "tests/ 디렉토리" "test -d tests && echo 0 || echo 1" "=" "0"

$_COUNTS_ONLY && { echo "$pass $total"; exit 0; }
echo "=== 프로젝트 기준: $pass/$total ==="
```

## --score vs --counts 플래그

| 플래그 | 출력 형식 | 사용처 |
|--------|-----------|--------|
| (없음) | 전체 출력 + 총점 | 수동 실행 |
| `--score` | 숫자 (0~100) | Stop hook |
| `--counts` | "pass total" | orchestrator 합산 |

## Stop hook 작동 방식

```
Claude 응답 완료
  → Stop hook 실행
  → bash .claude/check-criteria.sh --score
    → common-criteria.sh --counts (4개)
    → project-criteria.sh --counts (N개, 없으면 0 0)
    → 합산 후 pct 계산
  → pct < 90 → exit 2 (Claude 계속 작업)
  → pct ≥ 90 → exit 0 (정상 종료)
```
