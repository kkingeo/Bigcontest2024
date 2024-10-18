<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>simpleMap</title>
<script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>
<script src="https://apis.openapi.sk.com/tmap/jsv2?version=1&appKey=YOUR_APP_KEY"></script> <!-- Tmap API 사용 -->
<script type="text/javascript">
   var map, marker1;

   function initTmap() {
      map = new Tmapv2.Map("map_div", {
         center : new Tmapv2.LatLng(37.56520450, 126.98702028),  // 초기 지도 중심 좌표
         width : "100%",
         height : "400px",
         zoom : 17,
         zoomControl : true,
         scrollwheel : true
      });
      marker1 = new Tmapv2.Marker({
         icon : "/upload/tmap/marker/pin_b_m_a.png",
         iconSize : new Tmapv2.Size(24, 38),
         map : map
      });
   }

   $(document).ready(function() {
      $("#btn_select").click(function() {
         var city_do = $("#city_do").val();
         var gu_gun = $("#gu_gun").val();
         var dong = $("#dong").val();
         var bunji = $('#bunji').val();

         // 백엔드로 요청을 보냄
         $.ajax({
            method: "POST",
            url: "/geocode",  // 백엔드의 API 엔드포인트
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
                  map.setCenter(markerPosition);  // 지도 중심을 새로운 좌표로 이동
               }
            },
            error: function(request, status, error) {
               console.log("code:" + request.status + "\nmessage:" + request.responseText + "\nerror:" + error);
            }
         });
      });
   });
</script>
</head>
<body onload="initTmap();">
   <select id="city_do">
      <option value="서울시" selected="selected">서울시</option>
   </select>
   <select id="gu_gun">
      <option value="마포구" selected="selected">마포구</option>
      <option value="서대문구">서대문구</option>
   </select>
   <select id="dong">
      <option value="서교동" selected="selected">서교동</option>
   </select>
   <input type="text" id="bunji" name="bunji" value="1">
   <button id="btn_select">적용하기</button>
   <div id="map_div"></div>
</body>
</html>
