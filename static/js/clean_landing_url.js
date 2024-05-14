document.addEventListener('DOMContentLoaded', function () {
    function updateURL() {
        let urlParams = new URLSearchParams(window.location.search);
        let tourType = document.getElementById('tour_type').value;
        let filterBy = document.getElementById('filter_by').value;
        let destination = document.getElementById('destination-slug').value;

        let hasChanged = false;
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

    let urlParams = new URLSearchParams(window.location.search);
    let tourTypeValue = urlParams.get('tour_type') || 'all';
    let filterByValue = urlParams.get('filter_by') || 'all';
    let destinationSlug = urlParams.get('destination') || 'all';

    document.getElementById('tour_type').value = tourTypeValue;
    document.getElementById('filter_by').value = filterByValue;
    document.getElementById('destination-slug').value = destinationSlug;

    // Clean the URL if all parameters are default
    if (tourTypeValue === 'all' && filterByValue === 'all' && destinationSlug === 'all') {
        window.history.replaceState(null, null, window.location.pathname);
    }
});
