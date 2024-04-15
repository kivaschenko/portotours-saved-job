document.getElementById("subscription-form").addEventListener("submit", function (event) {
    event.preventDefault();
    fetch(event.target.action, {
        method: 'POST',
        body: new FormData(event.target),
        headers: {
            'X-CSRFToken': '{{ csrf_token }}'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show the popup message
                document.querySelector('.subscribe-popup').style.display = 'block';
            } else {
                // Handle error if needed
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
});

// Add event listener to the "Continue" button to hide the popup
document.getElementById("continue-btn").addEventListener("click", function (event) {
    event.preventDefault();
    document.querySelector('.subscribe-popup').style.display = 'none';
});

// Add event listener to hide the popup after some time (e.g., 5 seconds)
setTimeout(function () {
    document.querySelector('.subscribe-popup').style.display = 'none';
}, 5000); // Adjust the time as needed (in milliseconds)
