'''
25개 구 손실 경향성을 한 그래프에 그릴때 오류 발생
ValueError: cannot reshape array of size 0 into shape (0,newaxis,1)
<Figure size 1200x600 with 0 Axes>
'''

from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
import matplotlib.pyplot as plt

# 데이터 로드 및 전처리 함수
def load_and_preprocess_data(file_path, county_name):
    data = pd.read_csv(file_path)
    data['date'] = pd.to_datetime(data['date'])
    data = data[data['county name'] == county_name]  # 구 이름 필터링
    data = data.sort_values('date').reset_index(drop=True)
    
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data['number of cold case'].values.reshape(-1, 1))
    return scaled_data, scaler, data['date']

# 시퀀스 생성 함수 (특정 날짜까지의 데이터를 사용해 예측)
def create_dataset(data, date_data, target_date, time_step=1):
    X, y = [], []
    
    # target_date까지의 데이터를 기준으로 시퀀스 생성
    for i in range(len(data)):
        if date_data[i] == target_date:
            a = data[:i + 1, 0]  # target_date까지의 데이터를 시퀀스로 사용
            X.append(a)
            break
    
    return np.array(X)

# 모델 생성 및 학습 함수
def create_and_train_model(X, y):
    X = [np.pad(x, (0, max(0, X.shape[1] - len(x))), 'constant', constant_values=0) for x in X]
    X = np.array(X).reshape(len(X), -1, 1)

    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mean_squared_error')
    
    history = model.fit(X, y, epochs=100, batch_size=32, verbose=0)  # verbose=0으로 학습 출력 생략
    return model, history

# 특정 날짜의 예측 수행 함수
def predict_for_date(model, target_date, scaled_data, date_data):
    # target_date까지의 데이터를 이용해 시퀀스 생성
    X = create_dataset(scaled_data, date_data, target_date)
    X = np.pad(X, (0, max(0, 1 - len(X[0]))), 'constant').reshape(1, -1, 1)  # LSTM 입력 형식으로 변환
    predicted_value = model.predict(X)
    return predicted_value

# 서버 시간을 기준으로 예측할 날짜 추출
def get_server_date():
    server_date = datetime.now().strftime('%Y-%m-%d')
    return pd.to_datetime(server_date)

# 메인 함수
def main():
    file_path = 'county_data_without_20_21_22.csv'  # 데이터 파일 경로
    counties = ['Jongno', 'Jung', 'Yongsan', 'Seongdong', 'Gwangjin', 'Dongdaemun', 'Jungnang', 'Seongbuk', 'Gangbuk', 'Dobong', 'Nowon', 'Eunpyeong', 'Seodaemun', 'Mapo', 'Yangcheon', 'Gangseo', 'Guro',  'Geumcheon', 'Yeongdeungpo', 'Dongjak', 'Gwanak', 'Seocho', 'Songpa', 'Gangnam', 'Gangdong']  # 구 리스트
    target_date = get_server_date()  # 서버 시간을 기준으로 날짜 설정

    plt.figure(figsize=(12, 6))  # 그래프 크기 설정
    for county_name in counties:
        # 1. 데이터 로드 및 전처리
        scaled_data, scaler, date_data = load_and_preprocess_data(file_path, county_name)

        # 2. 예측 모델 생성 및 학습
        # y 값을 생성하기 위해 시퀀스 생성
        y = scaled_data[1:]  # 예측할 값은 다음 시점의 값
        X = create_dataset(scaled_data, date_data, target_date)

        model, history = create_and_train_model(X, y)

        # 3. 손실 값 시각화
        plt.plot(history.history['loss'], label=f'Loss for {county_name}')

        # 4. 서버 시간에 맞는 날짜의 예측 수행
        predicted_value = predict_for_date(model, target_date, scaled_data, date_data)
        predicted_value = scaler.inverse_transform(predicted_value)
        
        print(f'Predicted Value for {target_date.date()} in {county_name}: {predicted_value[0][0]}')

    # 그래프 제목 및 레이블 설정
    plt.title('Loss for Each County')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend(loc='upper right')  # 범례 위치 조정
    plt.grid()  # 격자 추가
    plt.show()

# 메인 함수 실행
if __name__ == "__main__":
    main()
