import os
from dotenv import load_dotenv

import mysql.connector
from mysql.connector import Error
from src.database.schema import DBSchema

load_dotenv()

class DBManager:
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME'),
        }
        self.connection = None
        self.cursor = None

    def connect(self):
        """DB 연결"""
        try:
            # database 없이 먼저 연결
            connect_config = {k: v for k, v in self.config.items() if k != 'database'}
            self.connection = mysql.connector.connect(**connect_config)
            self.cursor = self.connection.cursor()

            # 없으면 DB 생성
            db_name = self.config['database']
            self.cursor.execute(f'CREATE DATABASE IF NOT EXISTS {db_name}')
            self.cursor.execute(f'USE {db_name}')

            print(f'[DB] DB 연결 성공 ✅')
            return True
            
        except Error as e:
            print(f'[DB] DB 연결 실패 ❌: {e}')
            return False

    def create_tables(self):
        """테이블 생성"""
        try:
            tables = DBSchema.get_all_tables()
            table_names = DBSchema.get_table_names()
            
            for table in tables:
                self.cursor.execute(table)

            self.connection.commit()
            print(f'[DB] 테이블 생성 성공 ✅: {", ".join(table_names)}')
            return True

        except Error as e:
            print(f'[DB] 테이블 생성 실패 ❌: {e}')
            self.connection.rollback()
            return False
        
    def drop_all_tables(self):
        """모든 테이블 삭제"""
        try:
            # 외래키 제약 조건 무시
            self.cursor.execute('SET FOREIGN_KEY_CHECKS = 0')

            table_names = DBSchema.get_table_names()

            for table_name in reversed(table_names):
                self.cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
                print(f'[DB] - {table_name} 삭제')

            # 외래키 제약 조건 복구
            self.cursor.execute('SET FOREIGN_KEY_CHECKS = 1')
            self.connection.commit()
            
            print(f'[DB] 전체 테이블 삭제 완료 ✅')
            return True

        except Error as e:
            print(f'[DB] 테이블 삭제 실패 ❌: {e}')
            return False

    def execute(self, query, values=None):
        """
        쿼리 실행 (INSERT, UPDATE, DELETE)

        Args:
            query: SQL 쿼리문
            values: 쿼리 파라미터
        
        Returns:
            bool: 성공 여부
        """
        try:
            if values:
                self.cursor.execute(query, values)
            else:
                self.cursor.execute(query)
            return True

        except Error as e:
            print(f'[DB] 쿼리 실행 실패 ❌: {e}')
            return False

    def commit(self):
        """트랜젝션 커밋"""
        try:
            self.connection.commit()
            print(f'[DB] 트랜젝션 커밋 완료 ✅')
            return True

        except Error as e:
            print(f'[DB] 트랜젝션 커밋 실패 ❌: {e}')
            return False
    
    def rollback(self):
        """트랜젝션 롤백"""
        try:
            self.connection.rollback()
            print(f'[DB] 트랜젝션 롤백 완료 ✅')
            return True
        except Error as e:
            print(f'[DB] 트랜젝션 롤백 실패 ❌: {e}')
            return False
        
    def close(self):
        """DB 연결 종료"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
        print(f'[DB] DB 연결 종료 ✅')
        return True

    def get_connection(self):
        """DB 연결 반환"""
        return self.connection
    
    def get_cursor(self):
        """DB 커서 반환"""
        return self.cursor
