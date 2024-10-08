# 라이브러리 호출
import pandas as pd

# 시군구 이름(한글 -> 영어) 변환 딕셔너리 생성
district_name_map = {
    '종로구': 'Jongno', '중구': 'Jung', '용산구': 'Yongsan', '성동구': 'Seongdong',
    '광진구': 'Gwangjin', '동대문구': 'Dongdaemun', '중랑구': 'Jungnang', 
    '성북구': 'Seongbuk','강북구': 'Gangbuk', '도봉구': 'Dobong', '노원구': 'Nowon', 
    '은평구': 'Eunpyeong','서대문구': 'Seodaemun', '마포구': 'Mapo', 
    '양천구': 'Yangcheon', '강서구': 'Gangseo','구로구': 'Guro', '금천구': 'Geumcheon', 
    '영등포구': 'Yeongdeungpo', '동작구': 'Dongjak','관악구': 'Gwanak', 
    '서초구': 'Seocho', '강남구': 'Gangnam', '송파구': 'Songpa', '강동구': 'Gangdong'
}

# 데이터 읽어오기
city_county_code = pd.read_csv('시군구 코드.csv', encoding='cp949')
info_before23 = pd.read_csv('진료정보_감기_시군구_14-23_상반기.csv', encoding='cp949')
info_after23 = pd.read_csv('진료정보_감기_시군구_23_하반기.csv', encoding='cp949')

# 데이터 합치기
info_combined = pd.concat([info_before23, info_after23], ignore_index=True)

# 서울시 데이터 추출 (시군구지역코드가 11로 시작하는 데이터)
Seoul_cold = info_combined[info_combined['시군구지역코드'].astype(str).str.startswith('11')]

# 날짜 열을 datetime 형식으로 변환
Seoul_cold['날짜'] = pd.to_datetime(Seoul_cold['날짜'], format='%Y-%m-%d')

# 날짜를 기준으로 오름차순 정렬
Seoul_cold_sorted = Seoul_cold.sort_values(by='날짜')

# 시군구 코드와 이름을 매핑하는 딕셔너리 생성 (영어 이름을 사용)
city_county_code['시군구명_영문'] = city_county_code['시군구명'].map(district_name_map)
code_to_name_eng = dict(zip(city_county_code['시군구지역코드'], city_county_code['시군구명_영문']))

# 시군구 지역코드를 영어로 변환된 이름으로 맵핑
Seoul_cold_sorted['시군구명_영문'] = Seoul_cold_sorted['시군구지역코드'].map(code_to_name_eng)

# 행정구명(영문)으로 검색하여 데이터프레임을 필터링하는 함수 생성
def get_district_data_eng(district_name_eng):
    # 해당 행정구 이름에 대응하는 시군구 코드를 찾아서 필터링
    district_code = [code for code, name in code_to_name_eng.items() if name == district_name_eng]
    if district_code:
        return Seoul_cold_sorted[Seoul_cold_sorted['시군구지역코드'] == district_code[0]]
    else:
        return pd.DataFrame()  # 해당 행정구가 없을 경우 빈 데이터프레임 반환

# 모든 행정구의 데이터를 하나로 합치는 데이터프레임 생성
all_districts_data = pd.concat([get_district_data_eng(district_name) for district_name in district_name_map.values()], ignore_index=True)

# 최종 데이터프레임 출력 확인
# print(all_districts_data.head())

# 각 행정구 데이터를 하나로 합친 데이터프레임을 CSV로 저장
all_districts_data.to_csv('all_county_data.csv', index=False, encoding='cp949')

# 2020년, 2021년, 2022년 데이터를 제외한 데이터프레임 생성 및 CSV 저장
data_without_2020_2021_2022 = all_districts_data[~all_districts_data['날짜'].dt.year.isin([2020, 2021, 2022])]
data_without_2020_2021_2022.to_csv('county_data_without_20_21_22.csv', index=False, encoding='cp949')

# 2014년, 2020년, 2021년, 2022년 데이터를 제외한 데이터프레임 생성 및 CSV 저장
data_without_2014_2020_2021_2022 = all_districts_data[~all_districts_data['날짜'].dt.year.isin([2014, 2020, 2021, 2022])]
data_without_2014_2020_2021_2022.to_csv('county_data_without_14_20_21_22.csv', index=False, encoding='cp949')