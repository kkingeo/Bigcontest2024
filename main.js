function switchPlaces() {
    var startInput = document.getElementById('start');
    var destinationInput = document.getElementById('destination');
    var temp = startInput.value;
    startInput.value = destinationInput.value;
    destinationInput.value = temp;
}

function submitForm() {
    // 출발지 정보
    var start_city_do = document.getElementById("start_city_do").value;
    var start_gu_gun = document.getElementById("start_gu_gun").value;
    var start_dong = document.getElementById("start_dong").value;
    var start_bunji = document.getElementById("start_bunji").value;
  
    // 도착지 정보
    var destination_city_do = document.getElementById("destination_city_do").value;
    var destination_gu_gun = document.getElementById("destination_gu_gun").value;
    var destination_dong = document.getElementById("destination_dong").value;
    var destination_bunji = document.getElementById("destination_bunji").value;
  
    // URL 파라미터로 값을 넘김
    var url = "routefinder.html?";
    url += "start_city_do=" + start_city_do + "&start_gu_gun=" + start_gu_gun + "&start_dong=" + start_dong + "&start_bunji=" + start_bunji;
    url += "&destination_city_do=" + destination_city_do + "&destination_gu_gun=" + destination_gu_gun + "&destination_dong=" + destination_dong + "&destination_bunji=" + destination_bunji;
  
    window.location.href = url;
  }