from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)

# CSV 파일을 불러와서 JSON으로 변환해주는 함수
def load_predictions_from_csv():
    try:
        # 고정된 CSV 파일 이름을 사용하여 파일 불러오기 (테스트 단계)
        csv_file = 'predicted_cases_2023-09-30.csv'
        df = pd.read_csv(csv_file)
        
        # 필요한 데이터만 JSON 형태로 변환
        predictions = df.to_dict(orient='records')
        return predictions
    except FileNotFoundError:
        return {'error': 'File not found'}, 404

# 프론트엔드에서 GET 요청으로 데이터를 받아갈 수 있게 만듦
@app.route('/predicted_cases', methods=['GET'])
def get_predicted_cases():
    # 테스트 단계에서는 target_date를 받지 않고 고정된 파일을 사용
    predictions = load_predictions_from_csv()
    
    if 'error' in predictions:
        return jsonify(predictions), 404
    
    # JSON 형태로 데이터를 반환
    return jsonify(predictions), 200

if __name__ == '__main__':
    app.run(debug=True)

'''
# method = Post 버전 

from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)

# CSV 파일을 불러와서 JSON으로 변환해주는 함수
def load_predictions_from_csv():
    try:
        # 고정된 CSV 파일 이름을 사용하여 파일 불러오기 (테스트 단계)
        csv_file = 'predicted_cases_2023-09-30.csv'
        df = pd.read_csv(csv_file)
        
        # 필요한 데이터만 JSON 형태로 변환
        predictions = df.to_dict(orient='records')
        return predictions
    except FileNotFoundError:
        return {'error': 'File not found'}, 404

# 프론트엔드에서 POST 요청으로 데이터를 받아갈 수 있게 만듦
@app.route('/predicted_cases', methods=['POST'])
def get_predicted_cases():
    # 고정된 CSV 파일을 사용하여 데이터 반환
    predictions = load_predictions_from_csv()
    
    if 'error' in predictions:
        return jsonify(predictions), 404
    
    # JSON 형태로 데이터를 반환
    return jsonify(predictions), 200

if __name__ == '__main__':
    app.run(debug=True)

'''