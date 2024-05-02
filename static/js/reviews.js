// reviews.js
document.addEventListener('DOMContentLoaded', () => {
    const reviewContainer = document.getElementById('reviewContainer');
    const paginationContainer = document.getElementById('paginationContainer');

    // Function to fetch reviews with pagination
    async function fetchReviews(pageNumber) {
        try {
            const response = await fetch(`/reviews/?page=${pageNumber}`);
            if (!response.ok) {
                throw new Error('Failed to fetch reviews');
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching reviews:', error);
            return { reviews: [], has_next: false, has_previous: false };
        }
    }

    // Function to render reviews
    function renderReviews(reviews) {
        reviewContainer.innerHTML = ''; // Clear existing reviews

        reviews.forEach(review => {
            // Create HTML elements for each review and append them to reviewContainer
            const reviewElement = document.createElement('div');
            // Populate reviewElement with review data
            reviewContainer.appendChild(reviewElement);
        });
    }

    // Function to render pagination controls
    function renderPaginationControls(paginationData) {
        paginationContainer.innerHTML = ''; // Clear existing pagination controls

        const { has_next, has_previous, next_page_number, previous_page_number, total_pages, current_page_number } = paginationData;

        // Render previous page button
        if (has_previous) {
            const prevButton = document.createElement('button');
            prevButton.textContent = 'Previous';
            prevButton.addEventListener('click', () => handlePaginationClick(previous_page_number));
            paginationContainer.appendChild(prevButton);
        }

        // Render page numbers
        for (let i = 1; i <= total_pages; i++) {
            const pageButton = document.createElement('button');
            pageButton.textContent = i;
            if (i === current_page_number) {
                pageButton.disabled = true;
            }
            pageButton.addEventListener('click', () => handlePaginationClick(i));
            paginationContainer.appendChild(pageButton);
        }

        // Render next page button
        if (has_next) {
            const nextButton = document.createElement('button');
            nextButton.textContent = 'Next';
            nextButton.addEventListener('click', () => handlePaginationClick(next_page_number));
            paginationContainer.appendChild(nextButton);
        }
    }

    // Function to handle pagination click event
    function handlePaginationClick(pageNumber) {
        fetchReviews(pageNumber)
            .then(data => {
                renderReviews(data.reviews);
                renderPaginationControls(data);
            })
            .catch(error => {
                console.error('Error fetching reviews:', error);
            });
    }

    // Fetch reviews for the first page when the page loads
    handlePaginationClick(1);
});
