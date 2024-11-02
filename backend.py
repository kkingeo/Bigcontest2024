from flask import Flask, request, jsonify
from flask_cors import CORS  # Flask-CORS 임포트
import requests
from datetime import datetime
import urllib.parse

app = Flask(__name__)
CORS(app)

API_KEY = 'gDkNTudIim8P9UUU18StX8dvwGql27Ib4sh7fb9y'
TMAP_URL = "https://apis.openapi.sk.com/transit/routes"

# 전역 변수로 선언
route_data = None
all_subway_info = None

@app.route('/find_route', methods=['POST'])

def find_route():
    global route_data, all_subway_info  # 전역 변수 사용 선언
    
    # 프론트엔드에서 경도, 위도 좌표를 받아옴
    data = request.get_json()
    start_lon = data.get('start_lon')
    start_lat = data.get('start_lat')
    end_lon = data.get('end_lon')
    end_lat = data.get('end_lat')

    # Tmap API에 요청할 페이로드
    payload = {
        "startX": start_lon,
        "startY": start_lat,
        "endX": end_lon,
        "endY": end_lat,
        "lang": 0,
        "format": "json",
        "count": 10,
        "searchDttm": datetime.now().strftime("%Y%m%d%H%M")
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "appKey": API_KEY
    }

    # Tmap API 요청
    try:
        response = requests.post(TMAP_URL, json=payload, headers=headers)
        
        # 응답 상태 코드와 내용을 출력해 디버깅
        print(f"Response Status Code: {response.status_code}")  # 상태 코드 출력
        print("Response JSON:")  # 응답 데이터 출력
        print(response.text)  # 전체 응답을 문자열로 출력 (디버깅용)
        
        if response.status_code == 200:
            route_data = response.json()  # 전역 변수에 할당
<<<<<<< HEAD
            print("Route Data:", route_data)  # 제대로 된 응답 데이터인지 확인

            # 지하철 정보 추출 함수 호출
            all_subway_info = extract_subway_info(route_data)
=======
            #print("Route Data:", route_data)  # 제대로 된 응답 데이터인지 확인
>>>>>>> f1493a9fc021a018cdd6f66fd8c758cb2edd5c7a
            print("Updated all_subway_info:", all_subway_info) # 확인 로그

            return jsonify(route_data), 200
        else:
            return jsonify({"error": "Tmap API request failed"}), response.status_code
    except requests.RequestException as e:
        print(f"Request failed: {e}")  # 예외 상황 출력
        return jsonify({"error": "Unable to find route"}), 500


# 경로 데이터에서 지하철 정보 추출하는 함수
def extract_subway_info(route_data):
    
    global all_subway_info
    
    all_subway_info = {}

    try:
        itineraries = route_data['metaData']['plan']['itineraries']
        # 각 'itinerary'에서 legs 확인
        for idx, itinerary in enumerate(itineraries):
            
            # 경로에 포함된 지하철역 이름과 호선 정보를 담을 리스트
            subway_station_info = []
            
            for leg in itinerary['legs']:
                # 지하철 경로인지 확인
                if leg['mode'] == 'SUBWAY':
                    route_name = leg['route']  # 호선 정보
                    if '수도권' in route_name or '(급행)' in route_name:
                        route_name = route_name.replace('수도권', '').replace('(급행)', '').strip()
                    
                    # 'passStopList'에서 지하철역 목록 추출
                    for station in leg['passStopList']['stationList']:
                        station_name = station['stationName']
                        
                        # 역 이름 뒤에 '역'을 붙임 (중복 방지 포함)
                        if not station_name.endswith('역'):
                            station_name += '역'
                        
                        # 역 이름과 호선 정보 함께 저장
                        subway_station_info.append({
                            'station_name': station_name,
                            'line': route_name
                        })
            
            # 지하철 정보가 있는 경로만 저장
            if subway_station_info:
                all_subway_info[f'route_{idx + 1}'] = subway_station_info
        print("all_subway_info after extraction:", all_subway_info)  # 추출 직후 값 확인
    except KeyError:
        print("Invalid route data structure")
    
    return all_subway_info


# all_subway_info에서 경로별로 노선명과 역명칭을 가져와서 차례대로 인코딩 및 API 호출
def get_congestion_data(all_subway_info):
    congestion_results = {}
    
    # 현재 시간 반영 (요일과 시간)
    now = datetime.now()
    day_of_week = now.strftime('%a').upper()  # 요일을 MON, TUE 형식으로 반환
    current_hour = int(now.strftime('%H'))  # 현재 시간을 24시간 형식으로 반환
    current_minute = int(now.strftime('%M'))  # 현재 분을 숫자로 반환

    # 시간 범위 제한 (05 ~ 23시)
    if current_hour < 5:
        current_hour = 5
    elif current_hour > 23:
        current_hour = 23
    hour_str = f"{current_hour:02d}"  # 두 자리 형식으로 맞추기

    headers = {
        "accept": "application/json",
        "appKey": API_KEY  # 실제 Tmap API Key 입력
    }

    # all_subway_info에서 경로별로 노선명과 역명칭을 가져와서 API 호출
    for route, stations in all_subway_info.items():
        route_results = []  # 경로별로 혼잡도 데이터를 저장할 리스트

        for station_info in stations:
            route_name = station_info['line']
            station_name = station_info['station_name']

            # URL 인코딩 (노선명과 역명칭)
            encoded_route_name = urllib.parse.quote(route_name)
            encoded_station_name = urllib.parse.quote(station_name)

            # 완성된 URL
            url = f"https://apis.openapi.sk.com/transit/puzzle/subway/congestion/stat/train?routeNm={encoded_route_name}&stationNm={encoded_station_name}&dow={day_of_week}&hh={hour_str}"

            # Tmap API 호출
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    # 응답 데이터 저장
                    congestion_data = response.json()

                    # 현재 시간에 가장 가까운 데이터를 찾기
                    if 'stat' in congestion_data['contents']:
                        closest_congestion = None
                        closest_time_diff = float('inf')

                        for stat in congestion_data['contents']['stat']:
                            for data in stat['data']:
                                hh = int(data['hh'])
                                mm = int(data['mm'])

                                time_diff = abs((current_hour * 60 + current_minute) - (hh * 60 + mm))

                                if time_diff < closest_time_diff:
                                    closest_time_diff = time_diff
                                    closest_congestion = {
                                        'station_name': station_name,
                                        'route_name': route_name,
                                        'congestion_data': data['congestionTrain']
                                    }
                        if closest_congestion:
                            route_results.append(closest_congestion)
            except requests.RequestException as e:
                print(f"Request failed for station: {station_name}, route: {route_name}")

        # 경로별 결과를 딕셔너리에 추가
        if route_results:
            congestion_results[route] = route_results

    return congestion_results

# 프론트엔드로 혼잡도 데이터를 전송하는 API 엔드포인트
@app.route('/get_congestion', methods=['POST'])  # POST로 변경
def send_congestion_data():
    print("Received request data:", request.json)  # 요청 데이터 출력
    global all_subway_info
    
    print("Request received at /get_congestion:", request.json)  # 요청 데이터 확인 로그 추가
    if not all_subway_info:
        print("Error: No subway info available.")
        return jsonify({"error": "No subway info available. Please find the route first."}), 400

    # 혼잡도 데이터 가져오기
    congestion_results = get_congestion_data(all_subway_info)
    print("Congestion Results:", congestion_results) # 혼잡도 결과 확인
    
    # 프론트엔드로 JSON 형식으로 반환
    return jsonify(congestion_results)

if __name__ == '__main__':
    app.run(debug=True, port=5001)

'''
# 프론트엔드로 혼잡도 데이터를 전송하는 API 엔드포인트
@app.route('/get_congestion', methods=['GET'])
def send_congestion_data():
    global all_subway_info
    if not all_subway_info:
        return jsonify({"error": "No subway info available. Please find the route first."}), 400

    # 혼잡도 데이터 가져오기
    congestion_results = get_congestion_data(all_subway_info)
    
    # 프론트엔드로 JSON 형식으로 반환
    return jsonify(congestion_results)


if __name__ == '__main__':
    app.run(debug=True)
'''