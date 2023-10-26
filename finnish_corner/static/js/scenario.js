$(document).ready(function() {
    $('#startChatButton').on('click', function() {
        var selectedScenarioId = $('#scenarioDropdown').val();
        
        if (selectedScenarioId) {
            window.location.href = `/app/?scenario_id=${selectedScenarioId}`;
        } else {
            alert('Please select a scenario before starting the chat.');
        }
    });
});

function getParameterByName(name, url = window.location.href) {
    name = name.replace(/[\[\]]/g, '\\$&');
    var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
}

// You may add other functions here related to handling chat messages and interactions
