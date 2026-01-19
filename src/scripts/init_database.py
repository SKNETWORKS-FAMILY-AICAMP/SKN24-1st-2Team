from src.database.db_manager import DBManager

def init_database(reset=False):
    """
    DB 초기화

    Args:
        reset (bool): 기존 테이블 삭제 여부
    """
    print('=' * 50)
    print('[DBSCRIPT] DB 초기화 시작')
    print('=' * 50)

    db = DBManager()

    # 1. 연결
    if not db.connect():
        return 

    # 2. reset=True인 경우 기존 테이블 삭제
    if reset:
        print('[DBSCRIPT] 기존 테이블 삭제')
        db.drop_all_tables()
    
    # 3. 테이블 생성
    print('[DBSCRIPT] 테이블 생성')
    db.create_tables()

    # 4. 테이블 확인
    print('[DBSCRIPT] 테이블 확인')
    verify_tables(db)

    # 5. DB 연결 종료
    print('\n' + '=' * 50)
    db.close()
    print('[DBSCRIPT] DB 초기화 완료 ✅')

def verify_tables(db):
    """생성된 테이블 확인"""
    cursor = db.get_cursor()
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()

    print(f'[DBSCRIPT] 생성된 테이블: {tables}')

if __name__ == '__main__':
    import sys

    reset = '--reset' in sys.argv

    if reset:
        confirm = input('기존 테이블을 삭제하고 초기화하시겠습니까? (y/n): ')
        if confirm.lower() != 'y':
            print('[DBSCRIPT] 초기화 취소')
            sys.exit(0)

    init_database(reset=reset)