var map, marker1;

// Tmap 지도 초기화
function initTmap() {
   map = new Tmapv2.Map("map_div", {
      center: new Tmapv2.LatLng(37.56520450, 126.98702028), // 초기 지도 중심 좌표
      width: "100%",
      height: "400px",
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
