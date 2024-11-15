var map, marker1, marker2, routeLine;
var tmapApiKey = 'gDkNTudIim8P9UUU18StX8dvwGql27Ib4sh7fb9y';
var markers = [];
var polylines = [];


var map = null; // 전역 변수로 선언하여 페이지 로드 시 초기화
var markers = []; // 마커들을 저장할 배열

// 페이지 로드 시 실행될 지도 초기화 함수
function initMap() {
    map = new Tmapv2.Map("map_div", {
        center: new Tmapv2.LatLng(37.5665, 126.9780), // 초기 중심 좌표를 서울의 중심으로 설정
        width: "100%",
        height: "400px",
        zoom: 12
    });
}

// 기존 마커들을 삭제하는 함수
function clearMarkers() {
    markers.forEach(marker => marker.setMap(null)); // 모든 마커를 지도에서 제거
    markers = []; // 배열 초기화
}

// 지도 및 경로 찾기와 감기 예측 데이터 표시를 모두 처리하는 함수
function initMapWithMarkers() {

    // 사용자 입력값 가져오기
    var startAddress = document.getElementById("start_address").value.trim();
    var destinationAddress = document.getElementById("end_address").value.trim();

    // 주소 확인 후 길찾기 진행
    if (!startAddress || !destinationAddress) {
        alert("출발지와 도착지 주소를 모두 입력해 주세요.");
        return;
    }

    console.log("출발지 주소:", startAddress);
    console.log("도착지 주소:", destinationAddress);

    // 기존 마커들 삭제
    clearMarkers();

    // 출발지 좌표 가져오기
    getCoordinates(startAddress, function(startLat, startLon) {
        // 도착지 좌표 얻기
        getCoordinates(destinationAddress, function(destinationLat, destinationLon) {
            // 출발지와 도착지 마커 추가
            var marker1 = new Tmapv2.Marker({
                position: new Tmapv2.LatLng(startLat, startLon),
                map: map
            });
            var marker2 = new Tmapv2.Marker({
                position: new Tmapv2.LatLng(destinationLat, destinationLon),
                map: map
            });

            // 마커를 배열에 저장
            markers.push(marker1, marker2);

            // 지도의 범위를 두 마커가 모두 보이도록 조정
            var bounds = new Tmapv2.LatLngBounds();
            bounds.extend(new Tmapv2.LatLng(startLat, startLon));
            bounds.extend(new Tmapv2.LatLng(destinationLat, destinationLon));
            map.fitBounds(bounds);

            // 감기 예측 데이터를 표시하기 위한 구 이름 가져오기
            displayFluPredictionInfo(startAddress, destinationAddress, startLat, startLon, destinationLat, destinationLon);

            // 경로 찾기 함수 호출 (경로 찾기 실행 보장)
            findRoute(startLat, startLon, destinationLat, destinationLon);
        });
    });
}

// 페이지가 로드될 때 초기 지도를 설정
window.onload = function() {
    initMap();
};


// 주소에서 구 이름에 따라 감기 예측 데이터를 지도에 표시하는 함수
function displayFluPredictionInfo(startAddress, endAddress, startLat, startLon, endLat, endLon) {
   // CSV 파일 경로를 확인하고 감기 예측 데이터를 로드
   $.get("static/predicted_cases_2024-01-01_UTF.csv", function(data) {
       const fluData = Papa.parse(data, { header: true }).data;

       const fluCases = {};
       fluData.forEach(row => {
           fluCases[row['district']] = row['cold_case'];
       });

       // 디버깅: fluCases 객체 내용 출력
       console.log("Loaded fluCases data:", fluCases);

       // 출발지와 도착지 구 이름을 구해 예측 데이터를 지도에 표시
       getDistrictName(startAddress, function(startGu) {
           getDistrictName(endAddress, function(endGu) {
               console.log("출발지 구:", startGu, "도착지 구:", endGu); // 추가 디버깅 로그
               addFluCaseMarkers(startGu, endGu, startLat, startLon, endLat, endLon, fluCases);
           });
       });
   });
}



// 주소에서 구 이름을 추출하는 함수 (Tmap Geocoding API 사용)
function getDistrictName(address, callback) {
   $.ajax({
       method: "GET",
       url: "https://apis.openapi.sk.com/tmap/geo/fullAddrGeo?version=1",
       data: {
           format: "json",
           coordType: "WGS84GEO",
           fullAddr: address,
           appKey: tmapApiKey  // Tmap API Key 입력
       },
       success: function(response) {
           const districtName = response.coordinateInfo.coordinate[0].gu_gun; // 구 이름 추출
           callback(districtName);
       },
       error: function(error) {
           console.error("구 이름을 찾을 수 없습니다:", error);
           callback(null);
       }
   });
}

// 구에 따라 마커 옆에 감기 예측 데이터를 표시하는 함수
function addFluCaseMarkers(startGu, endGu, startLat, startLon, endLat, endLon, fluCases) {
   // 출발지 구 예측 데이터 표시
   if (startGu && fluCases[startGu]) {
       const fluCaseText = `예측 감기 환자 수: ${fluCases[startGu]}`;
       const startInfoWindow = new Tmapv2.InfoWindow({
           position: new Tmapv2.LatLng(startLat, startLon),
           content: `<div class="flu-info">${startGu} ${fluCaseText}</div>`,
           map: map
       });
   } else {
       console.warn(`출발지 구에 대한 감기 예측 데이터가 없습니다: ${startGu}`);
   }

   // 도착지 구 예측 데이터 표시
   if (endGu && fluCases[endGu]) {
       const fluCaseText = `예측 감기 환자 수: ${fluCases[endGu]}`;
       const endInfoWindow = new Tmapv2.InfoWindow({
           position: new Tmapv2.LatLng(endLat, endLon),
           content: `<div class="flu-info">${endGu} ${fluCaseText}</div>`,
           map: map
       });
   } else {
       console.warn(`도착지 구에 대한 감기 예측 데이터가 없습니다: ${endGu}`);
   }
}



// 주소를 전체 문자열로 변환한 후, 좌표 변환 API를 이용해 위도와 경도로 변환하는 함수
function getCoordinates(address, callback) {
   console.log("Sending route request to backend with coordinates:", address);  // 디버깅 로그 추가

   $.ajax({
      method: "GET",
      url: "https://apis.openapi.sk.com/tmap/geo/fullAddrGeo?version=1", // Tmap 좌표 변환 API
      data: {
         version: 1,
         format: "json",
         coordType: "WGS84GEO",
         fullAddr: address,
         appKey: tmapApiKey  // 자신의 Tmap API 키 사용
      },
      success: function(response) {
         if (response && response.coordinateInfo && response.coordinateInfo.coordinate) {
            var lat = response.coordinateInfo.coordinate[0].lat;
            var lon = response.coordinateInfo.coordinate[0].lon;
            console.log("Coordinates received:", lat, lon);  // 좌표 디버깅 로그 추가
            callback(lat, lon); // 좌표 값을 콜백으로 전달
         } else {
            console.error("좌표를 찾을 수 없습니다.");
         }
      },
      error: function(error) {
         console.error("좌표 변환 실패", error);
      }
   });
}


// 경로 찾기 함수
function findRoute(startLat, startLon, destinationLat, destinationLon) {
    console.log("Finding route from", startLat, startLon, "to", destinationLat, destinationLon);
 
    var routeSelectionDiv = document.getElementById('routeSelection');
    routeSelectionDiv.innerHTML = '';  // 이전 경로 정보 제거
 
    $.ajax({
        method: "POST",
        url: "http://127.0.0.1:5001/find_route",
        contentType: "application/json",
        data: JSON.stringify({
            start_lat: startLat,
            start_lon: startLon,
            end_lat: destinationLat,
            end_lon: destinationLon
        }),
        success: function(response) {
            console.log("Received response:", response);
 
            if (response.metaData && response.metaData.plan && response.metaData.plan.itineraries && response.metaData.plan.itineraries.length > 0) {
                
                response.metaData.plan.itineraries.forEach(function(itinerary, index) {
                    const totalMinutes = Math.floor(itinerary.totalTime / 60);
                    const hours = Math.floor(totalMinutes / 60);
                    const minutes = totalMinutes % 60;
                    const timeDisplay = hours > 0 ? `${hours}시간 ${minutes}분` : `${minutes}분`;
 
                    var routeSummary = document.createElement('div');
                    routeSummary.className = 'route-summary';
                    routeSummary.innerHTML = `
                        <h3>경로 ${index + 1}</h3>
                    `;
 
                    // 경로 시간과 요금, 버튼을 같은 줄에 배치하는 새로운 div 생성
                    var routeDetails = document.createElement('div');
                    routeDetails.className = 'route-details'; // Flex 레이아웃을 위한 클래스
 
                    var routeInfo = document.createElement('p');
                    routeInfo.innerText = `총 시간: ${timeDisplay}, 요금: ${itinerary.fare.regular.totalFare}원`;
 
                    var routeButton = document.createElement('button');
                    routeButton.innerHTML = "이 경로 선택";
                    routeButton.className = 'select-route-btn';
                    routeButton.onclick = function() {
                        document.querySelectorAll('.station-info').forEach(function(info) {
                            info.style.display = 'none';
                        });
 
                        stationInfo.style.display = 'block';
                        drawRoute(itinerary.legs);
 
                        // 혼잡도 데이터를 요청하고 성공 시 정류장 정보를 표시
                        processCongestionData(itinerary.legs, function(congestionData) {
                            displayStationInfo(itinerary.legs, stationInfo, congestionData);
                        });
                    };
 
                    routeDetails.appendChild(routeInfo);
                    routeDetails.appendChild(routeButton);
 
                    var stationInfo = document.createElement('div');
                    stationInfo.className = 'station-info';
                    stationInfo.style.display = 'none';
 
                    routeSummary.appendChild(routeDetails);
                    routeSelectionDiv.appendChild(routeSummary);
                    routeSelectionDiv.appendChild(stationInfo);
                });
            } else {
                console.error("경로 탐색 결과가 없습니다.", response);
            }
        },
        error: function(error) {
            console.error("경로 찾기 실패", error);
        }
    });
 }
 



// 타는 역과 내리는 역만 표시하는 함수 (혼잡도 정보 추가)
function displayStationInfo(legs, stationInfoDiv, congestionData) {
   // 기존 내용을 초기화하여 지도 아래 정보가 다시 표시되지 않도록 설정
   stationInfoDiv.innerHTML = '';

   // congestionData가 객체일 경우 배열로 변환
   if (congestionData && !Array.isArray(congestionData)) {
       congestionData = Object.values(congestionData).flat();
   }

   // legs에 대해 반복하여 경로 선택 UI에 혼잡도 정보 표시
   legs.forEach(function(leg) {
       if (leg.mode === 'SUBWAY' && leg.passStopList && leg.passStopList.stationList) {
           const startStation = leg.passStopList.stationList[0];
           const endStation = leg.passStopList.stationList[leg.passStopList.stationList.length - 1];

           // 타는 역 혼잡도 정보
           const startStationCongestion = congestionData && congestionData.find(data => data.station_name.replace("역", "").trim() === startStation.stationName.replace("역", "").trim());
           const startCongestionText = startStationCongestion ? getCongestionText(startStationCongestion.congestion_data) : "혼잡도 없음";

           // 내리는 역 혼잡도 정보
           const endStationCongestion = congestionData && congestionData.find(data => data.station_name.replace("역", "").trim() === endStation.stationName.replace("역", "").trim());
           const endCongestionText = endStationCongestion ? getCongestionText(endStationCongestion.congestion_data) : "혼잡도 없음";

           // 경로 선택 UI에만 정보를 표시할 요소 생성
           const startStationInfo = document.createElement('p');
           startStationInfo.innerHTML = `타는 역: ${startStation.stationName} - 혼잡도: ${startCongestionText}`;
           stationInfoDiv.appendChild(startStationInfo);

           const endStationInfo = document.createElement('p');
           endStationInfo.innerHTML = `내리는 역: ${endStation.stationName} - 혼잡도: ${endCongestionText}`;
           stationInfoDiv.appendChild(endStationInfo);

           // 디버깅 로그로 혼잡도 정보를 확인
           console.log(`타는 역: ${startStation.stationName} - 혼잡도: ${startCongestionText}`);
           console.log(`내리는 역: ${endStation.stationName} - 혼잡도: ${endCongestionText}`);
       }
   });
}












// 모든 폴리라인을 지도에서 제거하는 함수
function removePolylines() {
   if (polylines) {
      polylines.forEach(function(polyline) {
         polyline.setMap(null);  // 폴리라인을 지도에서 제거
      });
      polylines = [];  // 배열 초기화
   }
}

function drawRoute(legs) {
   removeMarkers();  // 기존 마커 삭제
   removePolylines();  // 기존 경로 선 삭제

   legs.forEach(function(leg, index) {
      console.log(`Leg ${index} mode:`, leg.mode);  // 각 leg의 mode를 확인

      let routeCoordinates = [];
      let lineColor;  // 교통수단에 따른 색상 설정

      // 교통수단별 색상 설정
      switch (leg.mode) {
         case 'WALK':
            lineColor = "#00FF00";  // 도보는 초록색
            break;
         case 'BUS':
            lineColor = "#FFA500";  // 버스는 주황색
            break;
         case 'SUBWAY':
            lineColor = "#0000FF";  // 지하철은 파란색
            break;
         case 'EXPRESSBUS':
            lineColor = "#FFD700";  // 고속/시외버스는 금색
            break;
         case 'TRAIN':
            lineColor = "#800080";  // 기차는 보라색
            break;
         case 'AIRPLANE':
            lineColor = "#00CED1";  // 항공은 청록색
            break;
         case 'FERRY':
            lineColor = "#1E90FF";  // 해운은 짙은 파란색
            break;
         default:
            lineColor = "#FF0000";  // 알 수 없는 모드
            console.warn(`Unknown mode: ${leg.mode}`);
      }

      console.log(`Polyline color for mode ${leg.mode}:`, lineColor);  // 각 mode에 따른 색상 출력

      // WALK 구간인 경우 start와 end 좌표만 사용하여 선을 그림
      if (leg.mode === 'WALK' && leg.start && leg.end) {
         routeCoordinates.push(new Tmapv2.LatLng(leg.start.lat, leg.start.lon));
         routeCoordinates.push(new Tmapv2.LatLng(leg.end.lat, leg.end.lon));
      } 
      // 다른 모드의 경우 passStopList를 통해 좌표 생성
      else if (leg.passStopList && leg.passStopList.stationList) {
         leg.passStopList.stationList.forEach(function(station) {
            if (station.lat && station.lon) {
               routeCoordinates.push(new Tmapv2.LatLng(station.lat, station.lon));
            }
         });
      } else {
         console.warn(`No station list or start/end data found for mode ${leg.mode}.`);
      }

      // 경로를 나타내는 선 생성
      if (routeCoordinates.length > 0) {
         let polyline = new Tmapv2.Polyline({
            path: routeCoordinates,
            strokeColor: lineColor,  // 각 구간별 색상 적용
            strokeWeight: 6,
            strokeStyle: 'solid',  // solid 스타일로 설정
            map: map
         });
          // 생성한 폴리라인을 전역 배열에 추가
          window.polylines.push(polyline);
         }

   });
}



// 받은 경로 데이터를 이 함수로 전달하여 지도에 경로 그리기
function handleRouteData(response) {
   const routes = response.routes;
   routes.forEach(route => {
       drawRoute(route);
   });
}


// 혼잡도 데이터를 서버에서 요청하여 호출 후 콜백으로 전달하는 함수
function processCongestionData(legs, callback) {
   const targetStations = [];

   // SUBWAY 모드의 타는 역과 내리는 역 정보를 추출하여 요청 대상 스테이션 리스트 생성
   legs.forEach((leg) => {
       if (leg.mode === 'SUBWAY' && leg.passStopList && leg.passStopList.stationList) {
           const startStation = leg.passStopList.stationList[0];
           const endStation = leg.passStopList.stationList[leg.passStopList.stationList.length - 1];
           targetStations.push({ station_name: startStation.stationName, route_name: leg.route });
           targetStations.push({ station_name: endStation.stationName, route_name: leg.route });
       }
   });

   console.log("Sending target stations data to server:", targetStations);

   $.ajax({
       method: "POST",
       url: "http://127.0.0.1:5001/get_congestion",
       contentType: "application/json",
       data: JSON.stringify({ stations: targetStations }),
       success: function(response) {
           console.log("Received congestion data:", response);
           callback(response);  // 혼잡도 데이터를 콜백으로 전달
       },
       error: function(error) {
           console.error("혼잡도 데이터 요청 실패", error);
           callback([]);  // 오류 시 빈 배열을 콜백으로 반환
       }
   });
}




// 혼잡도를 텍스트로 변환하는 함수
function getCongestionText(congestionLevel) {
   if (congestionLevel >= 80) {
       return "매우 혼잡";
   } else if (congestionLevel >= 60) {
       return "혼잡";
   } else if (congestionLevel >= 40) {
       return "보통";
   } else {
       return "여유";
   }
}

// 혼잡도 데이터를 서버에서 요청하여 마커를 생성하는 함수
function displayCongestionMarkers(stationCoordinates, congestionData) {
   console.log("Displaying congestion markers for received data:", stationCoordinates);

   // congestionData가 배열인지 확인하고 아니면 변환
   if (!Array.isArray(congestionData)) {
       congestionData = Object.values(congestionData).flat();
   }

   // stationCoordinates가 객체인 경우 배열로 변환
   const stationArray = Array.isArray(stationCoordinates) ? stationCoordinates : Object.values(stationCoordinates).flat();

   // 각 역의 혼잡도에 따라 마커를 지도에 표시
   congestionData.forEach(function(stationData) {
       const stationName = stationData.station_name.replace("역", "").trim();
       const routeName = stationData.route_name;
       const congestionLevel = stationData.congestion_data;

       // stationArray에서 일치하는 좌표 찾기
       const matchedStation = stationArray.find(coord => coord.name.replace("역", "").trim() === stationName);

       if (!matchedStation) {
           console.warn(`좌표 정보가 없습니다: ${stationName} (${routeName})`);
           return;
       }

       const { lat, lon } = matchedStation;
       console.log(`좌표를 찾았습니다 - ${stationName}: (${lat}, ${lon})`);

       // 혼잡도에 따른 마커 색상 설정
       const markerColor = getMarkerColor(congestionLevel);

       // 마커 생성 및 지도에 추가 (말풍선은 생략)
       const marker = new Tmapv2.Marker({
           position: new Tmapv2.LatLng(lat, lon),
           map: map,
           icon: {
               fillColor: markerColor,
               fillOpacity: 0.8,
               strokeColor: "#000000",
               strokeWeight: 1
           }
       });

       markers.push(marker);
   });
}

// 혼잡도 데이터에 따라 마커와 정보창을 생성하여 지도에 표시하는 함수
// 혼잡도에 따른 마커 색상을 결정하는 함수
function getMarkerColor(congestionLevel) {
   if (congestionLevel >= 80) {
       return "#FF0000"; // 매우 혼잡 - 빨간색
   } else if (congestionLevel >= 50) {
       return "#FFA500"; // 혼잡 - 주황색
   } else if (congestionLevel >= 30) {
       return "#FFFF00"; // 약간 혼잡 - 노란색
   } else {
       return "#00FF00"; // 원활 - 초록색
   }
}



// 기존 마커 삭제 함수
function removeMarkers() {
   markers.forEach(function(marker) {
      marker.setMap(null);
   });
   markers = [];
}

// 기존 경로 삭제 함수
function removePolylines() {
   polylines.forEach(function(polyline) {
      polyline.setMap(null);
   });
   polylines = [];
}

