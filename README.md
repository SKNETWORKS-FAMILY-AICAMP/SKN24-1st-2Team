# SK네트웍스 Family AI 캠프 24기 1차 프로젝트
## 🏠팀 소개
### 👍DumPs-Up
|고아라|권민세|김현수|문성준|임정희|
|----|---|---|---|---|
| <img src="https://github.com/user-attachments/assets/d9c0b5d5-7df8-4d39-a31e-d16b036e9e8e" width="160"> | <img src="https://github.com/user-attachments/assets/72bad72a-a349-4d73-bc37-6b4b7534857d" width="160"> | <img src="https://github.com/user-attachments/assets/73d6a835-154a-46a9-8689-954402a433ca" width="160"> | <img src="https://github.com/user-attachments/assets/53ef684e-1826-4383-b7ad-b45866c38758" width="160"> | <img src="https://github.com/user-attachments/assets/df516a42-0c80-450a-b972-64e75778e420" width="160"> |
| [Akoh-0909](https://github.com/Akoh-0909) | [KweonMinSe0109](https://github.com/KweonMinSe0109) | [BarryKim34](https://github.com/BarryKim34) | [dal-sj](https://github.com/dal-sj) | [bigmooon](https://github.com/bigmooon) |

<br/>
<br/>

# 🚛 DumPs-Up: 화물차주를 위한 맞춤형 의사결정 지원 플랫폼

> **"화물차 시장의 새로운 기준을 세우고, 차주님들의 합리적인 선택을 응원합니다."**

---

## 1. 프로젝트 개요

### 1.1 프로젝트 명칭 및 의미
- **명칭**: **DumPs-Up** (덤프스업)
- **의미**: 화물차(**Dump**) 시장의 새로운 기준을 제시하고, 차주들의 합리적인 선택을 응원(**Thumbs Up**)한다는 가치를 담고 있습니다.

### 1.2 프로젝트 정의
노후화 및 사고로 차량 교체 기로에 선 화물 운송 종사자를 위해, 내연기관과 전기차의 최신 시장 데이터를 대조하여 제시하는 **'사용자 주도형 의사결정 지원 플랫폼'**입니다.

### 1.3 서비스 지향점
- **객관적 사실 고지**: 특정 유종이나 모델을 정답으로 강요하지 않으며, 급변하는 정보를 시각화하여 전달합니다.
- **자기결정권 존중**: 복잡한 운송 환경의 변수를 가장 잘 아는 주체는 '차주'라는 전제하에, 판단의 근거가 되는 양질의 정보를 스펙트럼 형태로 제공하여 정보 비대칭을 해소합니다.

---

## 2. 프로젝트 배경 및 필요성

### 2.1 운송업 종사자의 정보 취약성 및 디지털 격차
국내 화물 운송 종사자의 평균 연령대는 40~60대로, 타 산업군 대비 디지털 정보 접근성이 상대적으로 낮습니다. 급변하는 정책 공고와 보조금 신청 시스템에서 소외될 우려가 큽니다.
- **관련 통계**: 성인 8.2%는 일상적인 디지털 기기 조작에 어려움을 겪고 있으며, 40~50대 이상에서 그 비중이 높게 나타납니다.
  
    <img width="1311" height="681" alt="chart" src="https://github.com/user-attachments/assets/3d0bca51-7d10-4651-a90d-3b29b8b03d79" />

  - [성인 8.2%, 일상에서 기본적 디지털기기 조작도 어려워 (연합뉴스)](https://www.yna.co.kr/view/AKR20250819075600530)
  - [제1차 성인디지털문해능력조사 결과 발표 (교육부)](https://www.moe.go.kr/boardCnts/viewRenew.do?boardID=294&boardSeq=103949&lev=0&searchType=null&statusYN=W&page=1&s=moe&m=020402&opType=N)

### 2.2 시장 환경의 급변과 정보 통합의 필요성
내연기관 라인업 축소와 환경 규제 강화로 인해 신차 시장은 LPG와 EV(전기) 모델로 양분되었습니다. 하지만 관련 정보가 각 기관에 파편화되어 있어 생업에 바쁜 종사자들이 직접 비교하기엔 물리적 시간이 부족합니다.
- **시장 동향**: [2024 화물운송시장 동향 연간보고서 (한국교통연구원)](https://www.koti.re.kr)

### 2.3 인프라에 대한 막연한 불안감 해소
전기 화물차 초기 모델의 성능과 인프라에 대한 과거의 부정적 인식이 현재의 기술 발전을 가리고 있습니다. 객관적인 인프라 데이터 제시를 통해 이러한 오해를 해소할 필요가 있습니다.
- **관련 기사**: [충전소 불청객 된 ‘포터·EV’···전기 화물차 보급 문제 없나 (시사저널e)](https://www.sisajournal-e.com/news/articleView.html?idxno=295570)
- **인프라 확충**: [고속도로 휴게소 전기 상용차 충전소 운영 확대 추진 (에너지플랫폼뉴스)](https://www.e-platform.net/news/articleView.html?idxno=88123)

---

## 3. 주요 기능 및 데이터 구성

사용자가 단계적으로 정보를 수용할 수 있도록 총 3개 페이지로 데이터를 구성하였습니다.

### 📊 Page 1. 거시적 관점: 시장 지표 및 인프라 현황
- **시장 트렌드**: 화물차 등록 현황 대비 전기화물차 점유율 추이 시각화.
- **충전 가용성**: 전국 전기충전소 인프라 구축 현황 지도 제공.
- **연료 효율성**: 디젤, LPG vs 전기 연료별 유지비 직관적 비교.

### 🚚 Page 2. 미시적 관점: 상세 제원 대조
- **대상 모델**: 시장 점유율이 높은 '포터', '봉고' 시리즈 집중 분석.
- **스펙 비교**: 출력, 적재 용량, 주행 거리 등 실질적 제원 일대일 대조.

### ❓ Page 3. 실무적 관점: 통합 FAQ
- **비용**: 2026년 개편 보조금 정책, 화물차 취등록세 정보.
- **행정**: 운수사업 허가 신청 서류 및 영업용 번호판 발급 절차 안내.
- **운행**: 충전 시간, 주행 시 단점, 배터리 수명 및 정비료 비교.

---

## 4. 프로젝트 목표

1. **정보 비대칭 해소**: 정보 습득 역량에 따라 경제적 혜택에서 차별받지 않도록, 누구나 이해하기 쉬운 직관적인 대시보드를 제공합니다.
2. **지속 가능한 운송 생태계 지원**: 화물차 차주들이 막연한 불안감 때문에 효율적인 선택을 포기하지 않도록 돕는 신뢰할 수 있는 가이드 역할을 수행합니다.

<br/>
<br/>

## ⚙️기술 스택
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white) ![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)  ![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white) ![Plotly](https://img.shields.io/badge/Plotly-23F16F?style=for-the-badge&logo=plotly&logoColor=white) ![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)

<br/>
<br/>

## 💻WBS

<img width="1705" height="862" alt="image" src="https://github.com/user-attachments/assets/b45dd1b2-1332-49a9-888c-b42689d08ce6" />

<br/>
<br/>

## 📄요구사항 명세서

| 섹션 | 요구사항 범주 | 주요 세부 사항 |
| :--- | :--- | :--- |
| **1. 서론** | 프로젝트 개요 | 한국의 차량 등록, 연료, 충전 데이터에 대한 통찰력 및 시각화를 제공하는 데이터 기반 애플리케이션. |
| **2. 데이터 수집** | 출처 및 방법 | - **차량 등록:** 국토교통부(Excel) Selenium 수집<br>- **FAQ:** 정적/동적 사이트 Selenium/BS4 수집<br>- **연료:** 오피넷, EV.or.kr Selenium 수집<br>- **지역:** 차지인포 Selenium 수집 |
| | 데이터 유형 | Excel(.xlsx), 구조화된 FAQ(질문/답변, URL), 수치형 연료 가격, 지역명 및 충전소 수. |
| **3. 데이터 처리** | 변환 | - **차량 등록:** 연/월 추출, '화물'/'계' 필터링, 8개도 매핑, 4개 연료 유형(디젤, LPG, 전기, 기타) 매핑<br>- **연료:** 평균 가격 계산 (디젤, LPG, 전기)<br>- **지역:** 문자열 숫자를 정수로 변환 |
| | 출력물 | 처리된 등록 차량 `.csv` 파일, DB 로드를 위한 `(fuel_type, avg_price)` 및 `(region, count)` 튜플 |
| **4. 데이터 저장** | DB 시스템 및 스키마 | **MySQL 사용.** 스키마: `fuel_tbl`, `region_tbl`, `cnt_tbl`, `car_info_tbl`, `faq_category_tbl`, `faq_tbl` (외래 키 지정 포함) |
| | 데이터베이스 관리 | Python `DBManager` 클래스를 통한 연결, 테이블 CRUD 및 DML 작업 수행 |
| **5. 데이터 로드** | ETL 프로세스 | 처리된 데이터를 MySQL에 로드. 각 기능별 `load_*.py` 스크립트 사용. 연료/지역 데이터는 `ON DUPLICATE KEY UPDATE` 적용 |
| **6. 데이터 서비스** | API/백엔드 로직 | - `registration_service.py`: 등록 대수 및 전년 대비 추이 계산<br>- `region_service.py`: 지역별 충전기 수 조회<br>- `fuel_service.py`: 연료 유형 및 비용 목록 조회 |
| **7. 프론트엔드 / UI** | 프레임워크 및 디자인 | **Streamlit** 기반 웹 앱. 어두운 테마 및 사용자 정의 CSS 적용. 반응형 디자인 구현 |
| | 내비게이션 | "통계 및 현황", "차량 비교", "FAQ"로 구성된 상단 내비게이션 바 |
| | 페이지 구성 | - **통계:** 대화형 버블 맵(충전소, 화물차 비중), 등록 추이 및 유지비 차트<br>- **비교:** 상업용 차량 모델 상세 사양 비교<br>- **FAQ:** 카테고리별 확장 가능한 Q&A |
| **8. 환경 설정** | 설정 관리 | - **환경 변수:** `.env` (`DB_HOST`, `USER`, `PASSWORD` 등)<br>- **앱 설정:** `config.py` (지도 좌표 등 고정값 저장) |
| **9. 기술 스택** | 핵심 기술 | Python, Streamlit, Pandas, NumPy, Selenium, BeautifulSoup, MySQL, Plotly, Pydeck, python-dotenv |
| **10. 배포 및 실행** | 설정 및 운영 | 필수 요소: Python, MySQL, ChromeDriver<br>순서: 의존성 설치 → `.env` 구성 → DB 초기화(`init_database.py`) → 데이터 로딩 → `streamlit run main.py` |
<br/>
<br/>

## 📋ERD
<img width="674" height="335" alt="ERD_논리" src="https://github.com/user-attachments/assets/af61aa86-60d4-4ce5-9670-9400d4aee345" />

<br/>
<br/>

<img width="703" height="378" alt="ERD_물리" src="https://github.com/user-attachments/assets/e251df61-16ca-457f-8a12-200a9ce473a2" />

<br/>
<br/>

## 📊수행결과(시연 페이지)

<img width="1524" height="840" alt="image" src="https://github.com/user-attachments/assets/a1b8c390-8fda-4b44-a66b-3445c9710bb9" />

<br/>
<br/>

<img width="3420" height="2214" alt="비교1" src="https://github.com/user-attachments/assets/7cf8abbd-1674-49a0-a50c-ee71fe9eba44" />
<img width="3420" height="2214" alt="비교2" src="https://github.com/user-attachments/assets/a52861a1-7584-4b47-8f74-b2fd7175b9cd" />

<br/>
<br/>

<img width="1917" height="903" alt="faq1" src="https://github.com/user-attachments/assets/5469c692-e32d-4a39-9cda-1a19c43ccc4e" />
<img width="1913" height="902" alt="faq2" src="https://github.com/user-attachments/assets/10c7cbc4-a05f-4f4f-97d5-5b42cfca7973" />

<br/>
<br/>

## 💭한 줄 회고

🐨고아라
```
기초 학습이 제대로 되어있지 않고  충분한 적응 기간 없이 팀프로젝트에 투입이 되다보니, 
어느 정도 기본기가 숙련된 팀원들과의 소통과 업무 응용방식, 숙련도차이에서 큰 격차를 느끼며, 교육과정과 실무에서 오는 괴리감으로 힘들었습니다. 
특히 세부가이드라인이나 논의가 부족한 상황에서 제로베이스인 제가  스스로 프로세스를 이해하고 설계하기엔 한계가 있었고, 
이 과정에서 팀 프로젝트에 충분히 기여하지 못한 채 소외되는 부분이 있었던 것 같아 아쉬움으로 남습니다.
이번 경험을 통해 실무 투입 전 기본개념의 확립과 협업을 위한 구체적인 커뮤니케이션의 중요성을 다시한번 깨닫게 되는 계기가 되었으며, 마지막까지 최선을 다한 팀원들에게 박수를 보냅니다. 
```
🦦권민세
```
팀원들 모두가 열정적으로 참여해 준 덕분에 Git을 활용한 협업을 자연스럽게 숙지할 수 있었습니다.
크롤링 과정에서는 어려웠던 부분들을 팀원들과의 의견 공유를 통해 잘 해결할 수 있었지만 추후에 더 숙달해야겠다고 생각했습니다.
db 연동 및 streamlit 활용부터 git을 통한 협업까지 배울 수 있었던 뜻깊은 경험이었습니다.
```
🐢김현수
```
처음 접한 Git으로 체계적인 협업과 효율적인 업무 분담을 경험했으며 , 데이터 수집 전 진행한 사전 ERD 설계 덕분에 크롤링과 DB 구축 과정의 시행착오를 획기적으로 줄일 수 있었습니다.
예기치 못한 건강 문제에도 끝까지 이끌어준 팀원들에게 감사의 말씀 전합니다.
```
🐈‍⬛문성준
```
파편화된 데이터를 한 곳에 모으는 것 자체는 성공적이었다고 생각하지만 안정적인 크롤링과 데이터 표준화에 어려움을 겪었고 아쉬움이 많이 남습니다.
아쉬움과 함께 협업과정에서의 데이터 파이프라인의 중요성을 깨닫게 되는 계기가 되었습니다.
또한, 제대로 된 git 컨벤션을 활용한 협업을 배워갈 수 있었으며,
이는 많은 도움과 아이디어, 방향성을 공유해준 팀원들의 덕분이었습니다.
```
🦙임정희
```
촉박한 일정으로 문서화를 생략하여 중복 논의가 발생하는 시행착오가 있었으나,
할 수 있는 일에 최선을 다하는 팀원들 덕분에 프로젝트를 마칠 수 있었습니다. 
이번 경험을 통해 기록과 공유가 협업 효율의 핵심임을 배웠습나다.
```
