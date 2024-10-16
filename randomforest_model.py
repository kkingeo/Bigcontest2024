import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.ensemble import StackingRegressor
import xgboost as xgb

# 데이터 로드
data = pd.read_csv('county_data_without_14_20_21_22.csv', encoding='cp949')

# 날짜 관련 변수 추가
data['date'] = pd.to_datetime(data['date'])
data['year'] = data['date'].dt.year
data['month'] = data['date'].dt.month
data['day'] = data['date'].dt.day
data['weekday'] = data['date'].dt.dayofweek

# 차분 기법 (감기 발생 건수의 변화량)
data['diff_cold_cases'] = data['number of cold case'].diff().fillna(0)

# 날짜를 기준으로 정렬
data = data.sort_values(by=['year', 'month', 'day'])

# 데이터셋 분리
train_df = data[(data['year'] >= 2015) & (data['year'] <= 2019)]  # 2015~2019년 데이터
val_df = data[(data['year'] == 2023) & (data['month'] >= 1) & (data['month'] <= 6)]  # 2023년 1~6월 데이터
test_df = data[(data['year'] == 2023) & (data['month'] >= 7) & (data['month'] <= 9)]  # 2023년 7~9월 데이터

# 훈련, 검증, 테스트 데이터 준비
X_train = train_df[['year', 'month', 'day', 'weekday', 'county code', 'diff_cold_cases']]
y_train = train_df['number of cold case']
X_val = val_df[['year', 'month', 'day', 'weekday', 'county code', 'diff_cold_cases']]
y_val = val_df['number of cold case']
X_test = test_df[['year', 'month', 'day', 'weekday', 'county code', 'diff_cold_cases']]
y_test = test_df['number of cold case']

# -------------------------------
# 랜덤포레스트 하이퍼파라미터 최적화
param_grid_rf = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 15, 20],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

grid_search_rf = GridSearchCV(
    estimator=RandomForestRegressor(random_state=42),
    param_grid=param_grid_rf,
    scoring='neg_mean_squared_error',
    cv=5,
    n_jobs=-1,
    verbose=2
)

# 랜덤포레스트 최적의 하이퍼파라미터 탐색
grid_search_rf.fit(X_train, y_train)
best_rf = grid_search_rf.best_estimator_
print(f"Best RF params: {grid_search_rf.best_params_}")

# -------------------------------
# GradientBoosting 하이퍼파라미터 최적화
param_grid_gb = {
    'n_estimators': [100, 200],
    'learning_rate': [0.01, 0.1, 0.2],
    'max_depth': [3, 5, 7]
}

grid_search_gb = GridSearchCV(
    estimator=GradientBoostingRegressor(random_state=42),
    param_grid=param_grid_gb,
    scoring='neg_mean_squared_error',
    cv=5,
    n_jobs=-1,
    verbose=2
)

# GradientBoosting 최적의 하이퍼파라미터 탐색
grid_search_gb.fit(X_train, y_train)
best_gb = grid_search_gb.best_estimator_
print(f"Best GB params: {grid_search_gb.best_params_}")

# -------------------------------
# XGBoost 하이퍼파라미터 최적화
param_grid_xgb = {
    'n_estimators': [100, 200],
    'learning_rate': [0.01, 0.1, 0.2],
    'max_depth': [3, 5, 7]
}

grid_search_xgb = GridSearchCV(
    estimator=xgb.XGBRegressor(random_state=42),
    param_grid=param_grid_xgb,
    scoring='neg_mean_squared_error',
    cv=5,
    n_jobs=-1,
    verbose=2
)

# XGBoost 최적의 하이퍼파라미터 탐색
grid_search_xgb.fit(X_train, y_train)
best_xgb = grid_search_xgb.best_estimator_
print(f"Best XGB params: {grid_search_xgb.best_params_}")

# -------------------------------
# 최적화된 모델을 사용한 Stacking 앙상블 구성
estimators = [
    ('rf', best_rf),
    ('gb', best_gb),
    ('xgb', best_xgb)
]

stacking_model = StackingRegressor(
    estimators=estimators, final_estimator=Ridge(), cv=5
)

# Stacking 모델 학습
stacking_model.fit(X_train, y_train)

# -------------------------------
# MAPE 계산 함수
def mean_absolute_percentage_error(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

# 학습 데이터 예측 및 평가
y_train_pred = stacking_model.predict(X_train)
train_mae = mean_absolute_error(y_train, y_train_pred)
train_rmse = mean_squared_error(y_train, y_train_pred, squared=False)
train_mape = mean_absolute_percentage_error(y_train, y_train_pred)

print(f"Train MAE: {train_mae}")
print(f"Train RMSE: {train_rmse}")
print(f"Train MAPE: {train_mape}%")

# -------------------------------
# 검증 데이터 예측 및 평가
y_val_pred = stacking_model.predict(X_val)
val_mae = mean_absolute_error(y_val, y_val_pred)
val_rmse = mean_squared_error(y_val, y_val_pred, squared=False)
val_mape = mean_absolute_percentage_error(y_val, y_val_pred)

print(f"Validation MAE: {val_mae}")
print(f"Validation RMSE: {val_rmse}")
print(f"Validation MAPE: {val_mape}%")

# -------------------------------
# 테스트 데이터 예측 및 평가
y_test_pred = stacking_model.predict(X_test)
test_mae = mean_absolute_error(y_test, y_test_pred)
test_rmse = mean_squared_error(y_test, y_test_pred, squared=False)
test_mape = mean_absolute_percentage_error(y_test, y_test_pred)

print(f"Test MAE: {test_mae}")
print(f"Test RMSE: {test_rmse}")
print(f"Test MAPE: {test_mape}%")

# -------------------------------
# 그래프 시각화
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 검증 데이터에서 연, 월, 일을 사용해 날짜 생성
dates_val = pd.to_datetime(val_df[['year', 'month', 'day']])

plt.figure(figsize=(12, 6))
plt.plot(dates_val, y_val.values, label='Actual (Validation)', color='b')
plt.plot(dates_val, y_val_pred, label='Predicted (Validation)', color='r', linestyle='--')
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=10))
plt.gcf().autofmt_xdate(rotation=45)
plt.title('Validation Set: Actual vs Predicted')
plt.xlabel('Date')
plt.ylabel('Flu Cases')
plt.legend()
plt.show()

# 테스트 데이터에서 연, 월, 일을 사용해 날짜 생성
dates_test = pd.to_datetime(test_df[['year', 'month', 'day']])

plt.figure(figsize=(12, 6))
plt.plot(dates_test, y_test.values, label='Actual (Test)', color='b')
plt.plot(dates_test, y_test_pred, label='Predicted (Test)', color='r', linestyle='--')
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=10))
plt.gcf().autofmt_xdate(rotation=45)
plt.title('Test Set: Actual vs Predicted')
plt.xlabel('Date')
plt.ylabel('Flu Cases')
plt.legend()
plt.show()