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
    function renderReviews(reviewsData) {
        const reviewsList = document.getElementById('reviewsList');
        reviewsList.innerHTML = ''; // Clear existing reviews
        console.log('Got reviews data: ', reviewsData);
        reviewsData.forEach(review => {
            // Create HTML elements for each review and append them to reviewsList
            const reviewItem = document.createElement('li');
            reviewItem.classList.add('reviews-list-item');
            const starsWrapper = document.createElement('div');
            starsWrapper.classList.add('review-stars-wrapper');
            starsWrapper.classList.add(`star-${review.rating}`);
            starsWrapper.innerHTML = `
                <img class="star3" src="{% static 'icons/3-stars-icon.svg' %}" alt="3 start review">
                <img class="star4" src="{% static 'icons/4-stars-icon.svg' %}" alt="4 start review">
                <img class="star5" src="{% static 'icons/5-stars-icon.svg' %}" alt="5 start review">
            `;
            const reviewTitle = document.createElement('h4');
            reviewTitle.classList.add('review-title');
            reviewTitle.textContent = review.title;
            const reviewText = document.createElement('p');
            reviewText.classList.add('review-text');
            reviewText.textContent = review.short_text;
            const reviewAuthor = document.createElement('p');
            reviewAuthor.classList.add('review-author');
            reviewAuthor.textContent = review.full_name;

            // Append elements to reviewItem
            reviewItem.appendChild(starsWrapper);
            reviewItem.appendChild(reviewTitle);
            reviewItem.appendChild(reviewText);
            reviewItem.appendChild(reviewAuthor);

            // Append reviewItem to reviewsList
            reviewsList.appendChild(reviewItem);
        });
    }

    // Function to render reviews
    // function renderReviews(reviews) {
    //     reviewContainer.innerHTML = ''; // Clear existing reviews
    //     console.log('Got data.reviews: ', reviews);
    //     reviews.forEach(review => {
    //         // Create HTML elements for each review
    //         const reviewElement = document.createElement('div');
    //         const ratingElement = document.createElement('p');
    //         const titleElement = document.createElement('h4');
    //         const shortTextElement = document.createElement('p');
    //         const fullNameElement = document.createElement('p');
    //
    //         // Populate reviewElement with review data
    //         ratingElement.textContent = `Rating: ${review.rating}`;
    //         titleElement.textContent = review.title;
    //         shortTextElement.textContent = review.short_text;
    //         fullNameElement.textContent = `Full Name: ${review.full_name}`;
    //
    //         // Append elements to reviewElement
    //         reviewElement.appendChild(ratingElement);
    //         reviewElement.appendChild(titleElement);
    //         reviewElement.appendChild(shortTextElement);
    //         reviewElement.appendChild(fullNameElement);
    //
    //         // Append reviewElement to reviewContainer
    //         reviewContainer.appendChild(reviewElement);
    //     });
    // }

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
