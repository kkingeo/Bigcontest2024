var map, marker1, marker2;

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
            height: "100%",
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
         appKey: "Du88s82V2690hjVCJpUFf41sc3Xn94KL5rYJSE38" // 자신의 Tmap API 키로 대체
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

// 페이지 로드 시 지도와 마커 초기화
$(document).ready(function() {
   initMapWithMarkers(); // 페이지 로드 시 지도와 마커 표시
});
