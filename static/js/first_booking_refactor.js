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
            this.createCalendarDay(prevMonthDay, true);
        }

        for (let i = 1; i <= totalDays; i++) {
            const currentDay = new Date(date.getFullYear(), date.getMonth(), i);
            this.createCalendarDay(currentDay);
        }

        calendarGrid.querySelectorAll('.calendar-day').forEach((day, index) => {
            const isoDate = calendarGrid.children[index].dataset.date; // Получаем дату из data-атрибута
            const eventsForDate = model.events.filter(event => event.date === isoDate); // Фильтруем события по дате
        
            if (eventsForDate.length > 0) {
                const minPrice = Math.min(...eventsForDate.map(event => event.adult_price)); // Находим минимальную цену
        
                // Проверяем, есть ли уже элемент цены в ячейке
                let priceElement = day.querySelector('.calendar-price');
                
                // Если элемента цены еще нет, создаем его
                if (!priceElement) {
                    priceElement = document.createElement('span');
                    priceElement.classList.add('calendar-price'); // Добавляем класс для цены
                    day.appendChild(priceElement); // Добавляем элемент цены к дню календаря
                }
                
                // Обновляем содержимое элемента цены, если новая цена меньше
                if (!priceElement.textContent || minPrice < parseFloat(priceElement.textContent.slice(1))) {
                    priceElement.textContent = `€${minPrice}`;
                }
            }
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
            // Create a key for the date in ISO format
            const isoDate = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate())).toISOString();
            // Filter events for the current date
            const eventsForDate = model.events.filter(event => event.date === isoDate.split('T')[0]);
            
            // If there are events for the current date, add them to the day element
            if (eventsForDate.length > 0) {
                eventsForDate.forEach(event => {
                    // Create a span element to display the price
                    let priceElement = document.createElement('span');
                    priceElement.textContent = `€${event.adult_price}`;
                    // Append the price element to the day element
                    dayElement.appendChild(priceElement);
                    console.log(dayElement)
                });
            }
            dayElement.dataset.date = isoDate.split('T')[0];
        }
        dayElement.textContent = date.getDate();
        calendarGrid.appendChild(dayElement);
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
