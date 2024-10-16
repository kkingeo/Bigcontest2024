// 지도 생성
document.addEventListener("DOMContentLoaded", function() {
   var mapElement = document.getElementById("map_div");
   
   // map_div 요소가 있는지 확인
   if (mapElement) {
       var map = new Tmapv2.Map("map_div", {
           center: new Tmapv2.LatLng(37.570028, 126.986072),
           width: "100%",
           height: "400px",
           zoom: 15
       });
   } else {
       console.error("map_div 요소를 찾을 수 없습니다.");
   }
});


// URL에서 파라미터를 추출하는 함수
function getQueryParams() {
   var params = new URLSearchParams(window.location.search);
   var start_address = params.get("start_address");
   var end_address = params.get("end_address");
   return { start_address, end_address };
}

// 백엔드로 경로 요청을 보내고 데이터를 처리하는 함수
function fetchRouteData(start_address, end_address) {
   $.ajax({
       method: "POST",
       url: "/find_route",  // 백엔드의 경로 탐색 API 호출
       data: {
           start_address: start_address,
           end_address: end_address
       },
       success: function(response) {
           if (response.routes && response.routes.length > 0) {
               var route = response.routes[0];
               document.getElementById("route_description").textContent = 
                   "총 이동 거리: " + route.walk_distance + "m, 총 시간: " + route.total_time + "분";

               var subwayInfo = "";
               route.stations.forEach(function(station) {
                   var congestionStatus = station.congestion.status || "정보 없음";
                   var congestionLevel = station.congestion.congestionLevel || "N/A";
                   subwayInfo += "<p>" + station.station_name + " (" + station.lat + ", " + station.lon + "): " +
                                 congestionStatus + " (혼잡도 레벨: " + congestionLevel + ")</p>";
               });
               document.getElementById("subway_stations").innerHTML = subwayInfo;

               // 지도에 경로 및 마커 표시
               showMapWithMarkers(route);
           } else {
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

   // 출발지와 도착지 마커 추가
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

// 페이지가 로드되면 자동으로 경로 탐색 및 지도에 표시
document.addEventListener("DOMContentLoaded", function() {
   var params = getQueryParams(); // URL 파라미터 가져오기
   if (params.start_address && params.end_address) {
       // 백엔드로 경로 데이터를 요청
       fetchRouteData(params.start_address, params.end_address);
   }
});
