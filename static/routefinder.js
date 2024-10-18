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

// 지도 및 길찾기 초기화 함수
function initMapWithMarkers() {
   var locations = getQueryParams(); // URL 파라미터로부터 출발지 및 도착지 정보 추출
   var startAddress = locations.start;
   var destinationAddress = locations.destination;

   // 출발지와 도착지가 있으면 길찾기 자동 실행
   if (startAddress && destinationAddress) {
      getCoordinates(startAddress, function(startLat, startLon) {
         console.log("Start coordinates: ", startLat, startLon); // 좌표 확인 로그
         getCoordinates(destinationAddress, function(destinationLat, destinationLon) {
            console.log("Destination coordinates: ", destinationLat, destinationLon); // 좌표 확인 로그

            if (!map) {
               map = new Tmapv2.Map("map_div", {
                  center: new Tmapv2.LatLng(startLat, startLon),
                  width: "100%",
                  height: "400px",
                  zoom: 12
               });
            }

            // 기존 마커와 경로 삭제
            removeMarkers();
            removePolylines();

            // 출발지 마커 추가
            marker1 = new Tmapv2.Marker({
               position: new Tmapv2.LatLng(startLat, startLon),
               map: map
            });
            console.log("Start marker added: ", marker1); // 마커 생성 확인 로그

            // 도착지 마커 추가
            marker2 = new Tmapv2.Marker({
               position: new Tmapv2.LatLng(destinationLat, destinationLon),
               map: map
            });
            console.log("Destination marker added: ", marker2); // 마커 생성 확인 로그

            markers.push(marker1, marker2); // 마커 리스트에 추가

            var bounds = new Tmapv2.LatLngBounds();
            bounds.extend(new Tmapv2.LatLng(startLat, startLon));
            bounds.extend(new Tmapv2.LatLng(destinationLat, destinationLon));
            map.fitBounds(bounds);

            // 경로 찾기 함수 호출
            findRoute(startLat, startLon, destinationLat, destinationLon); // 경로 찾기 실행
         });
      });
   }
}

// 좌표 변환 API를 이용해 주소를 위도와 경도로 변환하는 함수
function getCoordinates(address, callback) {
   $.ajax({
      method: "GET",
      url: "https://apis.openapi.sk.com/tmap/geo/fullAddrGeo?version=1",
      data: {
         fullAddr: address,
         appKey: tmapApiKey
      },
      success: function(response) {
         if (response && response.coordinateInfo && response.coordinateInfo.coordinate) {
            var lat = response.coordinateInfo.coordinate[0].lat;
            var lon = response.coordinateInfo.coordinate[0].lon;
            callback(lat, lon);
         } else {
            console.error("좌표를 찾을 수 없습니다.", response); // 오류 로그 추가
         }
      },
      error: function(error) {
         console.error("좌표 변환 실패", error); // 오류 로그 추가
      }
   });
}

// 경로 찾기 함수
function findRoute(startLat, startLon, destinationLat, destinationLon) {
   $.ajax({
      method: "POST",
      url: "http://127.0.0.1:5000/find_route",  // 백엔드의 경로 탐색 API 호출
      data: {
         start_address: startLat,  // 출발지 주소
         end_address: destinationLon,  // 도착지 주소
         appKey: tmapApiKey
      },
      success: function(response) {
         if (response && response.routes && response.routes.length > 0) {
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
}

// 경로 그리기 함수
function drawRoute(route) {
   var routeLine = [];

   // 경로 정보로부터 좌표 추출
   route.legs.forEach(function(leg) {
      leg.passShape.forEach(function(coord) {
         var latLng = new Tmapv2.LatLng(coord.lat, coord.lon);
         routeLine.push(latLng);
      });
   });

   if (routeLine.length > 0) {
      // 경로 그리기
      var polyline = new Tmapv2.Polyline({
         path: routeLine,
         strokeColor: "#FF0000",
         strokeWeight: 6,
         map: map
      });
      polylines.push(polyline); // 경로를 관리하는 리스트에 추가
   }
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

document.addEventListener("DOMContentLoaded", function() {
    var button = document.getElementById("find_route_button");
    if (button) {
        button.addEventListener("click", function() {
            initMapWithMarkers(); // 주소 수정 후 길찾기 실행
        });
    } else {
        console.error("find_route_button 요소를 찾을 수 없습니다.");
    }
});
