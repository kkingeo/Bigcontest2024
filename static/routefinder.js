var map, marker1, marker2, routeLine;
var tmapApiKey = 'Du88s82V2690hjVCJpUFf41sc3Xn94KL5rYJSE38';
var markers = [];
var polylines = [];

// URL에서 파라미터 값을 추출하는 함수
function getQueryParams() {
   var params = new URLSearchParams(window.location.search);
   var start_address = params.get("start_address") || "";
   var end_address = params.get("end_address") || "";

   // 필드에 값 설정
   document.getElementById("start_address").value = start_address;
   document.getElementById("end_address").value = end_address;

   return {
      start: start_address,
      destination: end_address
   };
}

function initMapWithMarkers() {
   var locations = getQueryParams();  // URL 파라미터에서 값 가져오기
   var startAddress = locations.start;
   var destinationAddress = locations.destination;

   // 백엔드에 출발지와 도착지 주소를 보내고 경로 데이터를 받아오는 함수 호출
   findRoute(startAddress, destinationAddress);
}


document.addEventListener("DOMContentLoaded", function() {
   // 폼 요소가 로드된 후에 이벤트 리스너를 추가
   var routeForm = document.getElementById('routeForm');
   if (routeForm) {
      routeForm.addEventListener('submit', function(e) {
           e.preventDefault();  // 기본 폼 제출 방지

           // 수정된 출발지와 도착지 값 가져오기
           var startAddress = document.getElementById('start_address').value;
           var endAddress = document.getElementById('end_address').value;

           // 백엔드로 경로 탐색 요청
           findRoute(startAddress, endAddress);
       });
   } else {
         console.error("routeForm 요소를 찾을 수 없습니다.");
   }
});



// 경로 찾기 함수
function findRoute(startAddress, endAddress) {
   console.log("Sending route request to backend with coordinates:", startAddress, endAddress);  // 디버깅 로그 추가
   $.ajax({
      method: "POST",
      url: "http://127.0.0.1:5001/find_route",  // 백엔드의 경로 탐색 API 호출
      data: {
         start_address: startAddress,  // 출발지 주소
         end_address: endAddress,  // 도착지 주소
         appKey: tmapApiKey
      },
      success: function(response) {
         if (response && response.routes && response.routes.length > 0) {
            console.log("Route response received:", response);  // 디버깅 로그 추가
            var route = response.routes[0];
            drawRoute(route);
            processCongestionData(route);  // 혼잡도 데이터 처리 함수 호출
         } else {
            console.error("경로 데이터를 찾을 수 없습니다.");
         }
      },
      error: function(error) {
         console.error("경로 찾기 실패", error);
      }
   });
   console.log("start_address:", startAddress, "end_address:", endAddress);
}

// 지도에 경로 및 마커 표시하는 함수
function drawRoute(route) {
   // 좌표 및 경로 정보를 바탕으로 지도에 표시
   var routeLine = [];
   route.stations.forEach(function(station) {
       var latLng = new Tmapv2.LatLng(station.lat, station.lon);
       routeLine.push(latLng);
   });

   // Polyline으로 경로 그리기
   var polyline = new Tmapv2.Polyline({
       path: routeLine, // 경로 좌표
       strokeColor: "#FF0000", // 경로 색상
       strokeWeight: 6, // 경로 두께
       map: map // 그릴 지도 객체
   });

   // 마커 추가 (출발지와 도착지)
   var marker1 = new Tmapv2.Marker({
       position: new Tmapv2.LatLng(route.stations[0].lat, route.stations[0].lon),
       map: map
   });

   var marker2 = new Tmapv2.Marker({
       position: new Tmapv2.LatLng(route.stations[route.stations.length - 1].lat, route.stations[route.stations.length - 1].lon),
       map: map
   });

   // 지도의 범위를 두 마커가 모두 보이도록 조정
   var bounds = new Tmapv2.LatLngBounds();
   bounds.extend(new Tmapv2.LatLng(route.stations[0].lat, route.stations[0].lon));
   bounds.extend(new Tmapv2.LatLng(route.stations[route.stations.length - 1].lat, route.stations[route.stations.length - 1].lon));
   map.fitBounds(bounds);
}

// 혼잡도 데이터 처리 함수
function processCongestionData(route) {
   var subwayInfo = "";
   route.stations.forEach(function(station) {
      var congestionStatus = station.congestion.status || "정보 없음";
      var congestionLevel = station.congestion.congestionLevel || "N/A";
      subwayInfo += "<p>" + station.station_name + " (" + station.lat + ", " + station.lon + "): " +
                    congestionStatus + " (혼잡도 레벨: " + congestionLevel + ")</p>";
   });
   document.getElementById("subway_stations").innerHTML = subwayInfo;
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

