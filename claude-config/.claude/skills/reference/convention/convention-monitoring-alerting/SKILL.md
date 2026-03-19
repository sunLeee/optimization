---
name: convention-monitoring-alerting
triggers:
  - "convention monitoring alerting"
description: "모니터링 및 알림(Monitoring & Alerting) 컨벤션 참조 스킬. Performance metrics, health check, alerting strategies로 시스템 상태를 실시간 추적하고 문제를 조기에 탐지한다."
argument-hint: "[섹션] - metrics, health-check, alerting, dashboard, logging"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Glob
  - Grep
model: claude-sonnet-4-6[1m]
context: |
  시스템 모니터링 및 알림 전략을 제공한다.
  프로덕션 환경의 문제를 빠르게 감지하고 대응하기 위한 구현 가이드.
agent: |
  모니터링 전문가.
  Metrics collection, health check, alerting threshold 설정을 제시한다.
hooks:
  pre_execution: []
  post_execution: []
category: 컨벤션 참조
skill-type: Atomic
references: []
referenced-by: []

---
# 모니터링 및 알림(Monitoring & Alerting) 컨벤션

Performance metrics, health check, alerting strategies를 통해 시스템 상태를 실시간 추적하는 규칙.

## 목적

- **성능 메트릭**: 응답시간, 처리량, 에러율 등 핵심 지표
- **헬스 체크**: 서비스 상태 모니터링 (정상/비정상)
- **임계값 기반 알림**: 메트릭이 한계를 초과할 때 즉시 알림
- **이상 탐지**: 통계적 패턴에서 벗어난 경우 감지
- **대시보드**: 실시간 시각화로 상태 확인
- **로깅 통합**: 알림과 로그 연동으로 원인 분석

---

## 1. 성능 메트릭 수집

### 1.1 핵심 메트릭 정의

**모니터링 대상**:
- Latency (응답시간, ms)
- Throughput (초당 요청 수, req/s)
- Error Rate (에러 비율, %)
- Queue Depth (대기 작업 수)
- Memory Usage (메모리 사용량, MB)
- CPU Usage (CPU 사용률, %)

**메트릭 수집기 클래스**: [@templates/skill-examples/convention-monitoring-alerting/metrics-collector.py]

**주요 기능**:
- `record_latency()`: 응답시간 메트릭 기록
- `record_error()`: 에러 메트릭 기록
- `get_percentile()`: p50, p95, p99 백분위 값 조회
- `get_stats()`: 평균, 최소, 최대, 표준편차 통계

### 1.2 API 엔드포인트 메트릭 추적

**데코레이터 방식**: [@templates/skill-examples/convention-monitoring-alerting/metrics-decorator.py]

사용 예시:
```python
@track_metrics(collector, 'api.fetch_user')
def fetch_user(user_id: int):
    return {'id': user_id, 'name': 'Alice'}

user = fetch_user(1)  # 자동으로 메트릭 기록
```

---

## 2. 헬스 체크

### 2.1 헬스 체크 엔드포인트

**HealthChecker 클래스**: [@templates/skill-examples/convention-monitoring-alerting/health-checker.py]

**체크 항목**:
- 데이터베이스 연결성
- 외부 서비스 응답성
- 디스크 공간
- 메모리 사용률
- 큐 깊이 (대기 작업)

**헬스 상태**:
- `HEALTHY`: 모든 체크 통과
- `DEGRADED`: 일부 체크 실패 (50% 이하)
- `UNHEALTHY`: 과반수 체크 실패

사용 예시:
```python
checker = HealthChecker()
checker.register_check('database', check_db_connection)
status = checker.get_health()
print(f"System status: {status['overall_status']}")
```

---

## 3. 임계값 기반 알림

### 3.1 알림 규칙 정의

**AlertingEngine 클래스**: [@templates/skill-examples/convention-monitoring-alerting/alert-engine.py]

**알림 조건**:
- 메트릭 > 임계값 (N초 동안 지속)
- 메트릭 < 임계값 (N초 동안 지속)
- 에러율 > 한계

**심각도 레벨**:
- `info`: 정보성 알림
- `warning`: 주의 필요
- `critical`: 즉시 대응 필요

사용 예시:
```python
engine = AlertingEngine(collector, logger)
rule = AlertRule(
    'high_latency',
    'api.response_time',
    '>',
    1000,  # 1초
    duration=300  # 5분 지속 시
)
engine.register_rule(rule)
alerts = engine.check_alerts()
```

---

## 4. 이상 탐지 (Anomaly Detection)

### 4.1 통계적 이상 탐지

**Z-score 기반 이상 탐지**: [@templates/skill-examples/convention-monitoring-alerting/anomaly-detection.py]

**탐지 방법**:
- Z-score = (X - 평균) / 표준편차
- Z-score > 3.0 (99.7% 신뢰 구간 벗어남) → 이상치 판단

사용 예시:
```python
anomalies = detect_anomalies(
    collector,
    'api.response_time',
    zscore_threshold=3.0
)
for anomaly in anomalies:
    print(f"⚠️ 이상치: {anomaly['value']}ms (편차: {anomaly['deviation']:.1f}%)")
```

---

## 5. 대시보드 및 시각화

### 5.1 메트릭 대시보드 데이터 생성

**대시보드 함수**: [@templates/skill-examples/convention-monitoring-alerting/dashboard.py]

**기능**:
- `generate_dashboard_data()`: Grafana/Plotly용 JSON 데이터 생성
- `export_prometheus_metrics()`: Prometheus 형식 메트릭 내보내기

사용 예시:
```python
# Grafana/Plotly 대시보드
dashboard_data = generate_dashboard_data(
    collector,
    ['api.response_time', 'api.error_rate'],
    time_window_minutes=60
)

# Prometheus 메트릭
prometheus_output = export_prometheus_metrics(collector)
```

---

## 6. 종합 예제: 프로덕션 모니터링 설정

**프로덕션 설정 함수**: [@templates/skill-examples/convention-monitoring-alerting/production-setup.py]

프로세스:
1. 메트릭 수집기 초기화 (1시간 윈도우)
2. 헬스 체크 함수 등록 (DB, 외부 API)
3. 알림 규칙 정의 (응답시간 > 1초, 에러율 > 5%)
4. 백그라운드 모니터링 실행

사용 예시:
```python
collector, checker, alerter = setup_production_monitoring(
    logger,
    db_connection=db_conn
)

# 주기적 모니터링
while True:
    alerts = alerter.check_alerts()
    for alert in alerts:
        send_notification(alert)
    time.sleep(60)
```

---

## 7. 모니터링 체크리스트

구현 완료 후 다음을 확인하세요:

- [ ] 핵심 메트릭 정의 (latency, throughput, error rate)
- [ ] MetricsCollector 구현 및 테스트
- [ ] 메트릭 수집 데코레이터 적용
- [ ] 헬스 체크 함수 정의 (DB, 외부 API 등)
- [ ] HealthChecker 구현 및 테스트
- [ ] 알림 규칙 정의 (임계값, 심각도)
- [ ] AlertingEngine 구현 및 테스트
- [ ] 이상 탐지 (Z-score) 구현
- [ ] 대시보드 데이터 생성
- [ ] Prometheus 메트릭 내보내기
- [ ] 주기적 모니터링 백그라운드 작업
- [ ] 알림 채널 통합 (Slack, PagerDuty, Email)
- [ ] 모니터링 로그 분석

---

## 8. 외부 도구 통합

**통합 가이드**: [@templates/skill-examples/convention-monitoring-alerting/external-integrations.md]

지원 도구:
- **Prometheus + Grafana**: 메트릭 수집 및 시각화
- **Datadog**: 클라우드 모니터링 플랫폼
- **Python logging**: 로깅 통합

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/convention-logging/SKILL.md] | 구조화된 로깅 |
| [@skills/convention-error-handling/SKILL.md] | 에러 처리 |
| [@skills/check-python-style/SKILL.md] | 코드 스타일 검증 |

---

## 참고

- Prometheus Documentation: https://prometheus.io/docs/
- Grafana Dashboards: https://grafana.com/
- Datadog Monitoring: https://www.datadoghq.com/
- Python logging: https://docs.python.org/3/library/logging.html

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-28 | 1.1.0 | 보수적 리팩토링 - 1087→262줄. Python 코드 예시를 템플릿으로 분리 |
| 2026-01-21 | 1.0.0 | 초기 생성 - 메트릭, 헬스체크, 알림, 이상탐지 |

## Gotchas (실패 포인트)

- 임계값 너무 낮으면 alert fatigue — 팀이 알림 무시하게 됨
- 메트릭 수집 없이 임계값 설정 — baseline 데이터 없이 임의 설정
- 알림 수신자 설정 미비 시 알림이 있어도 아무도 대응 안 함
- health check endpoint에 실제 DB 연결 확인 안 하면 false positive
