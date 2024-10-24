var map, marker1, marker2, routeLine;
var tmapApiKey = 'gDkNTudIim8P9UUU18StX8dvwGql27Ib4sh7fb9y';
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
      contentType: "application/json",
      data: JSON.stringify({
         start_lat: startLat,
         start_lon: startLon,
         end_lat: destinationLat,
         end_lon: destinationLon

      }), success: function(response) {
         console.log("Received response:", response);  // 응답 전체 출력
         if (response && response.plan && response.plan.itineraries && response.plan.itineraries.length > 0) {
            console.log("Valid route response received:", response.plan.itineraries);  // 디버깅 로그 추가
             
             // 경로 선택 UI 생성
            var routeSelectionDiv = document.getElementById('routeSelection');
            routeSelectionDiv.innerHTML = '';  // 이전 내용 제거
             
             // 경로 리스트 생성
            response.plan.itineraries.forEach(function(itinerary, index) {
               // 경로 요약 정보를 표시할 요소 생성 (예: 총 시간, 요금)
               var routeSummary = document.createElement('div');
               routeSummary.innerHTML = "경로 " + (index + 1) + ": 총 시간 - " + itinerary.totalTime + "초, 요금 - " + itinerary.fare.regular.totalFare + "원";
               routeSelectionDiv.appendChild(routeSummary);

               // 혼잡도 정보를 추가할 요소 생성
               var congestionInfo = document.createElement('div');
               congestionInfo.innerHTML = getCongestionInfo(itinerary.legs);  // 혼잡도 정보 추가

                 // 경로 선택 버튼 생성
               var routeButton = document.createElement('button');
               routeButton.innerHTML = "이 경로 선택";
               routeButton.onclick = function() {
                  drawRoute(itinerary.legs);  // 경로의 세부 단계를 그리는 함수
                  processCongestionData(itinerary.legs);  // 혼잡도 데이터 처리
               };
                 
                 // UI에 추가
               routeSelectionDiv.appendChild(routeSummary);
               routeSelectionDiv.appendChild(congestionInfo);  // 혼잡도 정보 추가
               routeSelectionDiv.appendChild(routeButton);
            });
         } else {
            console.error("경로 탐색 결과가 없습니다.", response);  // 오류가 발생했을 경우의 로그
         }
      },
      error: function(error) {
         console.error("경로 찾기 실패", error);
      }
   });
}



function drawRoute(legs) {
   removeMarkers();  // 기존 마커 삭제
   removePolylines();  // 기존 경로 삭제

   legs.forEach(function(leg) {
      if (leg.mode === 'WALK') {
         console.log("도보 경로 그리기:", leg.steps);
         // 도보 경로에 대한 로직 추가 (지도 API 등 활용)
      } else if (leg.mode === 'SUBWAY') {
         console.log("지하철 경로 그리기:", leg.passStopList.stationList);
         // 지하철 경로에 대한 로직 추가 (지도 API 등 활용)
      }

      var startLat = leg.startLat || leg.startLocation.lat;  // startLocation에서 lat 값 추출
      var startLon = leg.startLon || leg.startLocation.lon;  // startLocation에서 lon 값 추출
      var endLat = leg.endLat || leg.endLocation.lat;        // endLocation에서 lat 값 추출
      var endLon = leg.endLon || leg.endLocation.lon;        // endLocation에서 lon 값 추출

      // 출발지 마커 추가
      var marker1 = new Tmapv2.Marker({
         position: new Tmapv2.LatLng(leg.start.lat, leg.start.lon),  // 출발지 좌표 설정
         map: map
      });
      markers.push(marker1);  // 마커 리스트에 추가

      // 도착지 마커 추가
      var marker2 = new Tmapv2.Marker({
         position: new Tmapv2.LatLng(leg.end.lat, leg.end.lon),  // 도착지 좌표 설정
         map: map
      });
      markers.push(marker2);  // 마커 리스트에 추가

      // 지도의 범위를 두 마커가 모두 보이도록 조정
      var bounds = new Tmapv2.LatLngBounds();
      bounds.extend(new Tmapv2.LatLng(leg.start.lat, leg.start.lon));
      bounds.extend(new Tmapv2.LatLng(leg.end.lat, leg.end.lon));
      map.fitBounds(bounds);
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


function processCongestionData(legs) {
   legs.forEach(function(leg) {
       if (leg.mode === 'SUBWAY' && leg.passStopList) {
           leg.passStopList.stationList.forEach(function(station) {
               // 혼잡도 데이터를 가져옴
               var congestionLevel = getStationCongestion(station.stationID);

               // 혼잡도에 맞는 마커 색상 설정
               var markerColor = getMarkerColor(congestionLevel);

               // 혼잡도에 맞는 마커 생성
               var marker = new Tmapv2.Marker({
                   position: new Tmapv2.LatLng(station.lat, station.lon),
                   map: map,
                   icon: {
                       fillColor: markerColor,  // 마커 색상 설정
                       fillOpacity: 0.8,        // 마커 불투명도 설정
                       strokeColor: "#000000",  // 마커 테두리 색상
                       strokeWeight: 1          // 마커 테두리 두께
                   }
               });

               // 마커에 혼잡도 정보 표시
               var infoWindow = new Tmapv2.InfoWindow({
                   position: new Tmapv2.LatLng(station.lat, station.lon),
                   content: "<div>" + station.stationName + ": " + congestionLevel + " (혼잡도)</div>", // 마커 정보창 내용
                   map: map
               });

               markers.push(marker);  // 마커를 배열에 추가
           });
       }
   });
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

