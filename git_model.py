'''1. 달 단위로 끊어서 학습 시도
2. test, train, validation 제대로 끊겼는지 확인
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

#3-5 sequential 2015~2018 학습 데이터, 2019 검증 데이터, 2023 테스트 데이터

from datetime import timedelta
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from keras.callbacks import EarlyStopping

# 데이터 로드 및 전처리 함수
def load_and_preprocess_data(file_path, county_name):
    data = pd.read_csv(file_path)
    data['date'] = pd.to_datetime(data['date'])
    data = data[data['county name'] == county_name]  # 구 이름 필터링
    data = data.sort_values('date').reset_index(drop=True)
    
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data['number of cold case'].values.reshape(-1, 1))
    return scaled_data, scaler, data['date']

# 시퀀스 생성 함수 (모든 데이터를 사용)
def create_dataset(data, time_step=60):
    X, y = [], []
    for i in range(len(data) - time_step):
        X.append(data[i:i + time_step, 0])
        y.append(data[i + time_step, 0])
    return np.array(X), np.array(y)

# 연도별로 데이터셋을 나누는 함수
def split_dataset_by_year(scaled_data, date_data, time_step=60):
    # 데이터프레임에 연도를 추가
    date_data = pd.to_datetime(date_data)
    year_data = date_data.dt.year

    # 연도별로 데이터 나누기
    train_mask = (year_data >= 2015) & (year_data <= 2018)
    val_mask = (year_data == 2019)
    test_mask = (year_data == 2023)

    X_train, y_train = create_dataset(scaled_data[train_mask], time_step)
    X_val, y_val = create_dataset(scaled_data[val_mask], time_step)
    X_test, y_test = create_dataset(scaled_data[test_mask], time_step)
    
    return X_train, y_train, X_val, y_val, X_test, y_test

# 모델 생성 및 학습 함수 (EarlyStopping 추가)
def create_and_train_model(X_train, y_train, X_val, y_val):
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])
    
    # EarlyStopping 콜백 추가 (검증 손실이 개선되지 않으면 10 에포크 이후에 학습 중단)
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    
    history = model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=100, batch_size=32, verbose=0, callbacks=[early_stopping])
    return model, history

# 메인 함수
def main():
    file_path = 'filled_county_data.csv'  # 데이터 파일 경로
    target_date = pd.to_datetime('2024-10-25')  # 예측할 목표 날짜
    counties = ['Jongno', 'Jung', 'Yongsan', 'Seongdong', 'Gwangjin', 'Dongdaemun', 'Jungnang', 'Seongbuk', 'Gangbuk', 'Dobong', 'Nowon', 'Eunpyeong', 'Seodaemun', 'Mapo', 'Yangcheon', 'Gangseo', 'Guro',  'Geumcheon', 'Yeongdeungpo', 'Dongjak', 'Gwanak', 'Seocho', 'Songpa', 'Gangnam', 'Gangdong']

    last_model = None  # 마지막 모델 저장

    loss_fig, ax_loss = plt.subplots(figsize=(12, 6))  # 손실 그래프
    mae_fig, ax_mae = plt.subplots(figsize=(12, 6))  # MAE 그래프
    val_loss_fig, ax_val_loss = plt.subplots(figsize=(12, 6))  # Validation 손실 그래프

    for county_name in counties:
        scaled_data, scaler, date_data = load_and_preprocess_data(file_path, county_name)

        # 연도 기준으로 데이터 분할
        X_train, y_train, X_val, y_val, X_test, y_test = split_dataset_by_year(scaled_data, date_data)
        
        model, history = create_and_train_model(X_train, y_train, X_val, y_val)

        # 구별로 모델 저장
        model.save(f'{county_name}_lstm_model.h5')  # 모델을 각 구 이름으로 저장

        last_model = model  # 마지막 학습된 모델을 전체 모델로 사용

        # 목표 날짜까지 예측 수행
        last_sequence = scaled_data[-len(X_test):]  # 테스트 셋 마지막 시퀀스 가져오기
        predicted_values = predict_future(model, last_sequence, len(X_test), scaler)

        print(f'Predicted Value for {target_date.date()} in {county_name}: {predicted_values[-1][0]}')

        # 손실 그래프
        ax_loss.plot(history.history['loss'], label=f'{county_name} Loss')

        # 검증 손실 그래프
        ax_val_loss.plot(history.history['val_loss'], label=f'{county_name} Validation Loss')

        # MAE 그래프
        ax_mae.plot(history.history['mae'], label=f'{county_name} MAE')

    # 그래프 제목 및 레이블 설정 (손실)
    ax_loss.set_title('Loss for Each County')
    ax_loss.set_xlabel('Epochs')
    ax_loss.set_ylabel('Loss')
    ax_loss.legend(loc='upper right')
    ax_loss.grid(True)

    # 검증 손실 그래프 제목 및 레이블 설정
    ax_val_loss.set_title('Validation Loss for Each County')
    ax_val_loss.set_xlabel('Epochs')
    ax_val_loss.set_ylabel('Validation Loss')
    ax_val_loss.legend(loc='upper right')
    ax_val_loss.grid(True)

    # 그래프 제목 및 레이블 설정 (MAE)
    ax_mae.set_title('MAE for Each County')
    ax_mae.set_xlabel('Epochs')
    ax_mae.set_ylabel('Mean Absolute Error')
    ax_mae.legend(loc='upper right')
    ax_mae.grid(True)

    plt.show()

    # 전체 마지막 모델 저장
    last_model.save('all_counties_lstm_model.h5')

    # 마지막 모델 평가 및 정확도 출력 (퍼센티지로)
    accuracy = evaluate_model(last_model, X_test, y_test, scaler)
    print(f'Test Accuracy for last model: {accuracy:.2f}%')

# 메인 함수 실행
if __name__ == "__main__":
    main()
