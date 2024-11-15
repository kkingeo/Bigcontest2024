from flask import Flask, request, jsonify
from flask_cors import CORS  # Flask-CORS 임포트
import requests
from datetime import datetime
import urllib.parse

app = Flask(__name__)
CORS(app)

API_KEY = 'RWOyGTYZEd6wRVENQxG0d7jBRDM2UhS17gohlHjf'
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
        #print("Response JSON:")  # 응답 데이터 출력
        #print(response.text)  # 전체 응답을 문자열로 출력 (디버깅용)
        
        if response.status_code == 200:
            route_data = response.json()  # 전역 변수에 할당
            # print("Route Data:", route_data)  # 제대로 된 응답 데이터인지 확인
            # 지하철 정보 추출 함수 호출 (갱신 수행)
            #all_subway_info = extract_subway_info(route_data)
            #print("Updated all_subway_info:", all_subway_info) # 확인 로그
            return jsonify(route_data), 200
        else:
            return jsonify({"error": "Tmap API request failed"}), response.status_code
    except requests.RequestException as e:
        print(f"Request failed: {e}")  # 예외 상황 출력
        return jsonify({"error": "Unable to find route"}), 500


def get_congestion_for_station(route_name, station_name):
    # 현재 시간 반영 (요일과 시간)
    now = datetime.now()
    day_of_week = now.strftime('%a').upper()  # 요일을 MON, TUE 형식으로 반환
    current_hour = int(now.strftime('%H'))  # 현재 시간을 24시간 형식으로 반환

    # 시간 범위 제한 (05 ~ 23시)
    if current_hour < 5:
        current_hour = 5
    elif current_hour > 23:
        current_hour = 23
    hour_str = f"{current_hour:02d}"  # 두 자리 형식으로 맞추기

    headers = {
        "accept": "application/json",
        "appKey": API_KEY
    }

    # URL 인코딩 (노선명과 역명칭)
    encoded_route_name = urllib.parse.quote(route_name)
    encoded_station_name = urllib.parse.quote(station_name)

    # 혼잡도 API URL
    url = f"https://apis.openapi.sk.com/transit/puzzle/subway/congestion/stat/train?routeNm={encoded_route_name}&stationNm={encoded_station_name}&dow={day_of_week}&hh={hour_str}"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            congestion_data = response.json()
            if 'stat' in congestion_data['contents']:
                # 현재 시간에 가장 가까운 혼잡도 데이터를 반환
                closest_congestion = None
                closest_time_diff = float('inf')
                for stat in congestion_data['contents']['stat']:
                    for data in stat['data']:
                        hh = int(data['hh'])
                        mm = int(data['mm'])
                        time_diff = abs((current_hour * 60) - (hh * 60 + mm))
                        if time_diff < closest_time_diff:
                            closest_time_diff = time_diff
                            closest_congestion = data['congestionTrain']
                return closest_congestion
    except requests.HTTPError as e:
        print(f"Error fetching congestion data for {station_name} on {route_name}: {e}")
    except requests.RequestException as e:
        print(f"Request failed for station: {station_name}, route: {route_name}")
    return None


# 프론트엔드로 혼잡도 데이터를 전송하는 API 엔드포인트
@app.route('/get_congestion', methods=['POST'])
def send_congestion_data():
    global all_subway_info
    request_data = request.get_json()  # 프론트엔드에서 받은 데이터 확인
    print("Received station data for congestion:", request_data)

    if not request_data or "stations" not in request_data:
        print("Error: No station data provided.")
        return jsonify({"error": "No station data provided."}), 400

    # 혼잡도 데이터 가져오기
    congestion_results = {}
    for station in request_data["stations"]:
        # 호선 이름 수정
        route_name = station["route_name"]
        if route_name.startswith("수도권"):
            route_name = route_name.replace("수도권", "").strip()
        # 역 이름에 '역' 붙이기
        station_name = station["station_name"]
        if not station_name.endswith("역"):
            station_name += "역"
        # 혼잡도 데이터 호출
        congestion_level = get_congestion_for_station(route_name, station_name)
        
        if congestion_level is not None:
            if route_name not in congestion_results:
                congestion_results[route_name] = []
            congestion_results[route_name].append({
                "station_name": station_name,
                "route_name": route_name,
                "congestion_data": congestion_level
            })
    
    print("Congestion Results:", congestion_results)  # 혼잡도 결과 확인
    
    return jsonify(congestion_results)



if __name__ == '__main__':
    app.run(debug=True, port=5001)


