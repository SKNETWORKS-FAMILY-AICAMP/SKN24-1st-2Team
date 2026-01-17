# DB 사용 가이드

## 초기 설정
### 1. requirements 파일 설치
```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정
프로젝트 루트 디렉토리에 `.env` 파일을 생성합니다.
내용은 `.env.example`을 복사하여 본인 환경에 맞게 입력합니다.

**주의**: `.env`파일은 절대 git에 커밋하면 안됩니다.

---

## DB 초기화
### 최초 1회 실행
```bash
python -m src.scripts.init_database
```

### DB 재초기화 (모든 데이터 삭제)
```bash
python -m src.scripts.init_database --reset
```

**주의**: `--reset` 옵션은 모든 테이블과 데이터를 삭제하고 재생성합니다.

---

## 데이터 삽입 방법

### DB Manager 직접 사용
```python
import mysql.connector
from database.db_manager import DBManager

db = DBManager()

try:
    db.connect()
    
    # 2. 데이터 삽입
    sql_insert = 'INSERT INTO fuel_tbl (fuel_type, fuel_cost) VALUES (%s, %s)'
    
    for item in data:
        values = (item['type'], item['cost'])
        db.execute(sql_insert, values)

    db.commit()

except Exception as e:
    db.rollback()

finally:
    db.close()
```
