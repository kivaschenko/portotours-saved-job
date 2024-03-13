const model = {};  // The JSON data about all allowed events will be seeded here after page loading

// The view object has functions that are responsible for changing the data in certain html blocks
const view = {
    seedDataToForm: function () {
        let form = document.getElementById("bookingForm");
    },

    showTimesAndPlaces: function (date) {
        console.log('Got date:', date);
    },

    grabCurrentBookingData: function () {
        let form = document.getElementById("bookingForm");
    }
};

// The controller has functions that respond to events in HTML blocks, forms, buttons
const controller = {
    handleSubmit: function (e) {
        // Do something with data of form
    }
};

// Function to fetch JSON data using AJAX
function fetchEventData(parentExperienceId) {
    // Make an AJAX request to your Django view
    fetch(`/actual-experience-events/${parentExperienceId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Call function to handle the received data
            handleEventData(data.result);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

// Function to handle the received JSON data
function handleEventData(data) {
    console.log('Got data from response:', data);
    // Check if data contains 'languages' and 'events' keys
    if (data.hasOwnProperty('languages') && data.hasOwnProperty('events')) {
        // Your logic to save the data into your model object
        // Example: Assuming 'model' is your model object defined earlier
        model.languages = data.languages;
        model.events = data.events;

        // Example: Log the updated model object
        console.log('Updated model:', model);
    } else {
        console.error('Received data format is invalid');
    }
}


document.addEventListener('DOMContentLoaded', function () {
    const prevMonthBtn = document.getElementById('prevMonth');
    const nextMonthBtn = document.getElementById('nextMonth');
    const currentMonthDisplay = document.getElementById('currentMonth');
    const calendarGrid = document.getElementById('calendarGrid');
    const ticketCounts = document.querySelectorAll('.ticket-count');
    const totalPriceDisplays = document.querySelectorAll('.total-price');
    const submitBtn = document.getElementById('submitBtn');
    let selectedDate = null;
    let currentDate = new Date();

    fetchEventData(parentExperienceId);
    
    renderCalendar(currentDate);

    prevMonthBtn.addEventListener('click', function () {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar(currentDate);
    });

    nextMonthBtn.addEventListener('click', function () {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar(currentDate);
    });

    calendarGrid.addEventListener('click', function (event) {
        if (event.target.classList.contains('inactive')) return;
        const selectedDay = event.target.dataset.date;
        selectedDate = new Date(selectedDay);
        updateSelectedDate(selectedDate);
    });

    function renderCalendar(date) {
        calendarGrid.innerHTML = '';
        currentMonthDisplay.textContent = getMonthYearString(date);

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
    }

    function createCalendarDay(date, inactive = false) {
        const dayElement = document.createElement('div');
        dayElement.classList.add('calendar-day');
        if (inactive) {
            dayElement.classList.add('inactive');
        } else {
            // Создаем дату без учета часового пояса
            const isoDate = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate())).toISOString();
            dayElement.dataset.date = isoDate;
        }
        dayElement.textContent = date.getDate();
        calendarGrid.appendChild(dayElement);
    }

    function getMonthYearString(date) {
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
        const month = monthNames[date.getMonth()];
        const year = date.getFullYear();
        return `${month} ${year}`;
    }

    calendarGrid.addEventListener('click', function (event) {
        if (event.target.classList.contains('inactive')) return;
        const selectedDay = event.target.dataset.date;
        selectedDate = new Date(selectedDay);
        updateSelectedDate(selectedDate);
    });


    // Функция обработки клика по дате
    function handleDateClick(event) {
        const clickedDateElement = event.target;
        const clickedDate = clickedDateElement.dataset.date;
        if (clickedDate) {
            // Удаляем класс у всех дат календаря
            calendarGrid.querySelectorAll('.calendar-day').forEach(day => {
                day.classList.remove('selected-date');
            });
            // Подсвечиваем выбранную дату
            clickedDateElement.classList.add('selected-date');
        }
    }

    // Добавляем обработчик клика к календарю
    calendarGrid.addEventListener('click', handleDateClick);

    // Определение сегодняшней даты
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const todayString = `${year}-${month}-${day}T00:00:00.000Z`;

    // Находим ячейку календаря для сегодняшней даты
    const todayCell = calendarGrid.querySelector(`[data-date="${todayString}"]`);


    // Если нашли ячейку, делаем ее активной
    if (todayCell) {
        todayCell.classList.add('selected-date');
        selectedDate = todayCell;
    }

    // Функция обновления выбранной даты
    function updateSelectedDate(date) {
        const formattedDate = date.toLocaleDateString('default', {weekday: 'long', month: 'long', day: 'numeric'});
        console.log('Выбрана дата:', formattedDate);

        // Дополнительные действия при выборе даты, например, обновление цены тура
        // Под каждой датой в календаре должна быть указана цена тура ($100)
        const tourPrice = 100;
        const priceElement = document.createElement('span');
        priceElement.textContent = `€${tourPrice}`;
        event.target.appendChild(priceElement);
    }

    function updateSelectedDate(date) {
        const formattedDate = date.toLocaleDateString('default', {weekday: 'long', month: 'long', day: 'numeric'});
        ticketCounts.forEach(count => count.value = 0);
        totalPriceDisplays.forEach(display => display.textContent = '$0');
        submitBtn.textContent = `add to cart`;
        selectedDate = date;
    }

    document.querySelectorAll('.increment').forEach(button => {
        button.addEventListener('click', function () {
            const ticketCount = this.previousElementSibling;
            const priceDisplay = this.nextElementSibling.nextElementSibling;
            let count = parseInt(ticketCount.value);
            count++;
            ticketCount.value = count;
            updateTotalPrice();
        });
    });

    document.querySelectorAll('.decrement').forEach(button => {
        button.addEventListener('click', function () {
            const ticketCount = this.nextElementSibling;
            const priceDisplay = this.nextElementSibling.nextElementSibling;
            let count = parseInt(ticketCount.value);
            if (count > 0) {
                count--;
                ticketCount.value = count;
                updateTotalPrice();
            }
        });
    });

    function updateTotalPrice() {
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

    submitBtn.addEventListener('click', function () {
        const totalPrice = parseInt(totalPriceDisplays[0].textContent.replace('$', ''));
        // Handle form submission here
    });
});


// open mobile form
let openMobileBookingFormBtn = document.querySelector('.mobile-form-btn')
let bookingForm = document.querySelector('.aside-form');
let htmlElement = document.documentElement;
let goBackBtn = document.querySelector('.btn-back');

openMobileBookingFormBtn.addEventListener('click', (e) => {
    e.preventDefault()
    bookingForm.classList.add('open-mobile');
    htmlElement.classList.add('off-scroll');
});
goBackBtn.addEventListener('click', () => {
    bookingForm.classList.remove('open-mobile');
    htmlElement.classList.remove('off-scroll');
})

