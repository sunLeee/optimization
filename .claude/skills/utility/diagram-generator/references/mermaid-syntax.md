# Mermaid Syntax Reference

## 구문 오류 방지 핵심 규칙

### 1. 따옴표 처리

```mermaid
%% GOOD - 따옴표 없이
Node[Simple Label]

%% GOOD - 특수문자 포함 시 따옴표
Node["Label with (parentheses) or [brackets]"]

%% BAD - 중첩 따옴표
Node["Label with "nested" quotes"]

%% SOLUTION - 작은따옴표 사용
Node["Label with 'nested' quotes"]
```

### 2. 멀티라인 라벨

```mermaid
%% GOOD - br 태그
Node["First Line<br/>Second Line"]

%% GOOD - 여러 줄
Node["Line 1<br/>Line 2<br/>Line 3"]

%% BAD - 실제 줄바꿈 사용
Node["First Line
Second Line"]
```

### 3. 엣지 라벨

```mermaid
%% GOOD - 간단한 라벨
A -->|Yes| B
A -->|No| C

%% BAD - 엣지 라벨에 따옴표
A -->|"Yes"| B
```

### 4. 서브그래프 ID

```mermaid
%% GOOD - 공백 없는 ID + 따옴표 라벨
subgraph DBLayer["Database Layer"]

%% BAD - 공백 포함 ID
subgraph Database Layer

%% BAD - 특수문자 ID 직접 사용
subgraph DB-Layer
```

### 5. 스타일 정의 순서

```mermaid
flowchart LR
    %% 1단계: 모든 노드 정의
    A[Node A] --> B[Node B]
    B --> C[Node C]

    %% 2단계: 스타일 적용 (노드 정의 후)
    style A fill:#f96,stroke:#333
    style B fill:#69b,stroke:#333

    %% 또는 classDef 사용
    classDef critical fill:#f66,stroke:#333
    class A critical
```

---

## Flowchart

### 기본 구조

```mermaid
flowchart TD
    %% 방향: TD, TB, BT, LR, RL
    A[사각형] --> B(둥근 사각형)
    B --> C{다이아몬드}
    C -->|예| D[[서브루틴]]
    C -->|아니오| E[(데이터베이스)]
    D --> F((원))
    E --> F
```

### 노드 형태

| 구문 | 형태 | 용도 |
|------|------|------|
| `[text]` | 사각형 | 일반 프로세스 |
| `(text)` | 둥근 사각형 | 시작/종료 |
| `{text}` | 다이아몬드 | 조건/분기 |
| `[(text)]` | 원통형 | 데이터베이스 |
| `[[text]]` | 서브루틴 | 서브프로세스 |
| `((text))` | 원 | 연결점 |
| `([text])` | 스타디움 | 시작/종료 |
| `>text]` | 비대칭 | 특수 용도 |
| `{{text}}` | 육각형 | 준비 단계 |

### 연결선

```mermaid
flowchart LR
    A --> B   %% 화살표
    B --- C   %% 선
    C -.-> D  %% 점선 화살표
    D ==> E   %% 굵은 화살표
    E --o F   %% 원 끝
    F --x G   %% X 끝
    G <--> H  %% 양방향
```

### 서브그래프

```mermaid
flowchart TB
    subgraph Frontend["Frontend Layer"]
        A[React App]
        B[Vue App]
    end

    subgraph Backend["Backend Layer"]
        C[API Server]
        D[Worker]
    end

    A --> C
    B --> C
    C --> D
```

### 데이터 파이프라인 템플릿

```mermaid
flowchart TD
    subgraph Extract
        A[Source 1] --> D[Staging]
        B[Source 2] --> D
        C[Source 3] --> D
    end

    subgraph Transform
        D --> E[Validation]
        E --> F[Cleaning]
        F --> G[Feature Engineering]
    end

    subgraph Load
        G --> H[(Data Warehouse)]
        H --> I[Analytics]
        H --> J[ML Pipeline]
    end

    style E fill:#f9f,stroke:#333
    style H fill:#bbf,stroke:#333
```

---

## Sequence Diagram

### 기본 구조

```mermaid
sequenceDiagram
    participant C as Client
    participant A as API Server
    participant D as Database

    C->>+A: GET /users
    A->>D: SELECT * FROM users
    D-->>A: Result Set
    A-->>-C: JSON Response
```

### 참가자 유형

```mermaid
sequenceDiagram
    participant A as API
    actor U as User
    participant D as Database

    U->>A: Request
    A->>D: Query
    D-->>A: Data
    A-->>U: Response
```

### 메시지 유형

| 구문 | 의미 |
|------|------|
| `->>` | 동기 메시지 (실선) |
| `-->>` | 응답 (점선) |
| `->>+` | 활성화 시작 |
| `-->>-` | 활성화 종료 |
| `-x` | 비동기 (즉시 반환) |
| `-)` | 비동기 응답 |

### 조건/반복

```mermaid
sequenceDiagram
    participant U as User
    participant S as Service
    participant D as Database

    U->>S: Login Request

    alt Valid Credentials
        S->>D: Verify
        D-->>S: OK
        S-->>U: Success + Token
    else Invalid Credentials
        S-->>U: 401 Unauthorized
    end

    loop Health Check
        S->>S: Check Status
    end

    opt Cache Available
        S->>S: Return Cached
    end
```

### API 호출 템플릿

```mermaid
sequenceDiagram
    participant C as Client
    participant G as API Gateway
    participant A as Auth Service
    participant S as Service
    participant D as Database

    C->>G: Request + Token
    G->>A: Validate Token
    A-->>G: Valid

    G->>+S: Forward Request
    S->>D: Query
    D-->>S: Data
    S-->>-G: Response

    G-->>C: Final Response

    Note over G,A: Authentication Layer
    Note over S,D: Business Layer
```

---

## Class Diagram

### 기본 구조

```mermaid
classDiagram
    class ClassName {
        <<interface>>
        +publicAttr: type
        -privateAttr: type
        #protectedAttr: type
        +publicMethod() returnType
        -privateMethod()
        #protectedMethod()
    }
```

### 접근 제어자

| 기호 | 의미 |
|------|------|
| `+` | public |
| `-` | private |
| `#` | protected |
| `~` | package/internal |

### 관계 유형

```mermaid
classDiagram
    %% 상속
    Animal <|-- Dog : extends

    %% 합성 (강한 소유)
    Car *-- Engine : has

    %% 집합 (약한 소유)
    Team o-- Player : contains

    %% 연관
    Student --> Course : enrolls

    %% 의존
    Service ..> Repository : uses

    %% 구현
    List ..|> Collection : implements
```

### 스테레오타입

```mermaid
classDiagram
    class AbstractClass {
        <<abstract>>
        +abstractMethod()*
    }

    class Interface {
        <<interface>>
        +method()
    }

    class Enumeration {
        <<enumeration>>
        VALUE1
        VALUE2
    }

    class Service {
        <<service>>
        +process()
    }
```

### 데이터 모델 템플릿

```mermaid
classDiagram
    class BaseModel {
        <<abstract>>
        +id: int
        +created_at: datetime
        +updated_at: datetime
        +save()
        +delete()
    }

    class User {
        +email: str
        +name: str
        +password_hash: str
        +is_active: bool
        +authenticate(password) bool
        +get_orders() List~Order~
    }

    class Order {
        +user_id: int
        +status: OrderStatus
        +total: Decimal
        +items: List~OrderItem~
        +calculate_total()
        +process()
    }

    class OrderItem {
        +order_id: int
        +product_id: int
        +quantity: int
        +price: Decimal
    }

    BaseModel <|-- User
    BaseModel <|-- Order
    BaseModel <|-- OrderItem
    User "1" --> "*" Order : places
    Order "1" *-- "*" OrderItem : contains
```

---

## ER Diagram

### 기본 구조

```mermaid
erDiagram
    ENTITY1 {
        int id PK
        string name
        int foreign_id FK
        string unique_field UK
    }

    ENTITY1 ||--o{ ENTITY2 : "relationship"
```

### 관계 표기

| 왼쪽 | 오른쪽 | 의미 |
|------|--------|------|
| `\|\|` | `\|\|` | 1:1 |
| `\|\|` | `o{` | 1:N (0 이상) |
| `\|\|` | `\|{` | 1:N (1 이상) |
| `o\|` | `o{` | 0..1:N |

### 데이터베이스 스키마 템플릿

```mermaid
erDiagram
    USER {
        int id PK
        string email UK
        string name
        string password_hash
        boolean is_active
        datetime created_at
    }

    ORDER {
        int id PK
        int user_id FK
        string status
        decimal total
        datetime created_at
    }

    ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal price
    }

    PRODUCT {
        int id PK
        string name
        string description
        decimal price
        int stock
    }

    USER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : "included in"
```

---

## State Diagram

### 기본 구조

```mermaid
stateDiagram-v2
    [*] --> State1
    State1 --> State2: event
    State2 --> State3
    State3 --> [*]
```

### 복합 상태

```mermaid
stateDiagram-v2
    [*] --> Active

    state Active {
        [*] --> Idle
        Idle --> Processing: start
        Processing --> Idle: complete
        Processing --> Error: fail
        Error --> Idle: retry
    }

    Active --> Inactive: deactivate
    Inactive --> Active: activate
    Inactive --> [*]: terminate
```

### Fork/Join

```mermaid
stateDiagram-v2
    [*] --> Ready

    state fork_state <<fork>>
    Ready --> fork_state

    fork_state --> Task1
    fork_state --> Task2
    fork_state --> Task3

    state join_state <<join>>
    Task1 --> join_state
    Task2 --> join_state
    Task3 --> join_state

    join_state --> Complete
    Complete --> [*]
```

### 주문 상태 템플릿

```mermaid
stateDiagram-v2
    [*] --> Created

    Created --> Pending: submit
    Pending --> Confirmed: confirm
    Pending --> Cancelled: cancel

    Confirmed --> Processing: start_processing
    Processing --> Shipped: ship

    Shipped --> Delivered: deliver
    Shipped --> Returned: return

    Delivered --> [*]
    Cancelled --> [*]
    Returned --> Refunded: process_refund
    Refunded --> [*]

    note right of Processing
        Inventory deducted
        at this stage
    end note
```

---

## Timeline

### 기본 구조

```mermaid
timeline
    title Project Timeline
    section Phase 1
        2025-01 : Task 1
        2025-02 : Task 2
    section Phase 2
        2025-03 : Task 3
        2025-04 : Task 4
```

### 프로젝트 로드맵 템플릿

```mermaid
timeline
    title 2025 Product Roadmap

    section Q1
        Jan : MVP Development
            : Core Features
        Feb : Alpha Testing
            : Bug Fixes
        Mar : Beta Release

    section Q2
        Apr : User Feedback
            : Performance Tuning
        May : Feature Expansion
        Jun : Public Launch

    section Q3
        Jul : Scale Infrastructure
        Aug : International Launch
        Sep : Enterprise Features
```

---

## 스타일링

### 개별 스타일

```mermaid
flowchart LR
    A[Critical] --> B[Warning] --> C[Success] --> D[Info]

    style A fill:#f66,stroke:#333,stroke-width:2px
    style B fill:#f96,stroke:#333
    style C fill:#9f9,stroke:#333
    style D fill:#69b,stroke:#333
```

### 클래스 정의

```mermaid
flowchart LR
    A[Node 1]:::critical --> B[Node 2]:::warning
    B --> C[Node 3]:::success

    classDef critical fill:#f66,stroke:#333,stroke-width:2px
    classDef warning fill:#f96,stroke:#333
    classDef success fill:#9f9,stroke:#333
```

### 색상 팔레트

| 용도 | 색상 코드 | 예시 |
|------|----------|------|
| Critical/Error | `#f66` | 오류, 경고 |
| Warning | `#f96` | 주의 |
| Success | `#9f9` | 성공, 완료 |
| Info/Primary | `#69b` | 정보, 주요 |
| Database | `#bbf` | 데이터 저장소 |
| External | `#ddd` | 외부 시스템 |

---

## 주석

```mermaid
flowchart TD
    %% 이것은 주석입니다
    %% 렌더링되지 않습니다

    A[Start] --> B[Process]

    %% 섹션 구분
    B --> C[End]
```

---

## 검증 체크리스트

생성된 Mermaid 코드 검증:

```
[ ] 중첩 따옴표 없음
[ ] 멀티라인에 <br/> 사용
[ ] 엣지 라벨 따옴표 불필요
[ ] 서브그래프 ID 유효 (공백/특수문자 없음)
[ ] 스타일 정의가 노드 정의 후에 위치
[ ] 모든 노드 ID 고유
[ ] 모든 참조된 노드 정의됨
[ ] Mermaid Live Editor에서 렌더링 성공
```

## 참고 자료

- Mermaid Live Editor: https://mermaid.live
- Mermaid 공식 문서: https://mermaid.js.org/
