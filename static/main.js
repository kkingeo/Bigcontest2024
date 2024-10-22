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

    // 출발지 값 가져오기
    var start_city = document.getElementById('start_city').value.trim();
    var start_gu = document.getElementById('start_gu').value.trim();
    var start_dong = document.getElementById('start_dong').value.trim();
    var start_bunji = document.getElementById('start_bunji').value.trim();
    
    // 도착지 값 가져오기
    var end_city = document.getElementById('end_city').value.trim();
    var end_gu = document.getElementById('end_gu').value.trim();
    var end_dong = document.getElementById('end_dong').value.trim();
    var end_bunji = document.getElementById('end_bunji').value.trim();

    // 필수 입력 체크
    if (!start_city || !start_gu || !start_dong || !end_city || !end_gu || !end_dong) {
        alert("모든 필수 입력 필드를 채워주세요.");
        return;
    }
    
    // URL 파라미터로 값을 넘김
    var url = "/routefinder?";
    url += "start_city=" + encodeURIComponent(start_city) + "&start_gu=" + encodeURIComponent(start_gu);
    url += "&start_dong=" + encodeURIComponent(start_dong) + "&start_bunji=" + encodeURIComponent(start_bunji);
    url += "&end_city=" + encodeURIComponent(end_city) + "&end_gu=" + encodeURIComponent(end_gu);
    url += "&end_dong=" + encodeURIComponent(end_dong) + "&end_bunji=" + encodeURIComponent(end_bunji);

    // 디버깅을 위한 로그
    console.log("Generated URL: ", url);

    // 새 페이지로 이동
    window.location.href = url;
}

