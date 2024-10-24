import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import RobustScaler
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error

# 데이터 로드 및 전처리 함수
def load_and_preprocess_data(file_path, county_name):
    data = pd.read_csv(file_path)
    data['date'] = pd.to_datetime(data['date'])
    
    # 지정된 카운티 이름으로 필터링
    data = data[data['county name'] == county_name]
    data = data.sort_values('date').reset_index(drop=True)

    # 결측치 처리: 중앙값으로 대체
    data['number of cold case'].fillna(data['number of cold case'].median(), inplace=True)

    # 이상치 클리핑 처리
    lower_bound = data['number of cold case'].quantile(0.01)
    upper_bound = data['number of cold case'].quantile(0.99)
    data['number of cold case'] = np.clip(data['number of cold case'], lower_bound, upper_bound)

    # RobustScaler로 데이터 정규화
    scaler = RobustScaler()
    scaled_data = scaler.fit_transform(data['number of cold case'].values.reshape(-1, 1))

    # 날짜 관련 변수 추가
    data['year'] = data['date'].dt.year
    data['month'] = data['date'].dt.month
    data['day'] = data['date'].dt.day
    data['weekday'] = data['date'].dt.dayofweek

    # 추가된 날짜 변수를 scaled_data에 결합
    date_features = data[['year', 'month', 'day', 'weekday']].values
    scaled_data = np.concatenate([scaled_data, date_features], axis=1)

    return scaled_data, scaler, data['date'], data

# 시퀀스 생성 함수
def create_dataset(data, time_step=90):
    X, y = [], []
    data_len = len(data)
    for i in range(data_len - time_step):
        X.append(data[i:i + time_step])  # (timesteps, features)
        y.append(data[i + time_step, 0])  # number of cold cases만 y로 사용
    return np.array(X), np.array(y)

# LSTM 모델 정의
class LSTMModel(nn.Module):
    def __init__(self, hidden_size, num_layers):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size=5, hidden_size=hidden_size, num_layers=num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out

# 학습 및 검증 함수
def train_model(X_train, y_train, X_val, y_val, epochs=200, lr=0.001, hidden_size=256, num_layers=8):
    model = LSTMModel(hidden_size, num_layers)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    X_train = torch.tensor(X_train, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.float32)

    if len(X_val) > 0:
        X_val = torch.tensor(X_val, dtype=torch.float32)
        y_val = torch.tensor(y_val, dtype=torch.float32)

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs, y_train.unsqueeze(1))
        loss.backward()
        optimizer.step()

        if epoch % 10 == 0:
            print(f'Epoch {epoch}, Loss: {loss.item()}')

    return model

# 예측 함수
def predict(model, X_test):
    model.eval()
    X_test = torch.tensor(X_test, dtype=torch.float32)
    with torch.no_grad():
        predictions = model(X_test)
    return predictions.numpy()

# 데이터셋을 연도별로 나누는 함수
def split_dataset_by_year(scaled_data, date_data, time_step=90):
    date_data = pd.to_datetime(date_data)
    year_data = date_data.dt.year

    train_mask = (year_data >= 2015) & (year_data <= 2017)
    val_mask = (year_data == 2018)
    test_mask = (year_data == 2019)

    # 데이터 나누기
    train_data = scaled_data[train_mask]
    val_data = scaled_data[val_mask]
    test_data = scaled_data[test_mask]

    # 시퀀스 생성
    X_train, y_train = create_dataset(train_data, time_step)
    X_val, y_val = create_dataset(val_data, time_step)
    X_test, y_test = create_dataset(test_data, time_step)

    return X_train, y_train, X_val, y_val, X_test, y_test

# 메인 함수
def main():
    file_path = 'filled_county_data.csv'
    counties = ['Jongno', 'Jung', 'Yongsan', 'Seongdong', 'Gwangjin', 'Dongdaemun', 'Jungnang', 'Seongbuk', 'Gangbuk', 
                'Dobong', 'Nowon', 'Eunpyeong', 'Seodaemun', 'Mapo', 'Yangcheon', 'Gangseo', 'Guro', 'Geumcheon', 
                'Yeongdeungpo', 'Dongjak', 'Gwanak', 'Seocho', 'Gangnam', 'Songpa', 'Gangdong']

    results = []

    for county in counties:
        print(f"\n=== {county} 구 학습 시작 ===")
        
        # 데이터 로드 및 전처리
        scaled_data, scaler, date_data, original_data = load_and_preprocess_data(file_path, county)

        # 연도 기준으로 데이터 분할
        time_step = 90
        X_train, y_train, X_val, y_val, X_test, y_test = split_dataset_by_year(scaled_data, date_data, time_step)

        # 모델 학습
        model = train_model(X_train, y_train, X_val, y_val)
        print(f"=== {county} 구 학습 완료 ===")

        # 예측
        predictions = predict(model, X_test)

        # 예측값을 복원하여 결과 저장
        predictions_inverse = scaler.inverse_transform(predictions.flatten().reshape(-1, 1)).flatten()
        total_cold_cases = np.sum(predictions_inverse)

        # 결과 저장
        results.append({'district': county, 'cold_case': total_cold_cases})

    # 결과를 데이터프레임으로 변환하여 엑셀 파일 저장
    results_df = pd.DataFrame(results)
    results_df.to_excel('predicted_cold_cases.xlsx', index=False)
    print("예측 결과를 predicted_cold_cases.xlsx 파일로 저장하였습니다.")

if __name__ == "__main__":
    main()
