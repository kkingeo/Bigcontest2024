import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense

data = pd.read_csv('county_data_without_20_21_22.csv', encoding='cp949', header=None, names=['date', 'number of cold case' ,'county name'])
data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d', errors='coerce')
data.set_index('date', inplace=True)

district_names=data['county name'].unique()

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense

# 데이터 불러오기
data = pd.read_csv('county_data_without_20_21_22.csv', encoding='cp949')

# 날짜를 인덱스로 설정
data['날짜'] = pd.to_datetime(data['날짜'])
data.set_index('날짜', inplace=True)

# 특정 시군구에 대한 데이터만 선택 (예: 'Jongno')
district_data = data[data['시군구명_영문'] == 'Jongno']

# '발생건수(건)' 열만 사용하여 정규화
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(district_data['발생건수(건)'].values.reshape(-1, 1))

# 시계열 윈도우 생성 함수
def create_dataset(dataset, look_back=1):
    X, Y = [], []
    for i in range(len(dataset) - look_back - 1):
        a = dataset[i:(i + look_back), 0]
        X.append(a)
        Y.append(dataset[i + look_back, 0])
    return np.array(X), np.array(Y)

# 30일 간의 데이터를 기반으로 예측 (look_back=30)
look_back = 30
X, Y = create_dataset(scaled_data, look_back)

# 입력 데이터를 LSTM 모델에 맞게 3차원 배열로 변환
X = np.reshape(X, (X.shape[0], X.shape[1], 1))

# LSTM 모델 생성
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(look_back, 1)))
model.add(LSTM(50))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mean_squared_error')

# 모델 학습
model.fit(X, Y, epochs=100, batch_size=32)

# 예측 (가장 최근의 데이터를 사용해 미래 예측)
predicted_cases = model.predict(X[-1].reshape(1, look_back, 1))
predicted_cases = scaler.inverse_transform(predicted_cases)

print("예측된 감기 확진자 수:", predicted_cases)
