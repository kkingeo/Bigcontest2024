import pandas as pd
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

app = Flask(__name__)

# 이 변수에 최신 데이터를 저장
latest_data = None

def update_data():
    global latest_data
    # 현재 날짜 구하기
    today = datetime.now().strftime('%Y-%m-%d')
    # 당일 날짜에 맞는 데이터 필터링
    '''df를 모델에서 가져온 데이터의 이름으로 바꿔줘야 함'''
    latest_data = df[df['date'] == today]
    print(f"데이터가 {today}로 갱신되었습니다.")

# 스케줄러 설정 (매일 오전 4시에 데이터 갱신)
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_data, trigger="cron", hour=4, minute=0)
scheduler.start()

# API 엔드포인트: 갱신된 데이터를 프론트엔드로 전달
@app.route('/get_data', methods=['GET'])
def get_data():
    if latest_data is not None and not latest_data.empty:
        result = latest_data.to_dict(orient='records')
        return jsonify(result)
    else:
        return jsonify({'message': 'No data for today.'}), 503

if __name__ == '__main__':
    update_data()  # 서버 시작 시 한 번 데이터를 갱신
    app.run(debug=True)