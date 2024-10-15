var map, marker1, marker2;
var tmapApiKey = 'Du88s82V2690hjVCJpUFf41sc3Xn94KL5rYJSE38';  // 자신의 Tmap API 키로 대체

// URL에서 파라미터 값을 추출하는 함수
function getQueryParams() {
   var params = new URLSearchParams(window.location.search);

   // 출발지와 도착지 주소 추출
   var start_address = params.get("start_address") || "출발지 주소 없음";
   var end_address = params.get("end_address") || "도착지 주소 없음";

   // 필드에 값 설정
   document.getElementById("start_address").value = start_address;
   document.getElementById("end_address").value = end_address;

   return {
      start: start_address,
      destination: end_address
   };
}

// Tmap 지도 초기화 및 마커 추가 함수
function initMapWithMarkers() {
   var locations = getQueryParams(); // URL 파라미터로부터 출발지 및 도착지 정보 추출

   var startAddress = locations.start;
   var destinationAddress = locations.destination;

   // 출발지 좌표 얻기
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
         findRoute(); // 경로 찾기 실행
      });
   });
}

// 좌표 변환 API를 이용해 주소를 위도와 경도로 변환하는 함수
function getCoordinates(address, callback) {
   $.ajax({
      method: "GET",
      url: "https://apis.openapi.sk.com/tmap/geo/fullAddrGeo?version=1", // Tmap 좌표 변환 API
      data: {
         fullAddr: address,
         appKey: tmapApiKey  // 자신의 Tmap API 키 사용
      },
      success: function(response) {
         if (response && response.coordinateInfo && response.coordinateInfo.coordinate) {
            var lat = response.coordinateInfo.coordinate[0].lat;
            var lon = response.coordinateInfo.coordinate[0].lon;
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

// 경로 찾기 함수 (백엔드와 연동)
function findRoute() {
   var locations = getQueryParams(); // URL에서 출발지와 도착지 주소 추출

   // 백엔드에 경로 찾기 요청
   $.ajax({
      method: "POST",
      url: "/find_route", // 백엔드 엔드포인트
      data: {
         start_address: locations.start,
         end_address: locations.destination
      },
      success: function(response) {
         if (response.routes && response.routes.length > 0) {
            // 경로 설명 표시
            var route = response.routes[0];
            document.getElementById("route_description").textContent = 
                "총 이동 거리: " + route.walk_distance + "m, 총 시간: " + route.total_time + "분";

            // 지하철역 정보 표시
            var subwayInfo = "";
            route.stations.forEach(function(station) {
               var congestionStatus = station.congestion.status ? station.congestion.status : "정보 없음";
               var congestionLevel = station.congestion.congestionLevel ? station.congestion.congestionLevel : "N/A";
               subwayInfo += "<p>" + station.station_name + " (" + station.lat + ", " + station.lon + "): " +
                             congestionStatus + " (혼잡도 레벨: " + congestionLevel + ")</p>";
            });
            document.getElementById("subway_stations").innerHTML = subwayInfo;

            // 지도에 경로와 마커 표시
            showMapWithMarkers(route);
         } else {
            document.getElementById("route_description").textContent = "경로 데이터를 찾을 수 없습니다.";
            document.getElementById("subway_stations").innerHTML = "지하철역 정보를 찾을 수 없습니다.";
            console.error("경로 데이터를 찾을 수 없습니다.");
         }
      },
      error: function(error) {
         console.error("경로 요청 실패", error);
      }
   });
}

// 지도에 경로와 마커 표시하는 함수
function showMapWithMarkers(route) {
   // 출발지와 도착지 좌표를 추출하고 지도에 마커로 추가
   var startLatLng = new Tmapv2.LatLng(route.stations[0].lat, route.stations[0].lon); // 첫 번째 역 기준
   var endLatLng = new Tmapv2.LatLng(route.stations[route.stations.length - 1].lat, route.stations[route.stations.length - 1].lon); // 마지막 역 기준

   // 출발지 마커 추가
   var marker1 = new Tmapv2.Marker({
      position: startLatLng,
      map: map
   });

   // 도착지 마커 추가
   var marker2 = new Tmapv2.Marker({
      position: endLatLng,
      map: map
   });

   // 지도의 범위를 두 마커가 모두 보이도록 조정
   var bounds = new Tmapv2.LatLngBounds();
   bounds.extend(startLatLng);
   bounds.extend(endLatLng);
   map.fitBounds(bounds);
}

// 페이지 로드 시 지도와 마커 초기화
$(document).ready(function() {
   initMapWithMarkers(); // 페이지 로드 시 지도와 마커 표시
});
