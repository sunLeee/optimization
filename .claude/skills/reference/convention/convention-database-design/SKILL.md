---
name: convention-database-design
triggers:
  - "convention database design"
description: "데이터베이스 설계(Database Design) 컨벤션 참조 스킬. 정규화, 인덱싱, 쿼리 최적화, 트랜잭션 관리로 성능이 우수하고 확장 가능한 DB 스키마를 설계한다."
argument-hint: "[섹션] - normalization, indexing, query-optimization, migration"
disable-model-invocation: false
user-invocable: false
allowed-tools:
  - Read
  - Glob
  - Grep
model: claude-sonnet-4-6[1m]
context: |
  데이터베이스 스키마 설계 및 성능 최적화 전략을 제공한다.
  정규화, 인덱싱, 트랜잭션을 통해 안정적인 DB를 구축한다.
agent: |
  데이터베이스 설계 전문가.
  정규화, 인덱싱, 쿼리 최적화의 모범 사례를 제시한다.
hooks:
  pre_execution: []
  post_execution: []
category: 컨벤션 참조
skill-type: Atomic
references: []
referenced-by: []

---
# 데이터베이스 설계 컨벤션

정규화, 인덱싱, 쿼리 최적화, 트랜잭션으로 성능 우수한 DB 스키마를 설계하는 규칙.

## 목적

- **정규화**: 데이터 중복 제거 및 무결성 보장
- **인덱싱**: 쿼리 성능 향상
- **쿼리 최적화**: 실행 계획 분석 및 개선
- **트랜잭션**: ACID 속성으로 데이터 일관성 유지
- **마이그레이션**: 스키마 변경 버전 관리

---

## 1. 정규화 (Normalization)

### 1.1 정규화 단계

**1NF (First Normal Form)**:
- 각 컬럼은 원자값(atomic value)만 가짐
- 반복 그룹 제거

**Before (비정규화)**:
```sql
-- ❌ 1NF 위반: 전화번호가 쉼표로 구분된 문자열
CREATE TABLE users_bad (
    user_id INT PRIMARY KEY,
    name VARCHAR(100),
    phone_numbers VARCHAR(255)  -- "010-1234-5678,010-9876-5432"
);
```

**After (1NF)**:
```sql
-- ✅ 1NF: 전화번호를 별도 테이블로 분리
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE phone_numbers (
    phone_id INT PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    phone_number VARCHAR(20)
);
```

**2NF (Second Normal Form)**:
- 1NF 만족
- 부분 종속 제거 (모든 비키 속성이 기본키 전체에 종속)

**Before (1NF만 만족)**:
```sql
-- ❌ 2NF 위반: order_date는 order_id에만 종속
CREATE TABLE order_items_bad (
    order_id INT,
    product_id INT,
    order_date DATE,  -- 부분 종속
    quantity INT,
    PRIMARY KEY (order_id, product_id)
);
```

**After (2NF)**:
```sql
-- ✅ 2NF: order 테이블 분리
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    order_date DATE
);

CREATE TABLE order_items (
    order_id INT REFERENCES orders(order_id),
    product_id INT,
    quantity INT,
    PRIMARY KEY (order_id, product_id)
);
```

**3NF (Third Normal Form)**:
- 2NF 만족
- 이행 종속 제거 (비키 속성 간 종속 제거)

**Before (2NF만 만족)**:
```sql
-- ❌ 3NF 위반: department_name은 department_id에 종속
CREATE TABLE employees_bad (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100),
    department_id INT,
    department_name VARCHAR(100)  -- 이행 종속
);
```

**After (3NF)**:
```sql
-- ✅ 3NF: department 테이블 분리
CREATE TABLE departments (
    department_id INT PRIMARY KEY,
    department_name VARCHAR(100)
);

CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100),
    department_id INT REFERENCES departments(department_id)
);
```

### 1.2 반정규화 (De-normalization) 전략

**언제 반정규화를 고려하는가?**:
- 읽기 성능이 중요하고 업데이트가 적을 때
- JOIN 비용이 매우 클 때
- 데이터 중복보다 성능이 우선일 때

**예시: 주문 총액 컬럼 추가**:
```sql
-- 반정규화: 계산 결과를 저장
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    order_date DATE,
    total_amount DECIMAL(10, 2)  -- 반정규화 (SUM 계산 결과)
);

-- 트리거로 일관성 유지
CREATE TRIGGER update_order_total
AFTER INSERT OR UPDATE OR DELETE ON order_items
FOR EACH ROW
BEGIN
    UPDATE orders
    SET total_amount = (
        SELECT SUM(quantity * unit_price)
        FROM order_items
        WHERE order_id = NEW.order_id
    )
    WHERE order_id = NEW.order_id;
END;
```

---

## 2. 인덱싱 (Indexing)

### 2.1 인덱스 타입

**B-Tree 인덱스** (기본값):
```sql
-- 범위 검색에 유리
CREATE INDEX idx_users_email ON users(email);

-- 복합 인덱스 (최좌측 매칭 원칙)
CREATE INDEX idx_orders_user_date
ON orders(user_id, order_date);
```

**Hash 인덱스**:
```sql
-- 동등 비교 (=)만 지원, 빠름
CREATE INDEX idx_users_username_hash
ON users USING HASH (username);
```

**Full-Text 인덱스**:
```sql
-- 텍스트 검색
CREATE FULLTEXT INDEX idx_posts_content
ON posts(content);

-- 사용
SELECT * FROM posts
WHERE MATCH(content) AGAINST('keyword');
```

### 2.2 인덱스 설계 원칙

**1. WHERE 절에 자주 사용되는 컬럼**:
```sql
-- 자주 검색되는 컬럼
CREATE INDEX idx_users_status ON users(status);
```

**2. JOIN 조건 컬럼**:
```sql
-- Foreign Key에 인덱스
CREATE INDEX idx_orders_user_id ON orders(user_id);
```

**3. ORDER BY/GROUP BY 컬럼**:
```sql
-- 정렬에 사용되는 컬럼
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);
```

**4. 복합 인덱스 순서**:
```sql
-- 규칙: 카디널리티 높은 컬럼을 먼저
-- status (낮음) vs user_id (높음)
CREATE INDEX idx_orders_user_status
ON orders(user_id, status);  -- ✅ 올바름

-- ❌ 잘못된 순서
CREATE INDEX idx_orders_status_user
ON orders(status, user_id);
```

### 2.3 인덱스 분석

```sql
-- PostgreSQL: 인덱스 사용 확인
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'test@example.com';

-- MySQL: 인덱스 힌트
SELECT * FROM users
USE INDEX (idx_users_email)
WHERE email = 'test@example.com';
```

---

## 3. 쿼리 최적화

### 3.1 EXPLAIN 분석

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""쿼리 최적화 분석 모듈.

Author: taeyang lee
Created: 2026-01-21 12:00(KST, UTC+09:00)
Modified: 2026-01-21 12:00(KST, UTC+09:00)
"""

from sqlalchemy import create_engine, text


def analyze_query(engine, query: str) -> dict:
    """쿼리 실행 계획을 분석한다.

    Args:
        engine: SQLAlchemy 엔진.
        query (str): 분석할 SQL 쿼리.

    Returns:
        dict: 실행 계획 분석 결과.

    Logics:
        1. EXPLAIN ANALYZE 실행.
        2. 실행 계획 파싱.
        3. 비용, 실행 시간 추출.
        4. 인덱스 사용 여부 확인.

    Example:
        >>> engine = create_engine('postgresql://...')
        >>> query = "SELECT * FROM users WHERE email = 'test@example.com'"
        >>> result = analyze_query(engine, query)
        >>> print(f"실행 시간: {result['execution_time']}ms")
    """
    with engine.connect() as conn:
        # EXPLAIN ANALYZE 실행
        explain_query = f"EXPLAIN ANALYZE {query}"
        result = conn.execute(text(explain_query))

        plan_lines = [row[0] for row in result]

        # 실행 시간 추출 (마지막 줄)
        last_line = plan_lines[-1]
        execution_time = None

        if 'Execution Time:' in last_line:
            execution_time = float(
                last_line.split(':')[1].strip().split()[0]
            )

        # 인덱스 사용 확인
        uses_index = any(
            'Index Scan' in line or 'Bitmap Index Scan' in line
            for line in plan_lines
        )

        return {
            'query': query,
            'execution_time_ms': execution_time,
            'uses_index': uses_index,
            'plan': '\n'.join(plan_lines)
        }
```

### 3.2 N+1 쿼리 문제 해결

**❌ Bad (N+1 Problem)**:
```python
# 1번의 users 쿼리 + N번의 orders 쿼리
users = session.query(User).all()

for user in users:
    # 각 user마다 쿼리 실행 (N번)
    orders = session.query(Order).filter_by(
        user_id=user.id
    ).all()
    print(f"{user.name}: {len(orders)} orders")
```

**✅ Good (Eager Loading)**:
```python
from sqlalchemy.orm import joinedload

# 1번의 JOIN 쿼리로 해결
users = session.query(User).options(
    joinedload(User.orders)
).all()

for user in users:
    # 추가 쿼리 없음
    print(f"{user.name}: {len(user.orders)} orders")
```

### 3.3 쿼리 최적화 체크리스트

- [ ] SELECT * 대신 필요한 컬럼만 조회
- [ ] WHERE 절에 인덱스 활용
- [ ] JOIN 순서 최적화 (작은 테이블 먼저)
- [ ] LIMIT 사용으로 결과 제한
- [ ] DISTINCT 대신 GROUP BY 고려
- [ ] 서브쿼리 대신 JOIN 고려
- [ ] 함수 사용 최소화 (WHERE LOWER(email) ❌)

---

## 4. 트랜잭션 관리

### 4.1 ACID 속성

```python
from sqlalchemy.orm import Session
from contextlib import contextmanager


@contextmanager
def transaction_scope(session: Session):
    """트랜잭션 컨텍스트 매니저.

    ACID 속성:
    - Atomicity: 모두 성공 또는 모두 실패.
    - Consistency: 데이터 무결성 유지.
    - Isolation: 동시 트랜잭션 간 격리.
    - Durability: 커밋 후 영구 저장.

    Logics:
        1. 트랜잭션 시작.
        2. 작업 실행.
        3. 성공 시 commit, 실패 시 rollback.
        4. finally에서 세션 정리.

    Example:
        >>> with transaction_scope(session) as tx_session:
        ...     user = User(name='Alice')
        ...     tx_session.add(user)
        ...     # 예외 발생 시 자동 rollback
    """
    try:
        yield session
        session.commit()  # 성공: 커밋
    except Exception as e:
        session.rollback()  # 실패: 롤백
        raise
    finally:
        session.close()  # 정리
```

### 4.2 Isolation Level

```python
from sqlalchemy import create_engine

# Isolation Level 설정
engine = create_engine(
    'postgresql://user:pass@localhost/mydb',
    isolation_level='REPEATABLE READ'
)

# 트랜잭션별 설정
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

session.connection(
    execution_options={'isolation_level': 'SERIALIZABLE'}
)
```

**Isolation Levels**:

| Level | 설명 | Dirty Read | Non-Repeatable Read | Phantom Read |
|-------|------|------------|---------------------|--------------|
| READ UNCOMMITTED | 커밋 안 된 데이터 읽기 가능 | ✅ | ✅ | ✅ |
| READ COMMITTED | 커밋된 데이터만 읽기 (기본값) | ❌ | ✅ | ✅ |
| REPEATABLE READ | 트랜잭션 내 일관된 읽기 | ❌ | ❌ | ✅ |
| SERIALIZABLE | 완전 격리 (순차 실행과 동일) | ❌ | ❌ | ❌ |

### 4.3 Optimistic Locking

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """사용자 모델 (Optimistic Locking 사용).

    version 컬럼으로 동시 업데이트 감지.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(255))
    version = Column(Integer, default=0, nullable=False)

    __mapper_args__ = {
        'version_id_col': version,
        'version_id_generator': False
    }


# 사용 예시
def update_user_safe(session, user_id: int, new_name: str):
    """Optimistic Locking으로 안전하게 업데이트한다.

    Logics:
        1. 사용자 조회 (version 포함).
        2. 데이터 수정.
        3. 커밋 시도.
        4. version 불일치 시 StaleDataError 발생.
        5. 재시도 또는 오류 처리.

    Example:
        >>> try:
        ...     update_user_safe(session, 1, 'New Name')
        ... except StaleDataError:
        ...     print("다른 사용자가 이미 수정함")
    """
    from sqlalchemy.orm.exc import StaleDataError

    try:
        user = session.query(User).filter_by(id=user_id).one()
        user.name = new_name
        session.commit()  # version 자동 증가

    except StaleDataError:
        session.rollback()
        raise Exception(
            "동시 수정 감지. 최신 데이터 확인 후 재시도 필요."
        )
```

---

## 5. 스키마 마이그레이션

### 5.1 Alembic 설정

```bash
# Alembic 초기화
alembic init migrations

# 마이그레이션 생성
alembic revision --autogenerate -m "Add users table"

# 마이그레이션 실행
alembic upgrade head

# 롤백
alembic downgrade -1
```

### 5.2 마이그레이션 스크립트 예시

**migrations/versions/001_add_users_table.py**:
```python
"""Add users table

Revision ID: 001
Revises:
Create Date: 2026-01-21 12:00:00
"""

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """테이블 생성 (Forward)."""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('version', sa.Integer(), default=0)
    )

    # 인덱스 생성
    op.create_index('idx_users_email', 'users', ['email'])


def downgrade():
    """테이블 삭제 (Rollback)."""
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
```

---

## 6. 성능 튜닝

### 6.1 Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Connection Pool 설정
engine = create_engine(
    'postgresql://user:pass@localhost/mydb',
    poolclass=QueuePool,
    pool_size=10,          # 기본 연결 수
    max_overflow=20,       # 초과 연결 수
    pool_recycle=3600,     # 1시간마다 연결 재생성
    pool_pre_ping=True,    # 연결 유효성 사전 확인
    echo_pool=True         # Pool 로깅
)
```

### 6.2 쿼리 캐싱

```python
from functools import lru_cache


@lru_cache(maxsize=128)
def get_user_by_id(user_id: int) -> dict:
    """사용자를 ID로 조회 (캐싱).

    Logics:
        1. LRU 캐시 확인.
        2. 캐시 미스 시 DB 조회.
        3. 결과를 캐시에 저장.

    Example:
        >>> user = get_user_by_id(1)  # DB 조회
        >>> user = get_user_by_id(1)  # 캐시 사용
    """
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM users WHERE id = :id"),
            {'id': user_id}
        )
        row = result.fetchone()
        return dict(row) if row else None
```

### 6.3 Batch Insert

```python
from sqlalchemy.orm import Session


def bulk_insert_users(session: Session, users: list) -> None:
    """대량 사용자 삽입 (Batch).

    Args:
        session (Session): DB 세션.
        users (list): 사용자 딕셔너리 리스트.

    Logics:
        1. bulk_insert_mappings 사용 (빠름).
        2. 개별 INSERT 대신 단일 쿼리.
        3. 트랜잭션으로 원자성 보장.

    Example:
        >>> users_data = [
        ...     {'name': 'Alice', 'email': 'alice@example.com'},
        ...     {'name': 'Bob', 'email': 'bob@example.com'}
        ... ]
        >>> bulk_insert_users(session, users_data)
    """
    try:
        session.bulk_insert_mappings(User, users)
        session.commit()
        print(f"✅ {len(users)}명 사용자 삽입 성공")

    except Exception as e:
        session.rollback()
        print(f"❌ 삽입 실패: {str(e)}")
        raise
```

---

## 7. DB 설계 체크리스트

구현 완료 후 다음을 확인하세요:

- [ ] 정규화 (최소 3NF)
- [ ] Primary Key 정의 (모든 테이블)
- [ ] Foreign Key 관계 설정
- [ ] 인덱스 생성 (WHERE, JOIN 컬럼)
- [ ] 복합 인덱스 순서 최적화
- [ ] EXPLAIN으로 쿼리 분석
- [ ] N+1 쿼리 문제 해결
- [ ] 트랜잭션 사용 (ACID)
- [ ] Isolation Level 설정
- [ ] Connection Pool 설정
- [ ] 스키마 마이그레이션 스크립트
- [ ] Rollback 계획

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| [@skills/convention-data-handling/SKILL.md] | 데이터 처리 |
| [@skills/convention-data-validation/SKILL.md] | 데이터 검증 |
| [@skills/convention-error-handling/SKILL.md] | 트랜잭션 오류 처리 |
| [@skills/convention-monitoring-alerting/SKILL.md] | 쿼리 성능 모니터링 |

---

## 참고

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- SQLAlchemy: https://www.sqlalchemy.org/
- Alembic: https://alembic.sqlalchemy.org/
- Database Normalization: https://en.wikipedia.org/wiki/Database_normalization

---

## Changelog

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-21 | 1.0.0 | 초기 생성 - 정규화, 인덱싱, 쿼리 최적화, 트랜잭션 |

## Gotchas (실패 포인트)

- N+1 쿼리: ORM에서 related 객체를 루프 안에서 개별 조회
- Index 없는 컬럼으로 WHERE 조건 — 대용량 시 성능 급락
- 트랜잭션 미사용 시 일부 성공/일부 실패 상태 발생 가능
- NULL과 빈 문자열 혼용 — 의미 모호성 발생
