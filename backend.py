from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = 'YOUR_TMAP_API_KEY'  # 지오코딩 및 길찾기용 앱키
GEO_URL = "https://apis.openapi.sk.com/tmap/geo/geocoding"
FULLTEXT_GEO_URL = "https://apis.openapi.sk.com/tmap/geo/fullAddrGeo"
TRANSIT_ROUTE_URL = "https://apis.openapi.sk.com/transit/routes"
CONGESTION_URL = "https://apis.openapi.sk.com/transit/puzzle/subway/congestion/stat/train"

@app.route('/find_route', methods=['POST'])
def find_route():
    start_address = request.form.get('start_address')
    end_address = request.form.get('end_address')

    # 1. 출발지 좌표 얻기 (Geocoding -> Full Text Geocoding)
    start_coords = get_coordinates(start_address)
    if not start_coords:
        return jsonify({'error': 'Unable to find start location coordinates'}), 404

    # 2. 도착지 좌표 얻기 (Geocoding -> Full Text Geocoding)
    end_coords = get_coordinates(end_address)
    if not end_coords:
        return jsonify({'error': 'Unable to find end location coordinates'}), 404

    # 3. 길찾기 API 호출
    payload = {
        "startX": start_coords['lon'],
        "startY": start_coords['lat'],
        "endX": end_coords['lon'],
        "endY": end_coords['lat'],
        "lang": 0,
        "format": "json",
        "count": 10,
        "searchDttm": "202301011200"
    }
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "appKey": API_KEY
    }

    try:
        # 길찾기 API 호출
        response = requests.post(TRANSIT_ROUTE_URL, json=payload, headers=headers)
        route_data = response.json()  # 경로 데이터를 처리
        
        # 각 경로마다 지하철 역 리스트 생성
        route_results = []
        for route in route_data.get('features', []):
            if route['geometry']['type'] == 'LineString':
                subway_stations = extract_subway_stations(route['properties'])
                # 각 지하철역에 대해 혼잡도 가져오기
                congestion_data = []
                for station in subway_stations:
                    congestion = get_subway_congestion(station['line'], station['name'])
                    congestion_data.append({
                        'station': station['name'],
                        'congestion': congestion
                    })
                route_results.append({
                    'route': route['properties']['description'],
                    'subway_stations': subway_stations,
                    'congestion_data': congestion_data
                })

        return jsonify(route_results)
    except requests.RequestException as e:
        print(f"길찾기 API 요청 실패: {e}")
        return jsonify({'error': 'Unable to find the route'}), 500


def extract_subway_stations(properties):
    """
    경로 데이터에서 지하철 역 리스트를 추출하는 함수
    """
    subway_stations = []
    for segment in properties.get('segments', []):
        if '지하철' in segment.get('description', ''):
            for stop in segment.get('stops', []):
                subway_stations.append({'name': stop.get('name', 'Unknown Station'), 'line': segment.get('routeNm', 'Unknown Line')})
    return subway_stations


def get_subway_congestion(line, station):
    """
    각 지하철 역에 대해 실시간 혼잡도를 가져오는 함수
    """
    url = f"{CONGESTION_URL}?routeNm={line}&stationNm={station}"
    headers = {
        "accept": "application/json",
        "appKey": API_KEY
    }
    try:
        response = requests.get(url, headers=headers)
        return response.json()  # 혼잡도 정보를 JSON으로 반환
    except requests.RequestException as e:
        print(f"지하철 혼잡도 API 요청 실패: {e}")
        return {'error': 'Unable to get congestion data'}


def get_coordinates(address):
    """
    주소를 입력받아 좌표를 반환하는 함수 (Geocoding -> Full Text Geocoding)
    """
    # 1. 일반 지오코딩 시도
    geocode_response = geocoding(address)
    
    if geocode_response and geocode_response.get('coordinateInfo') and geocode_response['coordinateInfo'].get('coordinate'):
        coordinates = geocode_response['coordinateInfo']['coordinate'][0]
        lat = coordinates.get('lat', coordinates.get('newLat', None))
        lon = coordinates.get('lon', coordinates.get('newLon', None))
        if lat and lon:
            return {'lat': lat, 'lon': lon}

    # 2. 지오코딩 실패 시 풀 텍스트 지오코딩 시도
    fulltext_response = fulltext_geocoding(address)
    
    if fulltext_response and fulltext_response.get('coordinateInfo') and fulltext_response['coordinateInfo'].get('coordinate'):
        coordinates = fulltext_response['coordinateInfo']['coordinate'][0]
        lat = coordinates.get('lat', coordinates.get('newLat', None))
        lon = coordinates.get('lon', coordinates.get('newLon', None))
        if lat and lon:
            return {'lat': lat, 'lon': lon}

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
        return response.json()
    except requests.RequestException as e:
        print(f"Geocoding API 요청 실패: {e}")
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
        print(f"Full Text Geocoding API 요청 실패: {e}")
        return None


if __name__ == '__main__':
    app.run(debug=True)



