function switchPlaces() {
    var startInput = document.getElementById('start');
    var destinationInput = document.getElementById('destination');
    var temp = startInput.value;
    startInput.value = destinationInput.value;
    destinationInput.value = temp;
}

function submitForm(event) {
    // 기본 동작을 막아서 페이지 리로드 방지
    event.preventDefault();

    // 출발지와 도착지 주소 가져오기
    var start_address = document.getElementById("start_address").value;
    var end_address = document.getElementById("end_address").value;

    // URL 파라미터로 값을 넘김
    var url = "/routefinder?";
    url += "start_address=" + encodeURIComponent(start_address);
    url += "&end_address=" + encodeURIComponent(end_address);

    // 페이지 이동
    window.location.href = url;
}
