from flask import Flask, render_template, request, jsonify
import backend
import requests

# Flask 앱 생성
app = Flask(__name__)

# index.html 렌더링
@app.route('/')
def index():
    return render_template('index.html')  # templates 폴더에서 index.html 파일 렌더링

@app.route('/routefinder', methods=['GET'])
def routefinder():
    # 시/도, 구/군, 동, 번지 값을 개별적으로 받기
    start_city = request.args.get('start_city')
    start_gu = request.args.get('start_gu')
    start_dong = request.args.get('start_dong')
    start_bunji = request.args.get('start_bunji')
    
    end_city = request.args.get('end_city')
    end_gu = request.args.get('end_gu')
    end_dong = request.args.get('end_dong')
    end_bunji = request.args.get('end_bunji')
    
    # 각각의 값을 개별적으로 HTML 템플릿에 전달
    return render_template('routefinder.html', 
                           start_city=start_city, 
                           start_gu=start_gu, 
                           start_dong=start_dong, 
                           start_bunji=start_bunji, 
                           end_city=end_city, 
                           end_gu=end_gu, 
                           end_dong=end_dong, 
                           end_bunji=end_bunji)


if __name__ == '__main__':
    app.run(debug=True, port=5000)  # 5000번 포트에서 Flask 서버 실행
