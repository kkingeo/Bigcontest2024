from flask import Flask, render_template, request, jsonify
import backend
import requests

# Flask 앱 생성
app = Flask(__name__)

# index.html 렌더링
@app.route('/')
def index():
    return render_template('index.html')  # templates 폴더에서 index.html 파일 렌더링

@app.route('/routefinder')
def routefinder():
    start_address = request.args.get('start_address')
    end_address = request.args.get('end_address')
    return render_template('routefinder.html', start_address=start_address, end_address=end_address)


if __name__ == '__main__':
    app.run(debug=True, port=5000)  # 5000번 포트에서 Flask 서버 실행
