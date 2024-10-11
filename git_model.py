'''1. 달 단위로 끊어서 학습 시도
2. test, train, validation 제대로 끊겼는지 확인
3. 2023.10~12 데이터는 이전 5년치 일일 확진자 수 평균값으로 채운 후 학습(데이터 전처리)
'''

'''
2023-10~12 데이터 채우는 코드

import pandas as pd

# 데이터 로드
file_path = 'county_data_without_14_20_21_22.csv'  # 데이터 파일 경로
data = pd.read_csv(file_path)

# 'date' 열을 datetime 형식으로 변환
data['date'] = pd.to_datetime(data['date'])

# 2015년부터 2022년까지의 데이터 필터링
filtered_data = data[(data['date'] >= '2015-01-01') & (data['date'] <= '2022-12-31')]

# 각 구별로 연도와 날짜별 평균 계산
filtered_data['year'] = filtered_data['date'].dt.year
filtered_data['day'] = filtered_data['date'].dt.dayofyear  # 일 년 중 일수
daily_avg = filtered_data.groupby(['county name', 'day'])['number of cold case'].mean().reset_index()

# 2023년 10월부터 12월까지의 일수 범위 생성
months = ['October', 'November', 'December']
days_in_month = {
    'October': 31,
    'November': 30,
    'December': 31
}

# 2023년의 날짜에 대한 평균 값 채우기
new_data = []
for county in daily_avg['county name'].unique():
    for month in months:
        for day in range(1, days_in_month[month] + 1):
            # 해당 월과 일에 대한 날짜 계산
            date = pd.Timestamp(f'2023-{month[0:3]}-{day}')
            day_of_year = date.dayofyear
            
            # 해당 구의 평균 감기 환자 수 가져오기
            if not daily_avg[(daily_avg['county name'] == county) & (daily_avg['day'] == day_of_year)].empty:
                avg_cases = daily_avg[(daily_avg['county name'] == county) & (daily_avg['day'] == day_of_year)]['number of cold case'].values[0]
            else:
                avg_cases = 0  # 해당 데이터가 없는 경우 0으로 설정
            
            new_data.append({'date': date, 'number of cold case': avg_cases, 'county name': county})

# 새로운 데이터프레임 생성
new_df = pd.DataFrame(new_data)

# 원본 데이터와 새로운 데이터프레임을 합칩니다.
data = pd.concat([data, new_df], ignore_index=True)

# 결과 확인
print(data)


# CSV 파일 경로
output_file_path = 'filled_county_data.csv'

# DataFrame을 CSV 파일로 저장
data.to_csv(output_file_path, index=False)
'''
