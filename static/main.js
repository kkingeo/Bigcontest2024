function switchPlaces() {
    var startInput = document.getElementById('start');
    var destinationInput = document.getElementById('destination');
    var temp = startInput.value;
    startInput.value = destinationInput.value;
    destinationInput.value = temp;
}


