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
         end_address: endAddress  // 도착지 주소
      },
      success: function(response) {
         if (response && response.plan && response.plan.itineraries && response.plan.itineraries.length > 0) {
            console.log("Route response received:", response);  // 디버깅 로그 추가
             
             // 경로 선택 UI 생성
            var routeSelectionDiv = document.getElementById('routeSelection');
            routeSelectionDiv.innerHTML = '';  // 이전 내용 제거
             
             // 경로 리스트 생성
            response.plan.itineraries.forEach(function(itinerary, index) {
               // 경로 요약 정보를 표시할 요소 생성 (예: 총 시간, 요금)
               var routeSummary = document.createElement('div');
               routeSummary.innerHTML = "경로 " + (index + 1) + ": 총 시간 - " + itinerary.totalTime + "초, 요금 - " + itinerary.fare.regular.totalFare + "원";
                 
                 // 경로 선택 버튼 생성
               var routeButton = document.createElement('button');
               routeButton.innerHTML = "이 경로 선택";
               routeButton.onclick = function() {
                  drawRoute(itinerary.legs);  // 경로의 세부 단계를 그리는 함수
                  processCongestionData(itinerary.legs);  // 혼잡도 데이터 처리
               };
                 
                 // UI에 추가
               routeSelectionDiv.appendChild(routeSummary);
               routeSelectionDiv.appendChild(routeButton);
            });
         }
      },
      error: function(error) {
         console.error("경로 찾기 실패", error);
      }
   });
   console.log("start_address:", startAddress, "end_address:", endAddress);
}

function drawRoute(legs) {
   // 각 단계별로 경로를 그리는 로직
   legs.forEach(function(leg) {
      if (leg.mode === 'WALK') {
           // 도보 경로 그리기
         console.log("도보 경로 그리기:", leg.steps);
           // 도보 경로에 대한 로직 추가 (지도 API 등 활용)
      } else if (leg.mode === 'SUBWAY') {
           // 지하철 경로 그리기
         console.log("지하철 경로 그리기:", leg.passStopList.stationList);
           // 지하철 경로에 대한 로직 추가 (지도 API 등 활용)
      }
       // 필요한 추가 모드 처리
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

   });
}


// 받은 경로 데이터를 이 함수로 전달하여 지도에 경로 그리기
function handleRouteData(response) {
   const routes = response.routes;
   routes.forEach(route => {
       drawRoute(route);
   });
}


function processCongestionData(legs) {
   legs.forEach(function(leg) {
       // 혼잡도 관련 데이터가 있다면 처리
       if (leg.mode === 'SUBWAY' && leg.passStopList) {
           leg.passStopList.stationList.forEach(function(station) {
               console.log("지하철역 혼잡도 처리:", station.stationName);
               // 혼잡도 데이터 처리 로직 추가
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

