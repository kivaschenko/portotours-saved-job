document.addEventListener('DOMContentLoaded', function () {
    function updateURL() {
        let urlParams = new URLSearchParams(window.location.search);
        let tourType = document.getElementById('tour_type').value;
        let filterBy = document.getElementById('filter_by').value;
        let destination = document.getElementById('destination-slug').value;
        let time_of_day = document.getElementById('time_of_day').value;
        let duration = document.getElementById('duration').value;

        let hasChanged = false;

        if (time_of_day !== 'all') {
            urlParams.set('time_of_day', time_of_day);
            hasChanged = true;
        } else {
            urlParams.delete('time_of_day');
        }

        if (duration !== 'all') {
            urlParams.set('duration', duration);
        } else {
            urlParams.delete('duration');
        }

        if (tourType !== 'all') {
            urlParams.set('tour_type', tourType);
            hasChanged = true;
        } else {
            urlParams.delete('tour_type');
        }

        if (filterBy !== 'all') {
            urlParams.set('filter_by', filterBy);
            hasChanged = true;
        } else {
            urlParams.delete('filter_by');
        }

        if (destination !== 'all') {
            urlParams.set('destination', destination);
            hasChanged = true;
        } else {
            urlParams.delete('destination');
        }

        if (hasChanged) {
            window.history.replaceState(null, null, window.location.pathname + '?' + urlParams.toString());
        } else {
            window.history.replaceState(null, null, window.location.pathname);
        }

        window.location.reload();
    }

    document.getElementById('tour_type').addEventListener('change', updateURL);
    document.getElementById('filter_by').addEventListener('change', updateURL);
    document.getElementById('destination-slug').addEventListener('change', updateURL);
    document.getElementById('time_of_day').addEventListener('change', updateURL);
    document.getElementById('duration').addEventListener('change', updateURL);

    let urlParams = new URLSearchParams(window.location.search);
    let tourTypeValue = urlParams.get('tour_type') || 'all';
    let filterByValue = urlParams.get('filter_by') || 'all';
    let destinationSlug = urlParams.get('destination') || 'all';
    let timeOfDayValue = urlParams.get('time_of_day') || 'all';
    let durationValue = urlParams.get('duration') || 'all';

    document.getElementById('tour_type').value = tourTypeValue;
    document.getElementById('filter_by').value = filterByValue;
    document.getElementById('destination-slug').value = destinationSlug;
    document.getElementById('time_of_day').value = timeOfDayValue;
    document.getElementById('duration').value = durationValue;

    // Clean the URL if all parameters are default
    if (tourTypeValue === 'all' && filterByValue === 'all' && destinationSlug === 'all') {
        window.history.replaceState(null, null, window.location.pathname);
    }
});
