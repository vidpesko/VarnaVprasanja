// ! Endless scroll
// var waypoint = new Waypoint({
//     element: document.getElementById('questions'),
//     handler: function (d) {
//         console.log('Basic waypoint triggered' + d)
//     }
// })

var infinite = new Waypoint.Infinite({
    element: $('#questions'),
    onAfterPageLoad: function() {
        var questions = $('#questions')[0].childElementCount;
        var counter = $('#questions-count')[0];
        counter.innerHTML = questions;
    }
})