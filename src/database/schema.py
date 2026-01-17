"""
ERD 기반 데이터베이스 스키마 정의
"""

class DBSchema:
    # 1. 연료 테이블
    FUEL_TABLE = """
    CREATE TABLE IF NOT EXISTS fuel_tbl (
        fuel_type VARCHAR(20) PRIMARY KEY,                   -- 연료 이름(PK)
        fuel_cost DECIMAL(10, 2) NOT NULL DEFAULT 0          -- 평균 연료 비용
    );
    """
    
    # 2. 지역 테이블(전국팔도)
    REGION_TABLE = """
    CREATE TABLE IF NOT EXISTS region_tbl (
        region VARCHAR(10) PRIMARY KEY,                      -- 지역 이름(PK)
        charger_cnt INT NOT NULL                             -- 충전소 개수
    );
    """
    
    # 3. 지역별 연료별 등록 대수
    CNT_TABLE = """
    CREATE TABLE IF NOT EXISTS cnt_tbl (
        date INT PRIMARY KEY,                                -- 년월(PK)
        fuel_type VARCHAR(20) NOT NULL,                      -- 연료 이름(FK)
        region VARCHAR(10) NOT NULL,                         -- 지역 이름(FK)
        cnt INT NOT NULL,                                    -- 등록 대수
        
        FOREIGN KEY (fuel_type) REFERENCES fuel_tbl(fuel_type)
            ON UPDATE CASCADE,
        FOREIGN KEY (region) REFERENCES region_tbl(region)
            ON UPDATE CASCADE
    );
    """
    
    # 4. 차량 정보 테이블
    CAR_INFO_TABLE = """
    CREATE TABLE IF NOT EXISTS car_info_tbl (
        car_id INT PRIMARY KEY AUTO_INCREMENT,               -- 차량 코드(PK)
        fuel_type VARCHAR(20) NOT NULL,                      -- 연료(FK)
        name VARCHAR(50) NOT NULL,                           -- 차량 모델명
        maker VARCHAR(10) NOT NULL,                          -- 제조사
        size VARCHAR(10),                                    -- 차량 등급
        capacity DECIMAL(10, 1) NOT NULL,                    -- 적재량
        h_power INT NOT NULL,                                -- 최대 마력
        max_fuel DECIMAL(10, 1) NOT NULL,                    -- 연료 용량
        cx_efc DECIMAL(10, 1),                               -- 복합 연비
        ct_efc DECIMAL(10, 1),                               -- 도심 연비
        hw_efc DECIMAL(10, 1),                               -- 고속도로 연비
        max_dist INT NOT NULL,                               -- 최대 주행거리
        price INT NOT NULL,                                  -- 가격
        image VARCHAR(255),                                  -- 이미지 경로

        FOREIGN KEY (fuel_type) REFERENCES fuel_tbl(fuel_type)
            ON UPDATE CASCADE
    );
    """

    # 5. FAQ 카테고리 테이블
    FAQ_CATEGORY_TABLE = """
    CREATE TABLE IF NOT EXISTS faq_category_tbl (
        category_code INT PRIMARY KEY AUTO_INCREMENT,        -- 카테고리 코드(PK)
        category_name VARCHAR(10) NOT NULL,                  -- 카테고리명
    );
    """

    # 6. FAQ 테이블
    FAQ_TABLE = """
    CREATE TABLE IF NOT EXISTS faq_tbl (
        faq_id INT PRIMARY KEY AUTO_INCREMENT,               -- FAQ 코드(PK)
        category_code INT NOT NULL,                          -- 카테고리 코드(FK)
        question VARCHAR(255) NOT NULL,                      -- 질문
        answer VARCHAR(255) NOT NULL,                        -- 답변
        source_url VARCHAR(255) NOT NULL,                    -- 출처 URL
        related_fuel_type VARCHAR(20) NOT NULL,              -- 관련 연료 유형

        FOREIGN KEY (category_code) REFERENCES faq_category_tbl(category_code)
            ON UPDATE CASCADE
    );
    """

    @classmethod
    def get_all_tables(cls):
        """테이블 생성 쿼리 반환"""
        return [
            cls.FUEL_TABLE,
            cls.REGION_TABLE,
            cls.CAR_INFO_TABLE,
            cls.CNT_TABLE,
            cls.FAQ_CATEGORY_TABLE,
            cls.FAQ_TABLE,
        ]

    @classmethod
    def get_table_names(cls):
        return ['fuel_tbl', 'region_tbl', 'car_info_tbl', 'cnt_tbl', 'faq_category_tbl', 'faq_tbl']