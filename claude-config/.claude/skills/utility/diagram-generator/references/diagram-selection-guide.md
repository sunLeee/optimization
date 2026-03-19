# 다이어그램 선택 가이드

**"무엇을 시각화하려는가"에 따라 다이어그램 유형을 선택한다.**

---

## Quick Reference

| 시각화 대상 | 다이어그램 | 명령어 |
|------------|-----------|--------|
| 프로세스 흐름, ETL, 의사결정 | Flowchart | `/diagram flow` |
| API 호출, 서비스 통신 | Sequence | `/diagram sequence` |
| 클래스 구조, 상속 관계 | Class | `/diagram class` |
| DB 테이블, 스키마 | ER | `/diagram er` |
| 상태 전이, 라이프사이클 | State | `/diagram state` |
| 시스템 컴포넌트, 배포 | Architecture | `/diagram arch` |
| 병렬 처리, 워크플로우 | Activity | `/diagram activity` |
| 프로젝트 일정, 로드맵 | Timeline | `/diagram timeline` |
| 사용자-시스템 상호작용 | Use Case | `/diagram usecase` |

---

## 1. Flowchart (플로우차트)

### 언제 사용하는가

- **데이터 파이프라인**: ETL 프로세스, 데이터 흐름
- **비즈니스 로직**: 의사결정 분기, 조건 처리
- **알고리즘 설명**: 단계별 처리 과정
- **프로세스 문서화**: 업무 절차, 승인 흐름

### 적합한 질문

- "이 데이터는 어떻게 처리되는가?"
- "어떤 조건에서 분기가 발생하는가?"
- "입력에서 출력까지 어떤 단계를 거치는가?"

### 예시 시나리오

```
시나리오: GTFS 데이터 처리 파이프라인
├── 데이터 소스 3개 (버스, 지하철, 인구통계)
├── 검증 → 정제 → 변환 → 적재 단계
└── 최종 분석 결과 출력

→ Flowchart 선택
```

### 대안

- **복잡한 병렬 처리**: Activity Diagram 고려
- **시간 순서 강조**: Sequence Diagram 고려

---

## 2. Sequence Diagram (시퀀스 다이어그램)

### 언제 사용하는가

- **API 호출 흐름**: REST/GraphQL 요청-응답
- **마이크로서비스 통신**: 서비스 간 메시지 교환
- **함수 호출 순서**: 계층 간 호출 관계
- **인증 흐름**: OAuth, JWT 토큰 교환

### 적합한 질문

- "이 요청은 어떤 순서로 처리되는가?"
- "어떤 서비스들이 상호작용하는가?"
- "에러 발생 시 어떤 응답이 반환되는가?"

### 예시 시나리오

```
시나리오: 사용자 로그인 API 호출
├── Client → API Gateway → Auth Service → Database
├── 토큰 발급 및 검증 과정
└── 성공/실패 분기 응답

→ Sequence Diagram 선택
```

### 대안

- **상태 변화 중심**: State Diagram 고려
- **전체 아키텍처 표현**: Architecture Diagram 고려

---

## 3. Class Diagram (클래스 다이어그램)

### 언제 사용하는가

- **데이터 모델 설계**: Pydantic, dataclass 스키마
- **OOP 구조 문서화**: 상속, 합성, 의존 관계
- **API 스키마**: Request/Response 모델
- **도메인 모델**: DDD 엔티티, 값 객체

### 적합한 질문

- "이 클래스들은 어떤 관계인가?"
- "상속 구조는 어떻게 되어 있는가?"
- "어떤 속성과 메서드가 있는가?"

### 예시 시나리오

```
시나리오: 주문 시스템 도메인 모델
├── User → Order → OrderItem → Product
├── BaseModel 상속 관계
└── 각 클래스의 속성과 메서드

→ Class Diagram 선택
```

### 대안

- **DB 테이블 관계**: ER Diagram 고려 (FK/PK 명시)
- **런타임 상호작용**: Sequence Diagram 고려

---

## 4. ER Diagram (엔티티 관계 다이어그램)

### 언제 사용하는가

- **데이터베이스 스키마 설계**: 테이블 구조
- **ORM 모델 문서화**: SQLAlchemy, Django 모델
- **데이터 마이그레이션**: 스키마 변경 계획
- **정규화 검토**: 테이블 관계 분석

### 적합한 질문

- "테이블 간 관계는 어떻게 되는가?"
- "어떤 FK/PK 관계가 있는가?"
- "1:N, N:M 관계는 어디에 있는가?"

### 예시 시나리오

```
시나리오: 대중교통 분석 DB 스키마
├── STOP, ROUTE, STOP_TIME 테이블
├── FK 관계: STOP_TIME → STOP, ROUTE
└── 각 컬럼의 타입과 제약조건

→ ER Diagram 선택
```

### 대안

- **객체 구조 중심**: Class Diagram 고려
- **구현 코드 관계**: Class Diagram + 스테레오타입

---

## 5. State Diagram (상태 다이어그램)

### 언제 사용하는가

- **상태 머신**: FSM 구현 문서화
- **라이프사이클 관리**: Order, Ticket, Job 상태
- **워크플로우 상태**: 승인 프로세스, 문서 상태
- **UI 상태 관리**: 컴포넌트 상태 전이

### 적합한 질문

- "이 객체는 어떤 상태를 가질 수 있는가?"
- "어떤 이벤트로 상태가 전이되는가?"
- "최종 상태는 무엇인가?"

### 예시 시나리오

```
시나리오: 분석 Job 상태 관리
├── Created → Pending → Running → Completed/Failed
├── Retry 가능 상태
└── Cancel 이벤트 처리

→ State Diagram 선택
```

### 대안

- **단순 조건 분기**: Flowchart 고려
- **시간 순서 중심**: Sequence Diagram 고려

---

## 6. Architecture Diagram (아키텍처 다이어그램)

### 언제 사용하는가

- **시스템 구조 문서화**: 컴포넌트 배치
- **마이크로서비스 구조**: 서비스 간 관계
- **배포 구조**: 인프라 구성
- **C4 모델**: Context, Container, Component

### 적합한 질문

- "시스템은 어떤 컴포넌트로 구성되는가?"
- "어떤 서비스가 어떤 데이터 저장소를 사용하는가?"
- "외부 시스템과 어떻게 연결되는가?"

### 예시 시나리오

```
시나리오: 대중교통 분석 시스템 아키텍처
├── Client Layer: Web, Mobile
├── Service Layer: API, Auth, Analysis
├── Data Layer: PostgreSQL, Redis, S3
└── External: GTFS API, Census API

→ Architecture Diagram 선택
```

### 대안

- **런타임 호출 순서**: Sequence Diagram 고려
- **배포 인프라 상세**: 전용 인프라 도구 (Draw.io, Lucidchart)

---

## 7. Activity Diagram (활동 다이어그램)

### 언제 사용하는가

- **병렬 처리 표현**: Fork/Join 패턴
- **복잡한 워크플로우**: 동시 실행 경로
- **비즈니스 프로세스**: 병합/분기가 많은 흐름

### 적합한 질문

- "어떤 작업이 병렬로 실행되는가?"
- "모든 병렬 작업이 완료된 후 다음 단계는?"
- "동기화 지점은 어디인가?"

### 예시 시나리오

```
시나리오: 데이터 검증 파이프라인
├── 입력 수신
├── Fork: 스키마 검증 || 중복 체크 || 범위 검증
├── Join: 모든 검증 완료
└── 결과 집계 및 출력

→ Activity Diagram 선택
```

### 대안

- **단순 순차 흐름**: Flowchart 고려
- **상태 중심**: State Diagram 고려

---

## 8. Timeline (타임라인)

### 언제 사용하는가

- **프로젝트 로드맵**: 마일스톤 시각화
- **릴리스 계획**: 버전별 기능 계획
- **히스토리 문서화**: 주요 이벤트 연대기

### 적합한 질문

- "프로젝트 일정은 어떻게 되는가?"
- "각 단계에서 무엇을 완료해야 하는가?"
- "주요 마일스톤은 언제인가?"

### 예시 시나리오

```
시나리오: 대중교통 분석 프로젝트 로드맵
├── Q1: 데이터 수집, 피처 엔지니어링
├── Q2: 모델 개발, 검증
└── Q3: API 개발, 배포

→ Timeline 선택
```

### 대안

- **상세 Gantt 차트**: MS Project, Jira
- **마일스톤 관계**: Flowchart 고려

---

## 9. Use Case Diagram (유스케이스 다이어그램)

### 언제 사용하는가

- **요구사항 문서화**: 기능 요구사항 시각화
- **사용자 시나리오**: 액터-시스템 상호작용
- **범위 정의**: 시스템 경계 명시

### 적합한 질문

- "사용자가 이 시스템으로 무엇을 할 수 있는가?"
- "어떤 역할이 어떤 기능에 접근하는가?"
- "시스템 범위는 어디까지인가?"

### 예시 시나리오

```
시나리오: 대중교통 분석 대시보드 요구사항
├── User: 대시보드 조회, 리포트 다운로드
├── Admin: 사용자 관리, 설정 변경
└── System: 데이터 자동 갱신

→ Use Case Diagram 선택
```

### 대안

- **상세 상호작용**: Sequence Diagram 고려
- **UI 흐름**: Flowchart 고려

---

## 결정 트리

```
시각화 대상이 무엇인가?
│
├─ 시간/순서가 중요하다
│   ├─ 여러 액터 간 상호작용 → Sequence Diagram
│   ├─ 상태 변화 → State Diagram
│   └─ 프로세스 단계 → Flowchart / Activity
│
├─ 구조/관계가 중요하다
│   ├─ DB 스키마 → ER Diagram
│   ├─ 클래스 구조 → Class Diagram
│   └─ 시스템 컴포넌트 → Architecture
│
├─ 일정/계획이다
│   └─ → Timeline
│
└─ 요구사항/기능 범위다
    └─ → Use Case Diagram
```

---

## 복합 사용 예시

### 시스템 문서화 세트

하나의 시스템을 완전히 문서화하려면 여러 다이어그램이 필요하다:

```
1. Architecture Diagram - 전체 시스템 구조
2. ER Diagram - 데이터베이스 스키마
3. Class Diagram - 핵심 도메인 모델
4. Sequence Diagram - 주요 API 흐름
5. State Diagram - 주요 엔티티 상태
```

### API 문서화 세트

```
1. Architecture Diagram - API 서비스 위치
2. Sequence Diagram - 인증 흐름
3. Sequence Diagram - 주요 엔드포인트별 흐름
4. Class Diagram - Request/Response 스키마
```

### 데이터 파이프라인 문서화

```
1. Flowchart - ETL 전체 흐름
2. ER Diagram - 데이터 스키마
3. State Diagram - Job 상태 관리
4. Timeline - 파이프라인 스케줄
```

---

## 사용하지 말아야 할 상황

| 상황 | 왜 안 되는가 | 대안 |
|------|-------------|------|
| 막대/원/선 차트 데이터 | Mermaid는 데이터 시각화 도구가 아님 | matplotlib, plotly |
| 50+ 노드 조직도 | 복잡도 초과, 가독성 저하 | Visio, Lucidchart |
| 정밀 Gantt 차트 | 의존성, 리소스 관리 불가 | MS Project, Jira |
| Git 히스토리 | 전용 도구가 더 정확 | git log --graph |
| 지도/위치 기반 | 공간 데이터 지원 없음 | Leaflet, Mapbox |

---

## 참고

- `mermaid-syntax.md` - 구문 상세 레퍼런스
- Mermaid Live Editor: https://mermaid.live
