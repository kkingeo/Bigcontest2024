var map, marker1, marker2, routeLine;
var tmapApiKey = 'Du88s82V2690hjVCJpUFf41sc3Xn94KL5rYJSE38';
var markers = [];
var polylines = [];

// URL에서 파라미터 값을 추출하는 함수
function getQueryParams() {
   var params = new URLSearchParams(window.location.search);

   // 출발지에 대한 파라미터 추출
   var start_city = params.get("start_city") || "";
   var start_gu = params.get("start_gu") || "";
   var start_dong = params.get("start_dong") || "";
   var start_bunji = params.get("start_bunji") || "";

   // 도착지에 대한 파라미터 추출
   var end_city = params.get("end_city") || "";
   var end_gu = params.get("end_gu") || "";
   var end_dong = params.get("end_dong") || "";
   var end_bunji = params.get("end_bunji") || "";

   // 추출한 값을 필드에 설정
   document.getElementById("start_city").value = start_city;
   document.getElementById("start_gu").value = start_gu;
   document.getElementById("start_dong").value = start_dong;
   document.getElementById("start_bunji").value = start_bunji;

   document.getElementById("end_city").value = end_city;
   document.getElementById("end_gu").value = end_gu;
   document.getElementById("end_dong").value = end_dong;
   document.getElementById("end_bunji").value = end_bunji;

   // 전체 주소를 조합하여 반환
   return {
      start: `${start_city} ${start_gu} ${start_dong} ${start_bunji}`,
      destination: `${end_city} ${end_gu} ${end_dong} ${end_bunji}`
   };
}

function initMapWithMarkers() {
   var locations = getQueryParams();  // URL 파라미터에서 값 가져오기
   var startAddress = locations.start;
   var destinationAddress = locations.destination;

   getCoordinates(startAddress, function(startLat, startLon) {
      // 도착지 좌표 얻기
      getCoordinates(destinationAddress, function(destinationLat, destinationLon) {
         // 지도 초기화 (출발지와 도착지를 포함하는 위치로 초기화)
         map = new Tmapv2.Map("map_div", {
            center: new Tmapv2.LatLng(startLat, startLon),
            width: "100%",
            height: "400px",
            zoom: 12
         });

         // 출발지 마커 추가
         marker1 = new Tmapv2.Marker({
            position: new Tmapv2.LatLng(startLat, startLon),
            map: map
         });

         // 도착지 마커 추가
         marker2 = new Tmapv2.Marker({
            position: new Tmapv2.LatLng(destinationLat, destinationLon),
            map: map
         });

         // 지도의 범위를 두 마커가 모두 보이도록 조정
         var bounds = new Tmapv2.LatLngBounds();
         bounds.extend(new Tmapv2.LatLng(startLat, startLon));
         bounds.extend(new Tmapv2.LatLng(destinationLat, destinationLon));
         map.fitBounds(bounds);

         // 경로 찾기 함수 호출
         findRoute(startLat, startLon, destinationLat, destinationLon); // 경로 찾기 실행
      });
   });
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
   console.log("Finding route from", startLat, startLon, "to", destinationLat, destinationLon);  // 디버깅 로그 추가

   $.ajax({
      method: "POST",
      url: "http://127.0.0.1:5001/find_route",  // 백엔드의 경로 탐색 API 호출
      contentType: "application/json",  // POST 요청에 JSON 형식 명시
      data: JSON.stringify({  // 데이터를 JSON으로 전송
         start_lat: startLat,
         start_lon: startLon,
         end_lat: destinationLat,
         end_lon: destinationLon
      }),
      success: function(response) {
         console.log("Received response:", response);  // 전체 응답 데이터를 콘솔에 출력 (응답 전체 확인)
         
         // 응답에서 metaData -> plan -> itineraries 참조
         if (response.metaData && response.metaData.plan && response.metaData.plan.itineraries && response.metaData.plan.itineraries.length > 0) {
            console.log("Valid route response received:", response.metaData.plan.itineraries);  // 유효한 경로 응답 확인

            // 경로 선택 UI 생성
            var routeSelectionDiv = document.getElementById('routeSelection');
            routeSelectionDiv.innerHTML = '';  // 이전 내용 제거
             
            // 경로 리스트 생성
            response.metaData.plan.itineraries.forEach(function(itinerary, index) {
               console.log("Processing itinerary:", itinerary);  // 각 경로를 디버깅하기 위한 로그 추가

               // 경로 요약 정보를 표시할 요소 생성 (예: 총 시간, 요금)
               var routeSummary = document.createElement('div');
               routeSummary.innerHTML = "경로 " + (index + 1) + ": 총 시간 - " + itinerary.totalTime + "초, 요금 - " + itinerary.fare.regular.totalFare + "원";
               
               // 혼잡도 정보를 추가할 요소 생성
               var congestionInfo = document.createElement('div');
               congestionInfo.innerHTML = getCongestionInfo(itinerary.legs);  // 혼잡도 정보 추가
               console.log("Congestion info added:", congestionInfo);  // 혼잡도 정보를 추가한 후 확인

               // 경로 선택 버튼 생성
               var routeButton = document.createElement('button');
               routeButton.innerHTML = "이 경로 선택";
               routeButton.onclick = function() {
                  console.log("Selected route legs:", itinerary.legs);  // 경로 선택 시 다리 정보 확인
                  drawRoute(itinerary.legs);  // 경로의 세부 단계를 그리는 함수
                  processCongestionData(itinerary.legs);  // 혼잡도 데이터 처리
               };
                 
               // UI에 추가
               routeSelectionDiv.appendChild(routeSummary);
               routeSelectionDiv.appendChild(congestionInfo);  // 혼잡도 정보 추가
               routeSelectionDiv.appendChild(routeButton);
            });
         } else {
            console.error("경로 탐색 결과가 없습니다.", response);  // 오류가 발생했을 경우의 상세 로그 추가
         }
      },
      error: function(error) {
         console.error("경로 찾기 실패", error);  // 에러 발생 시 상세 로그 출력
      }
   });
}


function drawRoute(legs) {
   // 각 구간을 선으로 연결할 경로 좌표 배열
   let routeCoordinates = [];

   legs.forEach(function(leg) {
       if (leg.mode === 'SUBWAY' && leg.passStopList && leg.passStopList.stationList) {
           leg.passStopList.stationList.forEach(function(station) {
               // 각 역의 좌표를 배열에 추가
               if (station.lat && station.lon) {
                   routeCoordinates.push(new Tmapv2.LatLng(station.lat, station.lon));
               }
           });
       }
   });

   // Tmapv2.Polyline 객체를 생성하여 선으로 경로를 그리기
   const routeLine = new Tmapv2.Polyline({
       path: routeCoordinates, // 경로 좌표 배열
       strokeColor: "#FF0000", // 선 색상
       strokeWeight: 6, // 선 굵기
       map: map // 지도 객체
   });
}



// 받은 경로 데이터를 이 함수로 전달하여 지도에 경로 그리기
function handleRouteData(response) {
   const routes = response.routes;
   routes.forEach(route => {
       drawRoute(route);
   });
}

// 혼잡도에 따른 마커 색상을 반환하는 함수
function getMarkerColor(congestionLevel) {
   if (congestionLevel === 1) return "green";  // 여유
   if (congestionLevel === 2) return "yellow"; // 보통
   if (congestionLevel === 3) return "red";    // 혼잡
   return "blue";  // 기본 색상 (혼잡도 정보가 없는 경우)
}

function fetchCongestionData() {
   $.ajax({
      method: "POST",
      url: "http://127.0.0.1:5001/get_congestion",
      contentType: "application/json",
      data: JSON.stringify({}),  // 빈 JSON 객체 전달
      success: function(response) {
         console.log("Received congestion data:", response);
         if (response && Object.keys(response).length > 0) {
            displayCongestionMarkers(response);
         } else {
            console.error("혼잡도 데이터가 없습니다.");
         }
      },
      error: function(error) {
         console.error("혼잡도 데이터 요청 실패", error);
      }
   });
}


// 혼잡도 수준에 따른 색상을 반환하는 함수
function getMarkerColor(congestionLevel) {
   if (congestionLevel >= 80) return "#FF0000"; // 혼잡도 높음 (빨간색)
   else if (congestionLevel >= 50) return "#FFA500"; // 혼잡도 중간 (주황색)
   else return "#00FF00"; // 혼잡도 낮음 (초록색)
}

// 혼잡도 데이터에 따라 마커와 정보창을 생성하여 지도에 표시하는 함수
function displayCongestionMarkers(congestionData) {
   for (var route in congestionData) {
      var stations = congestionData[route];
      
      stations.forEach(function(stationData) {
         var stationName = stationData.station_name;
         var routeName = stationData.route_name;
         var congestionLevel = stationData.congestion_data;
         
         var markerColor = getMarkerColor(congestionLevel);

         var marker = new Tmapv2.Marker({
            position: new Tmapv2.LatLng(stationData.lat, stationData.lon),
            map: map,
            icon: {
               fillColor: markerColor,
               fillOpacity: 0.8,
               strokeColor: "#000000",
               strokeWeight: 1
            }
         });

         var infoWindowContent = `<div>${stationName} (${routeName}) 혼잡도: ${congestionLevel}</div>`;
         var infoWindow = new Tmapv2.InfoWindow({
            position: new Tmapv2.LatLng(stationData.lat, stationData.lon),
            content: infoWindowContent,
            map: map
         });

         markers.push(marker);
         markers.push(infoWindow);
      });
   }
}

// 초기 로딩 시 혼잡도 데이터 요청 및 지도 마커 생성
document.addEventListener("DOMContentLoaded", function() {
   fetchCongestionData();  // 혼잡도 데이터 요청하여 마커 생성
});

// 혼잡도 정보를 반환하는 기본 함수 예시
function getCongestionInfo(stationData) {
   return `${stationData.station_name} (${stationData.route_name}) 혼잡도: ${stationData.congestion_data}`;
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

// 페이지 로드 시 지도 및 길찾기 초기화
$(document).ready(function() {
   initMapWithMarkers(); // 페이지 로드 시 길찾기 자동 실행
});
