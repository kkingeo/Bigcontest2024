from flask import Flask, request, jsonify
from flask_cors import CORS  # CORS 추가
import requests

app = Flask(__name__)
CORS(app)  # 모든 출처에서의 요청을 허용

API_KEY = 'Du88s82V2690hjVCJpUFf41sc3Xn94KL5rYJSE38'
GEO_URL = "https://apis.openapi.sk.com/tmap/geo/geocoding"
FULLTEXT_GEO_URL = "https://apis.openapi.sk.com/tmap/geo/fullAddrGeo"
TRANSIT_ROUTE_URL = "https://apis.openapi.sk.com/transit/routes"


@app.route('/find_route', methods=['POST'])
def find_route():
    start_address = request.form.get('start_address')
    end_address = request.form.get('end_address')

    # Start와 End address 확인 로그
    print(f"Received route request: Start Address: {start_address}, End Address: {end_address}")
    
    start_coords = get_coordinates(start_address)
    end_coords = get_coordinates(end_address)

    if not start_coords or not end_coords:
        print("Coordinates could not be found.")  # 디버깅 로그
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
    
    print(f"Payload for Tmap API: {payload}")  # 디버깅 로그

    try:
        response = requests.post(TRANSIT_ROUTE_URL, json=payload, headers=headers)
        print(f"Tmap API Response Status Code: {response.status_code}")  # 응답 상태 코드 확인
        
        route_data = response.json()
        print(f"Tmap API Response Data: {route_data}")  # 응답 데이터 확인


        plan = route_data.get('plan')
        if not plan:
            print("No plan data found in the API response.")  # 디버깅 로그
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

                linestring = leg.get('passShape', {}).get('linestring', '')
                station_info.append({
                    'start_station': leg['start']['name'],
                    'end_station': leg['end']['name'],
                    'distance': leg['distance'],
                    'total_time': leg['sectionTime'],
                    'linestring': linestring
                })

            return station_info

        routes = list(map(lambda it: {
            'walk_distance': it.get('walkDistance'),
            'total_time': it.get('totalTime'),
            'stations': process_legs(it.get('legs', []))
        }, plan.get('itineraries', [])))

        print(f"Routes processed: {routes}")  # 최종 처리된 경로 데이터 확인
        return jsonify({'routes': routes})

    except requests.RequestException as e:
        print(f"Request Exception: {str(e)}")  # 요청 중 예외 발생 시 로그
        return jsonify({'error': 'Unable to find the route'}), 500


def get_subway_congestion(line, station, cache):
    """
    각 지하철 역에 대해 실시간 혼잡도를 가져오는 함수. 중복 호출 방지를 위해 cache 사용.
    """
    if station in cache:
        return cache[station]

    url = f"https://apis.openapi.sk.com/transit/puzzle/subway/congestion/stat/train?routeNm={line}&stationNm={station}"
    headers = {
        "accept": "application/json",
        "appKey": API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        congestion_data = response.json()
        cache[station] = congestion_data  # 캐시에 저장
        return congestion_data
    except requests.RequestException as e:
        return {'error': 'Unable to get congestion data'}


def get_coordinates(address):
    """
    주소를 입력받아 좌표를 반환하는 함수 (지오코딩 -> 풀 텍스트 지오코딩)
    """
    print(f"Geocoding address: {address}")  # 디버깅 로그 추가
    
    geocode_response = geocoding(address)
    
    print(f"Geocode response: {geocode_response}")  # API 응답 출력
    
    if geocode_response and geocode_response.get('coordinateInfo') and geocode_response['coordinateInfo'].get('coordinate'):
        coordinates = geocode_response['coordinateInfo']['coordinate'][0]
        lat = coordinates.get('lat', coordinates.get('newLat', None))
        lon = coordinates.get('lon', coordinates.get('newLon', None))
        if lat and lon:
            print(f"Coordinates found: lat={lat}, lon={lon}")  # 좌표 확인 로그 추가
            return {'lat': lat, 'lon': lon}

    fulltext_response = fulltext_geocoding(address)
    if fulltext_response and fulltext_response.get('coordinateInfo') and fulltext_response['coordinateInfo'].get('coordinate'):
        coordinates = fulltext_response['coordinateInfo']['coordinate'][0]
        lat = coordinates.get('lat', coordinates.get('newLat', None))
        lon = coordinates.get('lon', coordinates.get('newLon', None))
        if lat and lon:
            return {'lat': lat, 'lon': lon}

    print("Coordinates not found")  # 좌표를 찾지 못한 경우
    return None


def geocoding(address):
    headers = {
        'appKey': API_KEY
    }
    params = {
        'version': 1,
        'format': 'json',
        'coordType': 'WGS84GEO',
        'addressType': 'A00',
        'fullAddr': address
    }

    try:
        response = requests.get(GEO_URL, headers=headers, params=params)
        print(f"Geocoding API URL: {response.url}")  # API 요청 URL을 확인하는 로그
        return response.json()
    except requests.RequestException as e:
        print(f"Geocoding API request failed: {str(e)}")  # 요청 실패 로그
        return None


def fulltext_geocoding(address):
    headers = {
        'appKey': API_KEY
    }
    params = {
        'version': 1,
        'format': 'json',
        'coordType': 'WGS84GEO',
        'fullAddr': address
    }

    try:
        response = requests.get(FULLTEXT_GEO_URL, headers=headers, params=params)
        return response.json()
    except requests.RequestException as e:
        return None


if __name__ == '__main__':
    app.run(debug=True, port=5001)