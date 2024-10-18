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

API_KEY = 'Du88s82V2690hjVCJpUFf41sc3Xn94KL5rYJSE38'
TRANSIT_ROUTE_URL = 'https://apis.openapi.sk.com/transit/routes'  # 실제 Tmap API 경로

def get_coordinates(address):
    # 좌표 찾기 함수 예시 (주소에서 위도와 경도를 찾음)
    return {"lat": 37.5665, "lon": 126.9780}  # 테스트 좌표 (서울 시청)

def get_subway_congestion(route, station_name, cache):
    # 혼잡도 데이터 가져오는 함수 예시
    return {"status": "Normal", "congestionLevel": 1}

@app.route('/find_route', methods=['POST'])
def find_route():
    try:
        start_address = request.form.get('start_address')
        end_address = request.form.get('end_address')

        # Start Address 및 End Address 출력
        print(f"Start Address: {start_address}, End Address: {end_address}")

        start_coords = get_coordinates(start_address)
        end_coords = get_coordinates(end_address)

        if not start_coords or not end_coords:
            print("Unable to find coordinates for the provided addresses.")
            return jsonify({'error': 'Unable to find coordinates'}), 404

        payload = {
            "startX": start_coords['lon'],
            "startY": start_coords['lat'],
            "endX": end_coords['lon'],
            "endY": end_coords['lat'],
            "lang": 0,
            "format": "json",
            "count": 10
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "appKey": API_KEY
        }

        print(f"Payload for Tmap API: {payload}")

        # 외부 API 호출
        response = requests.post(TRANSIT_ROUTE_URL, json=payload, headers=headers)

        print(f"Tmap API Response Status Code: {response.status_code}")

        # 응답 데이터를 JSON으로 변환하고, 이를 출력
        route_data = response.json()
        print(f"Tmap API Response Data: {route_data}")  # 응답 데이터 출력
        
        # 경로가 제공되지 않는 경우 처리
        if route_data.get('result') and route_data['result'].get('status') == 11:
            print("출발지와 도착지가 너무 가까움")  # 디버깅 로그
            return jsonify({'error': '출발지와 도착지가 너무 가까워 경로를 제공할 수 없습니다.'}), 400

        # 응답 데이터에서 'plan' 필드 확인
        plan = route_data.get('plan')
        if not plan:
            print("No plan data found in the response.")  # 디버깅 로그
            return jsonify({'error': 'No plan data found'}), 500

        # 중복된 역 제거하기 위해 set 사용
        all_stations = set()
        congestion_cache = {}

        def process_legs(legs):
            station_info = []
            for leg in filter(lambda l: l['mode'] == 'SUBWAY', legs):
                station_list = leg['passStopList']['stationList']
                for station in station_list:
                    station_key = f"{station['stationName']}_{leg['route']}"
                    if station_key not in all_stations:
                        all_stations.add(station_key)
                        congestion = get_subway_congestion(leg['route'], station['stationName'], congestion_cache)
                        station_info.append({
                            'station_name': station['stationName'],
                            'lon': station['lon'],
                            'lat': station['lat'],
                            'congestion': congestion
                        })

                station_info.append({
                    'start_station': leg['start']['name'],
                    'end_station': leg['end']['name'],
                    'distance': leg['distance'],
                    'total_time': leg['sectionTime'],
                    'linestring': leg.get('passShape', {}).get('linestring', '')
                })

            return station_info

        # 경로 데이터 직렬화
        routes = list(map(lambda it: {
            'walk_distance': it.get('walkDistance'),
            'total_time': it.get('totalTime'),
            'stations': process_legs(it.get('legs', []))
        }, plan.get('itineraries', [])))

        return jsonify({'routes': routes})

    except requests.RequestException as e:
        print(f"Request Exception: {str(e)}")
        return jsonify({'error': 'Unable to find the route', 'details': str(e)}), 500
    except Exception as e:
        print(f"General Exception: {str(e)}")
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)  # 5000번 포트에서 Flask 서버 실행
