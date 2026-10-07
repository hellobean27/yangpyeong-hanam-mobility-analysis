# 데이터 설명

이 디렉터리에는 공모전 보고서 재현에 필요한 **집계 입력값**만 포함합니다.

| 파일 | 내용 | 기간 |
|---|---|---|
| origin_totals.csv | 양평군 12개 읍·면 → 하남시 이동량 | 2026-06 |
| key_od.csv | 현재 수치가 확보된 주요 OD | 2026-06 |
| purpose_totals.csv | 이동목적별 집계 | 2026-06 |
| mode_inputs.csv | 차량·대중교통·기타 이동 및 거리·시간·차량수단 이용 인·km | 2026-08-24~30 |
| transit_supply.csv | 대표 버스 노선 평일 운행횟수 | 2026-10 확인 |
| equity_inputs.csv | 읍·면 인구 및 주요 고정거점 보유 여부 | 2026-08 / 검증본 |
| service_scenario.csv | 8-8 현행 시간표와 2시간 간격 실증 시나리오 | 현행 + 분석 시나리오 |

6월과 8월 자료는 서로 다른 기간이므로 동일한 개별 이동 단위로 결합하지 않습니다.

## 단위 수정

`CNT × MOVE_DIST`로 계산한 1,499,543은 자동차 **대수**에 대한 vehicle-km가 아니라
차량 수단을 이용한 추정 이동인구에 거리를 곱한 **person-km(인·km)** 로 관리합니다.

## 원자료

- 서울 데이터 허브 수도권 생활이동: https://data.seoul.go.kr/bsp/wgs/dataView/data300View/20062.do
- 수도권 생활이동 출도착 행정동별 수단 데이터: https://data.seoul.go.kr/dataList/OA-22657/F/1/datasetView.do
- 양평군청 시내버스: https://www.yp21.go.kr/www/contents.do?key=1500
- 탄소 원단위 산정근거: 한국환경공단 지자체 온실가스 감축사업별 감축원단위 적용 가이드라인(2024.10)
