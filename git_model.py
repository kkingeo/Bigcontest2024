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

#4-4
 
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import QuantileTransformer  # QuantileTransformer 사용
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy import stats

# 데이터 로드 및 전처리 함수
def load_and_preprocess_data(file_path, county_name='Jongno'):
    data = pd.read_csv(file_path)
    data['date'] = pd.to_datetime(data['date'])
    # 지정된 카운티 이름으로 필터링
    data = data[data['county name'] == county_name]  
    data = data.sort_values('date').reset_index(drop=True)

    # 1. 결측치 처리: 결측치를 중앙값으로 대체
    data['number of cold case'].fillna(data['number of cold case'].median(), inplace=True)

    # 2. 이상치 탐지: Z-Score를 사용하여 이상치 탐지
    z_scores = np.abs(stats.zscore(data['number of cold case']))
    
    # 3. 이상치 처리: 중앙값으로 이상치 대체
    median_value = data['number of cold case'].median()
    data['number of cold case'] = np.where(z_scores > 3, median_value, data['number of cold case'])

    # Quantile Transformation으로 데이터 정규화
    transformer = QuantileTransformer(output_distribution='uniform')
    scaled_data = transformer.fit_transform(data['number of cold case'].values.reshape(-1, 1))
    
    return scaled_data, transformer, data['date'], data

# 박스 플롯을 그리는 함수
def plot_box(data, title):
    plt.figure(figsize=(10, 5))
    plt.boxplot(data)
    plt.title(title)
    plt.ylabel('Cold Cases')
    plt.show()

# 데이터셋을 연도별로 나누는 함수
def split_dataset_by_year(scaled_data, date_data, time_step=30):
    date_data = pd.to_datetime(date_data)
    year_data = date_data.dt.year

    train_mask = (year_data >= 2015) & (year_data <= 2018)
    val_mask = (year_data == 2019)
    test_mask = (year_data == 2023)

    # 데이터 나누기
    train_data = scaled_data[train_mask]
    val_data = scaled_data[val_mask]
    test_data = scaled_data[test_mask]

    # 시퀀스 생성
    X_train, y_train = create_dataset(train_data, time_step)
    X_val, y_val = create_dataset(val_data, time_step)
    X_test, y_test = create_dataset(test_data, time_step)

    print(f"2023년 데이터 길이: {len(test_data)}")
    print(f"X_test shape: {X_test.shape}, y_test shape: {y_test.shape}")

    return X_train, y_train, X_val, y_val, X_test, y_test

# 시퀀스 생성 함수 (LSTM을 위한 데이터)
def create_dataset(data, time_step=30):
    X, y = [], []
    data_len = len(data)
    for i in range(data_len - time_step):
        X.append(data[i:i + time_step])  # (timesteps, 1) shape
        y.append(data[i + time_step])
    return np.array(X), np.array(y)

# LSTM 모델 정의
class LSTMModel(nn.Module):
    def __init__(self, hidden_size, num_layers):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=hidden_size, num_layers=num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)  # LSTM 적용
        out = self.fc(out[:, -1, :])  # 마지막 LSTM 출력만 사용
        return out

# 학습 및 검증 함수 (LSTM 적용)
def train_model(X_train, y_train, X_val, y_val, epochs=300, lr=0.001, hidden_size=256, num_layers=4):
    model = LSTMModel(hidden_size, num_layers)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    # Tensor로 변환
    X_train = torch.tensor(X_train, dtype=torch.float32).reshape(X_train.shape[0], X_train.shape[1], 1)  # (samples, timesteps, 1)
    y_train = torch.tensor(y_train, dtype=torch.float32)

    if len(X_val) > 0:
        X_val = torch.tensor(X_val, dtype=torch.float32).reshape(X_val.shape[0], X_val.shape[1], 1)  # (samples, timesteps, 1)
        y_val = torch.tensor(y_val, dtype=torch.float32)

    train_losses, val_losses = [], []
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()

        train_losses.append(loss.item())

        if len(X_val) > 0:
            model.eval()
            val_outputs = model(X_val)
            val_loss = criterion(val_outputs, y_val)
            val_losses.append(val_loss.item())

        if epoch % 10 == 0:
            if len(X_val) > 0:
                print(f'Epoch {epoch}, Loss: {loss.item()}, Validation Loss: {val_loss.item()}')
            else:
                print(f'Epoch {epoch}, Loss: {loss.item()}')

    return model, train_losses, val_losses

# 예측 함수
def predict(model, X_test):
    model.eval()
    X_test = torch.tensor(X_test, dtype=torch.float32).reshape(X_test.shape[0], X_test.shape[1], 1)  # (samples, timesteps, 1)
    with torch.no_grad():
        predictions = model(X_test)
    return predictions.numpy()

# 메인 함수
def main():
    file_path = 'filled_county_data.csv'  # 데이터 파일 경로
    county_name = 'Jongno'  # Jongno 구만 학습하도록 설정
    
    # 데이터 로드 및 전처리
    scaled_data, transformer, date_data, original_data = load_and_preprocess_data(file_path, county_name)

    # 박스 플롯: 이상치 대체 전
    plot_box(original_data['number of cold case'], "Original Data Box Plot")

    # 연도 기준으로 데이터 분할
    time_step = 30  # 타임스텝을 설정
    X_train, y_train, X_val, y_val, X_test, y_test = split_dataset_by_year(scaled_data, date_data, time_step)

    # 모델 학습
    model, train_losses, val_losses = train_model(X_train, y_train, X_val, y_val)

    # 예측
    if X_test.shape[0] > 0:  # 테스트 데이터가 있는지 확인
        predictions = predict(model, X_test)

        # 예측값을 정규화된 상태로 그대로 사용
        predictions_normalized = predictions.flatten()

        # 실제 값을 정규화된 상태로 유지
        y_test_normalized = y_test.flatten()

        # 예측값과 실제값 시각화
        plt.figure(figsize=(12, 6))
        plt.plot(predictions_normalized, label='Predicted')
        plt.plot(y_test_normalized, label='Actual')
        plt.title("Predicted vs Actual (Normalized)")
        plt.xlabel("Days")
        plt.ylabel("Cold Cases (Normalized)")
        plt.legend()
        plt.show()
        
        # 예측값을 복원하여 MSE 계산
        predictions_inverse = transformer.inverse_transform(predictions_normalized.reshape(-1, 1))
        y_test_inverse = transformer.inverse_transform(y_test_normalized.reshape(-1, 1))

        mse_original = mean_squared_error(y_test_inverse, predictions_inverse)
        print(f'Mean Squared Error (Original Scale): {mse_original:.4f}')

        # 추가: RMSE 계산
        rmse_original = np.sqrt(mse_original)
        print(f'Root Mean Squared Error (Original Scale): {rmse_original:.4f}')

        # 추가: MAE 계산
        mae_original = mean_absolute_error(y_test_inverse, predictions_inverse)
        print(f'Mean Absolute Error (Original Scale): {mae_original:.4f}')

    else:
        print("No test data available!")

if __name__ == "__main__":
    main()