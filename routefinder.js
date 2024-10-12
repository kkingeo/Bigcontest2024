var map, marker1, marker2;

// URL에서 파라미터 값을 추출하는 함수
function getQueryParams() {
   var params = new URLSearchParams(window.location.search);

   // 출발지 정보
   var start_city_do = params.get("start_city_do");
   var start_gu_gun = params.get("start_gu_gun");
   var start_dong = params.get("start_dong");
   var start_bunji = params.get("start_bunji");

   // 입력된 값들로 필드를 채움 (기본값을 설정)
   document.getElementById("city_do").value = start_city_do || "서울시";
   document.getElementById("gu_gun").value = start_gu_gun || "마포구";
   document.getElementById("dong").value = start_dong || "서교동";
   document.getElementById("bunji").value = start_bunji || "1";

   // 기본 좌표 반환 (서울시청 기본 좌표)
   var lat = 37.56520450;
   var lon = 126.98702028;

   if (start_city_do && start_gu_gun && start_dong && start_bunji) {
      console.log("입력된 출발지: ", start_city_do, start_gu_gun, start_dong, start_bunji);
   }

   // 좌표 반환
   return { lat, lon };
}

// Tmap 지도 초기화
function initTmap() {
   var coords = getQueryParams(); // URL 파라미터로 받은 좌표
   
   // Tmap 지도 설정
   map = new Tmapv2.Map("map_div", {
      center: new Tmapv2.LatLng(coords.lat, coords.lon), // 초기 지도 중심 좌표
      width: "100%",
      height: "100%",
      zoom: 17,
      zoomControl: true,
      scrollwheel: true
   });
   
   // 기본 출발지 마커 설정 (서울시청 기본 좌표)
   marker1 = new Tmapv2.Marker({
      position: new Tmapv2.LatLng(coords.lat, coords.lon),
      map: map
   });
}

// AJAX를 사용하여 백엔드로 좌표 요청 후 출발지와 도착지 마커 설정
function findRoute() {
   var city_do = $("#city_do").val();
   var gu_gun = $("#gu_gun").val();
   var dong = $("#dong").val();
   var bunji = $('#bunji').val();

   // 백엔드로 요청을 보냄
   $.ajax({
      method: "POST",
      url: "/geocode", // 백엔드의 API 엔드포인트
      data: { city_do: city_do, gu_gun: gu_gun, dong: dong, bunji: bunji },
      success: function(response) {
         if (response.lat && response.lon) {
            console.log("출발지 좌표:", response.lat, response.lon);

            // 기존 출발지 마커 삭제
            marker1.setMap(null);

            // 응답받은 출발지 좌표로 새로운 마커 설정
            var startLatLng = new Tmapv2.LatLng(Number(response.lat), Number(response.lon));
            marker1 = new Tmapv2.Marker({
               position: startLatLng,
               map: map
            });

            // 도착지 좌표도 설정 후, 두 좌표를 지도에 보여줌
            addDestinationMarker();  // 도착지 마커 추가
         } else {
            console.error("출발지 좌표 값이 유효하지 않습니다.");
         }
      },
      error: function(request, status, error) {
         console.log("code:" + request.status + "\nmessage:" + request.responseText + "\nerror:" + error);
      }
   });
}

// 도착지 마커 추가
function addDestinationMarker() {
   var destination_city_do = $("#destination_city_do").val();
   var destination_gu_gun = $("#destination_gu_gun").val();
   var destination_dong = $("#destination_dong").val();
   var destination_bunji = $("#destination_bunji").val();

   // 도착지 정보를 사용하여 백엔드에 요청
   $.ajax({
      method: "POST",
      url: "/geocode", // 백엔드의 API 엔드포인트 (도착지 좌표 요청)
      data: { city_do: destination_city_do, gu_gun: destination_gu_gun, dong: destination_dong, bunji: destination_bunji },
      success: function(response) {
         if (response.lat && response.lon) {
            console.log("도착지 좌표:", response.lat, response.lon);

            // 도착지 마커 추가
            var destinationLatLng = new Tmapv2.LatLng(Number(response.lat), Number(response.lon));
            marker2 = new Tmapv2.Marker({
               position: destinationLatLng,
               map: map
            });

            // 두 마커를 모두 포함하는 지도의 경계 설정
            adjustMapBounds(marker1.getPosition(), marker2.getPosition());
         } else {
            console.error("도착지 좌표 값이 유효하지 않습니다.");
         }
      },
      error: function(request, status, error) {
         console.log("code:" + request.status + "\nmessage:" + request.responseText + "\nerror:" + error);
      }
   });
}

// 두 마커를 모두 포함하도록 지도 영역을 조정하는 함수
function adjustMapBounds(startPosition, destinationPosition) {
   var bounds = new Tmapv2.LatLngBounds();
   bounds.extend(startPosition);
   bounds.extend(destinationPosition);
   map.fitBounds(bounds); // 지도가 두 좌표를 모두 포함할 수 있도록 줌 및 중앙 조정
}

// 페이지 로드 시 지도 및 출발지 초기화
$(document).ready(function() {
   initTmap(); // 지도 초기화
   $("#btn_select").click(findRoute); // 경로 찾기 버튼 클릭 시 findRoute 함수 실행
});
