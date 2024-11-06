from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = 'Du88s82V2690hjVCJpUFf41sc3Xn94KL5rYJSE38'
GEO_URL = "https://apis.openapi.sk.com/tmap/geo/geocoding"
FULLTEXT_GEO_URL = "https://apis.openapi.sk.com/tmap/geo/fullAddrGeo"
TRANSIT_ROUTE_URL = "https://apis.openapi.sk.com/transit/routes"


@app.route('/find_route', methods=['POST'])
def find_route():
    start_address = request.form.get('start_address')
    end_address = request.form.get('end_address')

    start_coords = get_coordinates(start_address)
    end_coords = get_coordinates(end_address)

    if not start_coords or not end_coords:
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

    try:
        response = requests.post(TRANSIT_ROUTE_URL, json=payload, headers=headers)
        route_data = response.json()

        plan = route_data.get('plan')
        if not plan:
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

        return jsonify({'routes': routes})

    except requests.RequestException as e:
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
    geocode_response = geocoding(address)
    if geocode_response and geocode_response.get('coordinateInfo') and geocode_response['coordinateInfo'].get('coordinate'):
        coordinates = geocode_response['coordinateInfo']['coordinate'][0]
        lat = coordinates.get('lat', coordinates.get('newLat', None))
        lon = coordinates.get('lon', coordinates.get('newLon', None))
        if lat and lon:
            return {'lat': lat, 'lon': lon}

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
    app.run(debug=True)

'''
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
'''

'''
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
                print(f"Processing leg {idx+1}, mode: {leg['mode']}")  # 디버깅: 각 leg의 mode 확인
                # 지하철 경로인지 확인
                if leg['mode'] == 'SUBWAY':
                    route_name = leg['route']  # 호선 정보
                    print(f"Found SUBWAY leg, route name: {route_name}")  # 디버깅: SUBWAY 모드와 노선명 확인
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
                        print(f"Added station: {station_name}, line: {route_name}")  # 디버깅: 각 역 이름과 노선명 확인
            # 지하철 정보가 있는 경로만 저장
            if subway_station_info:
                all_subway_info[f'route_{idx + 1}'] = subway_station_info
                print(f"Added route_{idx + 1} with stations:", subway_station_info)  # 디버깅: 저장된 경로별 지하철역 목록 확인
        print("all_subway_info after extraction:", all_subway_info)  # 추출 직후 값 확인
    except KeyError:
        print("Invalid route data structure")
    print("all_subway_info after extraction:", all_subway_info)  # 최종 확인
    return all_subway_info
'''