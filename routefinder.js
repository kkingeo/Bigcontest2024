var map, marker1;

// URL에서 파라미터 값을 추출하는 함수
function getQueryParams() {
   var params = new URLSearchParams(window.location.search);
 
   // 출발지 정보
   var start_city_do = params.get("start_city_do");
   var start_gu_gun = params.get("start_gu_gun");
   var start_dong = params.get("start_dong");
   var start_bunji = params.get("start_bunji");
 
   // 입력된 값들로 필드를 채움
   document.getElementById("city_do").value = start_city_do || "서울시";
   document.getElementById("gu_gun").value = start_gu_gun || "마포구";
   document.getElementById("dong").value = start_dong || "서교동";
   document.getElementById("bunji").value = start_bunji || "1";
 
   // 주소 기반 좌표를 반환 (여기서는 임의의 기본 좌표를 사용 중)
   // 실제로는 서버로 좌표 요청을 해야 합니다.
   var lat = 37.56520450;  // 기본 위도 (서울시청)
   var lon = 126.98702028; // 기본 경도
 
   // 서버에서 받은 좌표로 설정 (이 부분은 실제 주소 변환 API로 변경 가능)
   if (start_city_do && start_gu_gun && start_dong && start_bunji) {
     // 여기서는 변환 API가 없으므로, 실제 좌표 변환을 서버에서 해야 함.
     console.log("입력된 출발지: ", start_city_do, start_gu_gun, start_dong, start_bunji);
     // 지도에 입력한 주소를 좌표로 변환하여 적용해야 합니다.
     // 예시로 서울시청 좌표를 사용하고 있지만, 여기서 변환된 좌표를 적용하면 됩니다.
   }
 
   return { lat, lon };
 }

 // Tmap 지도 초기화
 function initTmap() {
   var coords = getQueryParams(); // URL 파라미터로 받은 좌표
   
   map = new Tmapv2.Map("map_div", {
      center: new Tmapv2.LatLng(37.56520450, 126.98702028), // 초기 지도 중심 좌표
      width: "100%",
      height: "100%",
      zoom: 17,
      zoomControl: true,
      scrollwheel: true
   });
   marker1 = new Tmapv2.Marker({
      icon: "/upload/tmap/marker/pin_b_m_a.png",
      iconSize: new Tmapv2.Size(24, 38),
      map: map
   });
 }

// 문서 준비가 완료되면 실행
$(document).ready(function() {
   $("#btn_select").click(function() {
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
               // 기존 마커 삭제
               marker1.setMap(null);
               // 응답받은 좌표를 기반으로 새로운 마커 추가
               var markerPosition = new Tmapv2.LatLng(Number(response.lat), Number(response.lon));
               marker1 = new Tmapv2.Marker({
                  position: markerPosition,
                  icon: "/upload/tmap/marker/pin_b_m_a.png",
                  iconSize: new Tmapv2.Size(24, 38),
                  map: map
               });
               map.setCenter(markerPosition); // 지도 중심을 새로운 좌표로 이동
            }
         },
         error: function(request, status, error) {
            console.log("code:" + request.status + "\nmessage:" + request.responseText + "\nerror:" + error);
         }
      });
   });
});
