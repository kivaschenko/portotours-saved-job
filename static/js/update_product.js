const model = {
    // The JSON data about all allowed events will be seeded here after page loading
    'languages': [],
    'events': [],
    'bookingData': {
        'adults': 0,
        'children': 0,
        'language_code': null,
        'event_id': null,
        'product_id': productId, // from page scope
        'options': optionExtras,  // from page scope
    },
    'selectedDate': null,
    'current_event': {},
    'current_product': {
        'adultCount': adultCount,
        'childCount': childCount,
        'adultPrice': adultPrice,
        'childPrice': childPrice,
        'startDate': startDate,
        'startTime': startTime,
        'totalPrice': totalPrice,
        'language': languageProduct,
    },
    'productId': productId,
};

// The view object has functions that are responsible for changing the data in certain HTML blocks
const view = {
    // Function implementation for seeding data to form, if needed
    seedDataToForm: function () {
        const productData = model.current_product;

        const startTime = productData.startTime;
        const input = document.querySelector('input[type="radio"][value="' + startTime + '"]');
        const startLanguage = productData.language
        const languageInput = document.querySelector('input[type="radio"][value="' + startLanguage + '"]')
        const totalPrice = productData.totalPrice
        const totalPriceTextBlock = document.querySelector('.total-price-wrapper span')
        // const totalPriceExtrasTextBlock = document.querySelector('.total-price-extras-wrapper span')
        totalPriceTextBlock.innerHTML = `${totalPrice}`
        // totalPriceExtrasTextBlock.innerHTML = `${totalPrice}`

        // Enable the input if found
        if (input) {
            input.checked = true;
        } else {
            console.error('Input not found for the given start time:', startTime);
        }

        // Enable starting language if found 
        if (languageInput) {
            languageInput.checked = true;
        } else {
            console.error('Input not found for the given start language:', startLanguage);
        }

        document.getElementById('adultTicketCount').value = productData.adultCount;
        document.getElementById('childTicketCount').value = productData.childCount;
        const adultTotalPrice = productData.adultCount * productData.adultPrice;
        const childTotalPrice = productData.childCount * productData.childPrice;
        document.getElementById('childTotalPrice').textContent = '€' + childTotalPrice.toFixed(2);
        document.getElementById("adultTotalPrice").textContent = '€' + adultTotalPrice.toFixed(2);

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
        const selectedDate = model.selectedDate;
        calendarGrid.innerHTML = '';
        currentMonthDisplay.textContent = this.getMonthYearString(date);

        // Your calendar rendering logic here
        const today = new Date();
        if (date.getMonth() === today.getMonth() && date.getFullYear() === today.getFullYear()) {
            prevMonthBtn.disabled = true;
        } else {
            prevMonthBtn.disabled = false;
        }

        prevMonthBtn.addEventListener('click', function () {
            const prevMonth = new Date(date.getFullYear(), date.getMonth() - 1, 1);
            view.renderCalendar(prevMonth);
            if (selectedDate) {
                const selectedDateElement = calendarGrid.querySelector(`[data-date="${selectedDate}"]`);
                if (selectedDateElement) {
                    selectedDateElement.classList.add('selected-date');
                }
            }
        });

        // Event listener for next month button
        nextMonthBtn.addEventListener('click', function () {
            const nextMonth = new Date(date.getFullYear(), date.getMonth() + 1, 1);
            view.renderCalendar(nextMonth);
            if (selectedDate) {
                const selectedDateElement = calendarGrid.querySelector(`[data-date="${selectedDate}"]`);
                if (selectedDateElement) {
                    selectedDateElement.classList.add('selected-date');
                }
            }
        });

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
            const isoDate = calendarGrid.children[index].dataset.date;
            const eventsForDate = model.events.filter(event => event.date === isoDate);

            if (eventsForDate.length > 0) {
                const minPrice = Math.min(...eventsForDate.map(event => event.adult_price));

                let priceElement = day.querySelector('.calendar-price');

                if (!priceElement) {
                    priceElement = document.createElement('span');
                    priceElement.classList.add('calendar-price');
                    day.appendChild(priceElement);
                }

                if (!priceElement.textContent || minPrice < parseFloat(priceElement.textContent.slice(1))) {
                    priceElement.textContent = `€${minPrice}`;
                }
            }
        });
        // Event listener to handle click on a date cell
        calendarGrid.addEventListener('click', controller.handleDateClick);
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
                });
            }
            dayElement.dataset.date = isoDate.split('T')[0];
        }
        dayElement.textContent = date.getDate();
        // Append dayElement to calendar grid
        calendarGrid.appendChild(dayElement);
    },

    // Function to get month and year string
    getMonthYearString: function (date) {
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
        const month = monthNames[date.getMonth()];
        const year = date.getFullYear();
        return `${month} ${year}`;
    },

    // Function to update total price display
    updateTotalPriceDisplay: function (totalAdultPrice, totalChildPrice) {
        const adultTotalPriceElement = document.getElementById('adultTotalPrice');
        const childTotalPriceElement = document.getElementById('childTotalPrice');

        if (adultTotalPriceElement && childTotalPriceElement) {
            adultTotalPriceElement.textContent = `€${totalAdultPrice.toFixed(2)}`;
            childTotalPriceElement.textContent = `€${totalChildPrice.toFixed(2)}`;
        }
    },

    // Function to update the quantity display for an option
    updateOptionQuantityDisplay: function (optionId, quantity) {
        const input = document.getElementById(`option_${optionId}`);
        if (input) {
            input.value = quantity;
        }
    },

    // First seed for options from model
    seedOptionData: function () {
        model.bookingData.options.forEach(item => {
            console.log(item);
            this.updateOptionQuantityDisplay(item.id, item.quantity);
        })
    }

};

// The controller has functions that respond to events in HTML blocks, forms, buttons
const controller = {
    getTotalParticipants: function () {
        const adultCount = parseInt(document.getElementById('adultTicketCount').value);
        const childCount = parseInt(document.getElementById('childTicketCount').value);
        return adultCount + childCount;
    },

    validateParticipantLimits: function () {
        const selectedEvent = model.events.find(event => event.date === model.selectedDate);
        const totalParticipants = controller.getTotalParticipants();
        return totalParticipants <= selectedEvent.remaining_participants;

    },

    validateOptionLimits: function () {
        for (const option of model.bookingData.options) {
            const optionElement = document.getElementById(`option_${option.id}`);
            if (parseInt(optionElement.value) > option.max_quantity) {
                return false;
            }
        }
        return true;
    },

    // Function to handle form submission
    handleFormSubmit: async function () {
        if (!controller.validateParticipantLimits() || !controller.validateOptionLimits()) {
            return;
        }
        // Get the booking data from the model
        const bookingData = model.bookingData;

        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

        try {
            // Send the booking data to the server using fetch or another AJAX method
            const response = await fetch('/update-group-product-without-booking/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify(bookingData)
            });

            // Check if response is successful
            if (response.ok) {
                // Handle successful response
                console.log('Update Booking submitted successfully.');
                const languageSlug = model.bookingData.language_code.toLowerCase();

                // Redirect to the cart page after successful submission
                window.location.href = `/my-cart/${languageSlug}/`; // Replace '/my-cart/' with the URL of your cart page
            } else {
                // Handle error response
                console.error('Error submitting update of booking:', response.statusText);
            }
        } catch (error) {
            console.error('Error submitting update of booking:', error);
        }
    },
    handleTicketsIncrementDecrement: function () {
        document.querySelectorAll('.increment, .decrement').forEach(button => {
            button.addEventListener('click', (event) => {
                const button = event.currentTarget; // Ensure we get the button element itself
                const increment = button.classList.contains('increment') ? 1 : -1;
                const input = button.closest('.ticket-type').querySelector('.ticket-count');
                input.value = Math.max(0, parseInt(input.value) + increment);
                if (!controller.validateParticipantLimits()) {
                    input.value = Math.max(0, parseInt(input.value) - increment);
                } else {
                    controller.updateTotalPrice();
                    controller.performValidation();
                }
            });
        });
    },
    handleOptionIncrementDecrement: function () {
        document.querySelectorAll('.btn-increment, .btn-decrement').forEach(button => {
            button.addEventListener('click', event => {
                const button = event.currentTarget;
                const input = button.closest('.input-block').querySelector('input');
                const optionId = parseInt(input.id.replace('option_', ''));
                const option = model.bookingData.options.find(opt => opt.id === optionId);
                const increment = button.classList.contains('btn-increment') ? 1 : -1;
                // Ensure the input value is updated correctly first
                const newValue = Math.max(0, parseInt(input.value) + increment);
                // Ensure the input value does not exceed the max quantity
                if (newValue > option.max_quantity) {
                    input.value = option.max_quantity;
                } else {
                    input.value = newValue;
                }
                // Update the option quantity in the model
                option.quantity = parseInt(input.value);

                // Update the display price for the option
                const priceElement = document.getElementById(`option_price_${optionId}`);
                if (priceElement) {
                    if (option.price > 0) {
                        priceElement.innerHTML = `€${(option.price * option.quantity).toFixed(2)}`;
                    } else {
                        priceElement.innerHTML = 'FREE';
                    }
                }
                controller.updateTotalPrice();
            });
        });
    },

    handleTimeSelection: function () {
        document.querySelectorAll('time-selection input[type="radio"]').forEach(input => {
            input.addEventListener('change', function () {
                controller.performValidation();
                const selectedDate = document.querySelector('.calendar-day.selected-date');
                if (selectedDate) {
                    controller.updateTotalPrice(selectedDate.dataset.date, this.value);
                }
            })
        })
    },

    updateTotalPrice: function () {
        // Find the selected date and time
        const selectedDateElement = document.querySelector('.calendar-day.selected-date');
        const selectedTimeInput = document.querySelector('input[name="time"]:checked');

        if (selectedDateElement && selectedTimeInput) {
            const selectedDate = selectedDateElement.dataset.date;
            const selectedTime = selectedTimeInput.value;

            // Find the event matching the selected date and time
            const selectedEvent = model.events.find(event => event.date === selectedDate && event.time === selectedTime);

            if (selectedEvent) {
                const adultPrice = selectedEvent.adult_price;
                const childPrice = selectedEvent.child_price;

                // Get adult and child counts using IDs
                const adultCount = parseInt(document.getElementById('adultTicketCount').value);
                const childCount = parseInt(document.getElementById('childTicketCount').value);

                // Update total prices display
                const totalAdultPrice = adultPrice * adultCount;
                const totalChildPrice = childPrice * childCount;

                // Update the total prices directly next to the clickers
                const adultTotalPriceElement = document.getElementById('adultTotalPrice');
                const childTotalPriceElement = document.getElementById('childTotalPrice');
                if (adultTotalPriceElement && childTotalPriceElement) {
                    adultTotalPriceElement.textContent = `€${totalAdultPrice.toFixed(2)}`;
                    childTotalPriceElement.textContent = `€${totalChildPrice.toFixed(2)}`;
                }

                // Update submit button text
                const totalPrice = totalAdultPrice + totalChildPrice;
                submitBtn.textContent = `Save`;
                let totalPriceText = document.querySelector('.total-price-wrapper span')
                totalPriceText.innerHTML = `${totalPrice.toFixed(2)}`
            } else {
                console.error('Selected event not found.');
            }
        }
    },

    resetPricesAndButton: function () {
        document.getElementById('adultTotalPrice').textContent = '€0';
        document.getElementById('childTotalPrice').textContent = '€0';
        document.querySelector('.total-price-wrapper span').innerHTML = '0'
        submitBtn.textContent = 'Save';
    },

    // Function to handle click on a date cell
    handleDateClick: function (event) {
        const clickedDateElement = event.target;
        const clickedDate = clickedDateElement.dataset.date;

        // Clear the time selection area
        const timeSelection = document.querySelector('.time-selection');
        timeSelection.innerHTML = '';

        if (clickedDate) {
            const eventsForDate = model.events.filter(event => event.date === clickedDate);
            eventsForDate.sort((a, b) => {
                return new Date('1970/01/01 ' + a.time) - new Date('1970/01/01 ' + b.time);
            });

            // Check if this is the second date selection
            if (document.querySelectorAll('.calendar-day.selected-date').length === 1) {
                controller.resetPricesAndButton(); // Reset prices and submit button text
            }

            // If there are events for the clicked date
            if (eventsForDate.length > 0) {
                // If there is only one event, automatically select its time slot
                if (eventsForDate.length === 1) {
                    // Create radio button for the only available time
                    const timeInput = document.createElement('input');
                    timeInput.type = 'radio';
                    timeInput.id = eventsForDate[0].experience_event_id; // Using event ID as radio button ID
                    timeInput.name = 'time'; // Ensure the radio buttons are part of the same group
                    timeInput.value = eventsForDate[0].time; // Assign the time value
                    timeInput.checked = true; // Automatically select this time slot

                    // Create label for the radio button
                    const timeLabel = document.createElement('label');
                    timeLabel.htmlFor = eventsForDate[0].experience_event_id;
                    timeLabel.textContent = eventsForDate[0].time;

                    // Append the radio button and label to the time selection area
                    timeSelection.appendChild(timeInput);
                    timeSelection.appendChild(timeLabel);
                } else {
                    // Create time selection options for each event
                    eventsForDate.forEach(event => {
                        // Create radio button for each time
                        const timeInput = document.createElement('input');
                        timeInput.type = 'radio';
                        timeInput.id = event.experience_event_id;
                        timeInput.name = 'time';
                        timeInput.value = event.time;

                        // Create label for the radio button
                        const timeLabel = document.createElement('label');
                        timeLabel.htmlFor = event.experience_event_id;
                        timeLabel.textContent = event.time;

                        // Append the radio button and label to the time selection area
                        timeSelection.appendChild(timeInput);
                        timeSelection.appendChild(timeLabel);

                        timeInput.addEventListener('change', function () {
                            controller.performValidation(); // Call validation function when radio button changes
                        });
                    });
                }
            } else {
                // If no events are available for the clicked date, display a message
                const noEventsMessage = document.createElement('p');
                noEventsMessage.textContent = 'No events available for this date.';
                timeSelection.appendChild(noEventsMessage);
            }

            // Highlight the selected date
            document.querySelectorAll('.calendar-day').forEach(day => {
                day.classList.remove('selected-date');
            });
            clickedDateElement.classList.add('selected-date');
            model.selectedDate = clickedDate;
        }
    },
    performValidation: function () {
        const selectedDateElement = document.querySelector('.calendar-day.selected-date');
        const selectedTimeInput = document.querySelector('input[name="time"]:checked');
        const adultTicketCount = document.getElementById('adultTicketCount').value;
        const submitBtn = document.getElementById('submitBtn');
        const ticketSelection = document.querySelector('.ticket-selection');
        const languageSelection = document.querySelector('.language-selection');
        
        

        if (selectedDateElement && selectedTimeInput) {
            ticketSelection.classList.remove('disabled');
        } else {
            ticketSelection.classList.add('disabled');
            languageSelection.classList.add('disabled');
            // submitBtn.disabled = true;
            return;
        }

        // Enable language selection if adult ticket count is greater than 0
        if (parseInt(adultTicketCount) > 0) {
            languageSelection.classList.remove('disabled');
        } else {
            languageSelection.classList.add('disabled');
            // submitBtn.disabled = true;
            return;
        }

        // Enable submit button if all conditions are met
        if (document.querySelector('input[name="language"]:checked')) {
            submitBtn.disabled = false;
        } else {
            // submitBtn.disabled = true;
        }
    },

    // Function to change the quantity of an option
    // changeOptionQuantity: function (optionId, amount) {
    //     const option = model.bookingData.options.find(opt => opt.id === optionId);
    //     if (option) {
    //         option.quantity = Math.max(0, option.quantity + amount);
    //         view.updateOptionQuantityDisplay(optionId, option.quantity);
    //     }
    // },

    // Function to update the model booking data
    updateBookingData: function () {
        // Get the selected date and time
        const selectedDateElement = document.querySelector('.calendar-day.selected-date');
        const selectedTimeInput = document.querySelector('input[name="time"]:checked');

        if (selectedDateElement && selectedTimeInput) {
            const selectedDate = selectedDateElement.dataset.date;
            const selectedTime = selectedTimeInput.value;

            // Find the event matching the selected date and time
            const selectedEvent = model.events.find(event => event.date === selectedDate && event.time === selectedTime);

            if (selectedEvent) {
                // Update the booking data with the selected event's ID
                model.bookingData.event_id = selectedEvent.experience_event_id;
            } else {
                console.error('Selected event not found.');
            }
        } else {
            console.error('Selected date or time not found.');
        }

        // Update other booking data fields as needed
        model.bookingData.adults = parseInt(document.getElementById('adultTicketCount').value);
        model.bookingData.children = parseInt(document.getElementById('childTicketCount').value);

        // Get the selected language radio button
        const selectedLanguage = document.querySelector('input[name="language"]:checked');

        // Update the language code in the model based on the selected language
        if (selectedLanguage) {
            model.bookingData.language_code = selectedLanguage.value;
        } else {
            // If no language is selected, you may want to handle this case accordingly
            console.error('No language selected.');
        }
    },

    // Function to reset booking data when the date selection changes
    resetBookingData: function () {
        model.bookingData.adults = 0;
        model.bookingData.children = 0;
        model.bookingData.language_code = null;
        model.bookingData.event_id = null;
    },

};

// Function to fetch JSON data using AJAX
async function fetchEventData(parentExperienceId, url) {
    try {
        const response = await fetch(url);
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
    if (data.hasOwnProperty('languages') && data.hasOwnProperty('events')) {
        model.languages = data.languages;
        model.events = data.events;
        view.showOnlyAllowedLanguages();
        // Show calendar
        const currentDate = new Date(); // Or you can pass the date from the controller
        view.renderCalendar(currentDate);

    } else {
        const currentDate = new Date();
        view.renderCalendar(currentDate);
    }
};

// Function to fetch event data for the current event_id
async function fetchEventDataForCurrentEvent(eventId) {
    try {
        const response = await fetch(`/experience-event-data/${eventId}/`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        // Call function to handle the received data
        handleEventDataForCurrentEvent(data.result);
    } catch (error) {
        console.error('Error fetching data for current event:', error);
    }
};

// Function to handle the received event data for the current event
function handleEventDataForCurrentEvent(data) {
    model.current_event = data;
}

document.addEventListener('DOMContentLoaded', async function () {

    await fetchEventDataForCurrentEvent(currentEventId);

    // Fetch event data and wait for it to complete
    let fetchUrl;
    if (priceIsSpecial) {
        fetchUrl = `/actual-experience-events-with-discount/${parentExperienceId}/`;
    } else {
        fetchUrl = `/actual-experience-events/${parentExperienceId}/`;
    }
    await fetchEventData(parentExperienceId, fetchUrl);

    // Disable submit button, ticket selection, and language selection blocks on page load
    const submitBtn = document.getElementById('submitBtn');
    const ticketSelection = document.querySelector('.ticket-selection');
    const languageSelection = document.querySelector('.language-selection');

    // submitBtn.disabled = true;
    ticketSelection.classList.add('disabled');
    languageSelection.classList.add('disabled');

    controller.handleTicketsIncrementDecrement();
    controller.handleOptionIncrementDecrement();
    controller.handleTimeSelection();

    // Add event listeners to form inputs to update booking data
    document.getElementById('submitBtn').addEventListener('click', function (e) {
        e.preventDefault()
        controller.updateBookingData();
        controller.handleFormSubmit();
    });

    // Add event listener to the calendar to reset booking data on date selection change
    document.getElementById('calendarGrid').addEventListener('click', function () {
        controller.resetBookingData();
        controller.performValidation();
    });

    // Add event listener to time selection inputs to perform validation when time is selected
    document.querySelectorAll('input[name="time"]').forEach(input => {
        input.addEventListener('change', controller.performValidation);
    });

    // Add event listener to adult ticket count input to perform validation
    document.getElementById('adultTicketCount').addEventListener('input', controller.performValidation);


    document.querySelectorAll('input[name="language"]').forEach(input => {
        input.addEventListener('change', controller.performValidation);
    });

    // Simulate a click on the current date in the calendar
    const [tourMonth, tourDay, tourYear] = model.current_product.startDate.split('/');
    const tourStartDate = new Date(`${tourYear}-${tourMonth}-${tourDay}`);
    const tourStartYear = tourStartDate.getFullYear();
    const tourStartMonth = tourStartDate.getMonth();

    const [month, day, year] = model.current_product.startDate.split('/');

    view.renderCalendar(new Date(tourStartYear, tourStartMonth, 1));

    const currentDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    const currentDay = document.querySelector(`[data-date="${currentDate}"]`);
    if (currentDay) {
        currentDay.classList.add('selected-date');
        const clickEvent = new MouseEvent('click', {
            bubbles: true,
            cancelable: true,
            view: window
        });
        currentDay.dispatchEvent(clickEvent);
    } else {
        console.error('Current date not found in the calendar.');
    }

    // seed form data
    view.seedDataToForm();
    // view.seedOptionData();
});
