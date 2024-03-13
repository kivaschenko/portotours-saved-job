const model = {};  // The JSON data about all allowed events will be seeded here after page loading

// The view object has functions that are responsible for changing the data in certain HTML blocks
const view = {
    // Function implementation for seeding data to form, if needed
    seedDataToForm: function () {
        let form = document.getElementById("bookingForm");
    },

    // Check if model.languages exists and is an array before proceeding
    showOnlyAllowedLanguages: function () {
        if (model.languages && Array.isArray(model.languages)) {
            let allowedLanguages = model.languages;

            // Iterate over the allowed language codes
            allowedLanguages.forEach(langCode => {
                let inputId = "lang_" + langCode;
                let inputElement = document.getElementById(inputId);

                if (inputElement) {
                    inputElement.style.display = "block";
                }
            });
        } else {
            console.error("model.languages is either undefined or not an array");
        }
    },

    // Function to render the calendar
    renderCalendar: function (date) {
        const calendarGrid = document.getElementById('calendarGrid');
        const currentMonthDisplay = document.getElementById('currentMonth');
        const prevMonthBtn = document.getElementById('prevMonth');
        const nextMonthBtn = document.getElementById('nextMonth');

        calendarGrid.innerHTML = '';
        currentMonthDisplay.textContent = this.getMonthYearString(date);

        // Your calendar rendering logic here
        const today = new Date();
        if (date.getMonth() === today.getMonth() && date.getFullYear() === today.getFullYear()) {
            prevMonthBtn.disabled = true;
        } else {
            prevMonthBtn.disabled = false;
        }

        const firstDayOfMonth = new Date(date.getFullYear(), date.getMonth(), 1);
        const lastDayOfMonth = new Date(date.getFullYear(), date.getMonth() + 1, 0);
        const startingDay = firstDayOfMonth.getDay();
        const totalDays = lastDayOfMonth.getDate();


        for (let i = 0; i < startingDay; i++) {
            const prevMonthDay = new Date(date.getFullYear(), date.getMonth(), -startingDay + i + 1);
            createCalendarDay(prevMonthDay, true);
        }

        for (let i = 1; i <= totalDays; i++) {
            const currentDay = new Date(date.getFullYear(), date.getMonth(), i);
            createCalendarDay(currentDay);
        }

        const tourPrice = 100;
        calendarGrid.querySelectorAll('.calendar-day').forEach(day => {
            const priceElement = document.createElement('span');
            priceElement.textContent = `$${tourPrice}`;
            day.appendChild(priceElement);
        });

        // Example: Render the calendar days
        // this.createCalendarDays(date);
    },

    // Function to create calendar day
    createCalendarDay: function (date, inactive = false) {
        const dayElement = document.createElement('div');
        dayElement.classList.add('calendar-day');
        if (inactive) {
            dayElement.classList.add('inactive');
        } else {
            // Your logic to create calendar day element
            // ...

            // Example: Set dataset and textContent
            // dayElement.dataset.date = formattedDate;
            // dayElement.textContent = date.getDate();
        }
        // Append dayElement to calendar grid
        // calendarGrid.appendChild(dayElement);
    },

    // Function to get month and year string
    getMonthYearString: function (date) {
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
        const month = monthNames[date.getMonth()];
        const year = date.getFullYear();
        return `${month} ${year}`;
    }
};

// The controller has functions that respond to events in HTML blocks, forms, buttons
const controller = {
    handleSubmit: function (e) {
        // Do something with data of form
    },
    handleDecrementClick: function () {
        document.querySelectorAll('.decrement').forEach(button => {
            button.addEventListener('click', function () {
                const ticketCount = this.nextElementSibling;
                const priceDisplay = this.nextElementSibling.nextElementSibling;
                let count = parseInt(ticketCount.value);
                if (count > 0) {
                    count--;
                    ticketCount.value = count;
                    controller.updateTotalPrice();
                }
            });
        });
    },

    updateTotalPrice: function () {
        let totalAdultTickets = 0;
        let totalChildTickets = 0;

        ticketCounts.forEach((count, index) => {
            const ticketType = index % 2 === 0 ? 'adult' : 'child';
            const ticketPrice = ticketType === 'adult' ? 100 : 50; // Цена для взрослых $100, для детей $50
            const ticketTotalPrice = parseInt(count.value) * ticketPrice;

            if (ticketType === 'adult') {
                totalAdultTickets += ticketTotalPrice;
            } else {
                totalChildTickets += ticketTotalPrice;
            }
        });

        totalPriceDisplays[0].textContent = `$${totalAdultTickets}`;
        totalPriceDisplays[1].textContent = `$${totalChildTickets}`;

        const totalPrice = totalAdultTickets + totalChildTickets;
        submitBtn.textContent = `${totalPrice} add to cart`;
    }
};

// Function to fetch JSON data using AJAX
async function fetchEventData(parentExperienceId) {
    try {
        const response = await fetch(`/actual-experience-events/${parentExperienceId}/`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        // Call function to handle the received data
        handleEventData(data.result);
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Function to handle the received JSON data
function handleEventData(data) {
    console.log('Got data from response:', data);
    if (data.hasOwnProperty('languages') && data.hasOwnProperty('events')) {
        model.languages = data.languages;
        model.events = data.events;
        console.log('Updated model:', model);
        view.showOnlyAllowedLanguages();
        // Show calendar
        const currentDate = new Date(); // Or you can pass the date from the controller
        view.renderCalendar(currentDate);
    } else {
        console.error('Received data format is invalid');
    }
}

document.addEventListener('DOMContentLoaded', async function () {
    // Fetch event data and wait for it to complete
    await fetchEventData(parentExperienceId);

    // Event listeners for prevMonthBtn, nextMonthBtn, etc. can be added here or in the controller
    // Call the handleDecrementClick function to add event listeners to decrement buttons
    controller.handleDecrementClick();
});


// open mobile form
const openMobileBookingFormBtn = document.querySelector('.mobile-form-btn');
const bookingForm = document.querySelector('.aside-form');
const htmlElement = document.documentElement;
const goBackBtn = document.querySelector('.btn-back');

openMobileBookingFormBtn.addEventListener('click', (e) => {
    e.preventDefault();
    bookingForm.classList.add('open-mobile');
    htmlElement.classList.add('off-scroll');
});

goBackBtn.addEventListener('click', () => {
    bookingForm.classList.remove('open-mobile');
    htmlElement.classList.remove('off-scroll');
});
