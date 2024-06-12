const model = {
    // The JSON data about all allowed events will be seeded here after page loading
    'languages': [],
    'events': [],
    'bookingData': {
        'adults': 0,
        'children': 0,
        'language_code': null,
        'customer_id': customerId, // from page scope
        'session_key': sessionKey, // from page scope
        'event_id': null,
        'parent_experience_id': parentExperienceId, // from page scope
        'options': optionExtras,  // from page scope
    },
    'selectedDate': null,
    'googleItems': Object.assign(
        ecommerceItems,
        {'currency': 'EUR', 'price': 1.0, 'quantity': 1, 'item_variant': "EN"}
    ),
    'cart_not_empty': cartNotEmpty,
};

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
            const isoDate = calendarGrid.children[index].dataset.date; // Получаем дату из data-атрибута
            const eventsForDate = model.events.filter(event => event.date === isoDate); // Фильтруем события по дате


            if (eventsForDate.length > 0) {
                const minPrice = Math.min(...eventsForDate.map(event => event.total_price)); // Находим минимальную цену

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

    // Function to update the quantity display for an option
    updateOptionQuantityDisplay: function (optionId, quantity) {
        const input = document.getElementById(`option_${optionId}`);
        if (input) {
            input.value = quantity;
        }
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
        console.log("Inside Participants validation:");
        const selectedEvent = model.events.find(event => event.date === model.selectedDate);
        console.log("selectedEvent:", selectedEvent);
        const totalParticipants = controller.getTotalParticipants();
        console.log("Total participants:", totalParticipants);
        if (totalParticipants > selectedEvent.remaining_participants) {
            return false;
        }
        return true;
    },

    validateOptionLimits: function () {
        console.log("Inside Options validation:");
        for (const option of model.bookingData.options) {
            const optionElement = document.getElementById(`option_${option.id}`);
            console.log("Current optionElement:", optionElement);
            console.log("optionElement.value:", optionElement.value);
            console.log("option.max_quantity:", option.max_quantity);
            if (parseInt(optionElement.value) > option.max_quantity) {
                return false;
            }
        }
        return true;
    },

    // Function to handle form submission
    handleFormSubmit: async function () {
        console.log("Run submitting process...");
        if (!controller.validateParticipantLimits() || !controller.validateOptionLimits()) {
            return;
        }
        // Get the booking data from the model
        const bookingData = model.bookingData;

        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

        try {
            // Send the booking data to the server using fetch or another AJAX method
            const response = await fetch('/create-private-product-without-booking/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify(bookingData)
            });

            // Check if response is successful
            if (response.ok) {
                if (model.cart_not_empty) {
                    // Handle successful response
                    const languageSlug = model.bookingData.language_code.toLowerCase();

                    // Push data to Google analytics
                    window.dataLayer.push({ecommerce: null});
                    window.dataLayer.push({
                        event: "add_to_cart",
                        ecommerce: [model.googleItems],
                    });
                    setTimeout(() => {
                        // window.open(`/my-cart/${languageSlug}/`)
                        window.location.href = `/my-cart/${languageSlug}/`;
                    }, 200);

                } else {
                    const result = await response.json();

                    // Check if the response contains the expected data
                    if (result && result.tourName && result.tourInfo) {
                        // Fill the popup data
                        fillPopupData(result);

                        // Open the popup
                        openPopup();
                    }
                }
            } else {
                // Handle error response
                console.error('Error submitting booking:', response.statusText);
            }
        } catch (error) {
            console.error('Error submitting booking:', error);
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
                const input = button.closest('.quantity').querySelector('input');
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

                // Recalculate the total price
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

                // update quantity for Google data
                model.googleItems.quantity = adultCount + childCount;


                let totalOptionPrice = 0;
                model.bookingData.options.forEach(option => {
                    totalOptionPrice += option.price * option.quantity;
                });

                // Update submit button text
                const totalPrice = selectedEvent.total_price + totalOptionPrice;

                // Update price in Google data
                model.googleItems.price = totalPrice;

                submitBtn.textContent = `€${totalPrice.toFixed(2)} add to cart`;
            } else {
                console.error('Selected event not found.');
            }
        }
    },

    resetPricesAndButton: function () {


        // Reset submit button text
        submitBtn.textContent = 'Add to Cart';
    },

    // Function to handle click on a date cell
    handleDateClick: function (event) {
        const clickedDateElement = event.target;
        const clickedDate = clickedDateElement.dataset.date;

        // Clear the time selection area
        const timeSelection = document.querySelector('.time-selection');
        timeSelection.innerHTML = '';

        // Reset adult and child ticket counts when date changes
        // document.getElementById('adultTicketCount').value = 0;
        // document.getElementById('childTicketCount').value = 0;

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
                eventsForDate.forEach(event => {
                    const maxParticipantsElement = document.querySelector('.max-participants span');
                    maxParticipantsElement.textContent = `${event.max_participants}`;

                });
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
                noEventsMessage.textContent = 'No experiences available for this date.';
                timeSelection.appendChild(noEventsMessage);
            }

            // Highlight the selected date
            document.querySelectorAll('.calendar-day').forEach(day => {
                day.classList.remove('selected-date');
            });
            clickedDateElement.classList.add('selected-date');
            model.selectedDate = clickedDate;
            controller.updateTotalPrice()
        }
    },
    performValidation: function () {
        const selectedDateElement = document.querySelector('.calendar-day.selected-date');
        const selectedTimeInput = document.querySelector('input[name="time"]:checked');
        const adultTicketCount = document.getElementById('adultTicketCount').value;
        const submitBtn = document.getElementById('submitBtn');
        const ticketSelection = document.querySelector('.ticket-selection');
        const languageSelection = document.querySelector('.language-selection');
        const optionTitle = document.querySelector('.options-title-wrapper');
        const optionSelection = document.querySelector('.options-inputs-wrapper');

        // Enable ticket selection if date and time are selected
        if (selectedDateElement && selectedTimeInput) {
            ticketSelection.classList.remove('disabled');
        } else {
            ticketSelection.classList.add('disabled');
            languageSelection.classList.add('disabled');
            optionTitle.classList.add('disabled');
            optionSelection.classList.add('disabled');
            submitBtn.disabled = true;
            return;
        }

        // Enable language selection if adult ticket count is greater than 0
        if (parseInt(adultTicketCount) > 0) {

            languageSelection.classList.remove('disabled');
        } else {
            languageSelection.classList.add('disabled');
            submitBtn.disabled = true;
            return;
        }

        // Enable submit button if all conditions are met
        if (document.querySelector('input[name="language"]:checked')) {
            optionTitle.classList.remove('disabled');
            optionSelection.classList.remove('disabled');
            submitBtn.disabled = false;
        } else {
            submitBtn.disabled = true;
            return;
        }
    },

    // Function to change the quantity of an option
    // changeOptionQuantity: function (optionId, amount) {
    //     const option = model.bookingData.options.find(opt => opt.id === optionId);
    //     const price = document.getElementById(`option_price_${optionId}`);
    //
    //     if (option) {
    //         option.quantity = Math.max(0, option.quantity + amount);
    //         view.updateOptionQuantityDisplay(optionId, option.quantity);
    //         if (option.price > 0) {
    //             price.innerHTML = `€${option.price * option.quantity}`
    //         } else {
    //             price.innerHTML = 'FREE'
    //         }
    //     }
    //     controller.updateTotalPrice();
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
        // model.bookingData.adults = 0;
        // model.bookingData.children = 0;
        model.bookingData.language_code = null;
        model.bookingData.event_id = null;
        // Reset other fields as needed
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
}

// Function to open the popup
function openPopup() {
    const popupWrapper = document.querySelector('.upsale-popup-wrapper');
    popupWrapper.classList.add('opened');
}

// Function to close the popup
function closePopup() {
    const popupWrapper = document.querySelector('.upsale-popup-wrapper');
    popupWrapper.classList.remove('opened');
}

// Function to fill popup data
function fillPopupData(data) {
    const popupWrapper = document.querySelector('.upsale-popup-wrapper');
    const tourNameElement = popupWrapper.querySelector('.tour-name');
    const tourInfoListElement = popupWrapper.querySelector('.tour-info-list');

    // Fill tour name
    tourNameElement.textContent = data.tourName;

    // Clear existing tour info list items
    tourInfoListElement.innerHTML = '';

    // Fill tour info list
    data.tourInfo.forEach(info => {
        const listItem = document.createElement('li');
        listItem.textContent = info;
        tourInfoListElement.appendChild(listItem);
    });

    // Fill other popup elements if necessary
    // Example:
    // const popupTitle = popupWrapper.querySelector('.popup-title');
    // popupTitle.textContent = data.popupTitle;
}

// Event listeners
document.querySelector('.close-popup-btn').addEventListener('click', closePopup);

document.addEventListener('DOMContentLoaded', async function () {
    let fetchUrl;
    if (cartNotEmpty) {
        fetchUrl = `/actual-experience-events-with-discount/${parentExperienceId}/`
    } else {
        fetchUrl = `/actual-experience-events/${parentExperienceId}/`;
    }

    // Fetch event data and wait for it to complete
    await fetchEventData(parentExperienceId, fetchUrl);

    // Disable submit button, ticket selection, and language selection blocks on page load
    const submitBtn = document.getElementById('submitBtn');
    const ticketSelection = document.querySelector('.ticket-selection');
    const languageSelection = document.querySelector('.language-selection');

    submitBtn.disabled = true;
    ticketSelection.classList.add('disabled');
    languageSelection.classList.add('disabled');

    controller.handleTicketsIncrementDecrement();
    controller.handleOptionIncrementDecrement();
    // Call handleTimeSelection function to add event listeners to time selection inputs
    controller.handleTimeSelection();

    // Add event listeners to form inputs to update booking data
    document.getElementById('submitBtn').addEventListener('click', function (e) {
        e.preventDefault()
        // Gather form data and update the model
        controller.updateBookingData(); // This function should be updated to gather all form data

        // Call a function to handle form submission
        controller.handleFormSubmit();
    });

    // Add event listener to the calendar to reset booking data on date selection change
    document.getElementById('calendarGrid').addEventListener('click', function () {
        // Reset booking data and perform validation when date is selected
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
    // Get the current date
    const currentDate = new Date();

    // Simulate a click on the current date in the calendar
    const currentDay = document.querySelector(`[data-date="${currentDate.toISOString().split('T')[0]}"]`);
    if (currentDay) {
        const clickEvent = new MouseEvent('click', {
            bubbles: true,
            cancelable: true,
            view: window
        });
        currentDay.dispatchEvent(clickEvent);
    } else {
        console.error('Current date not found in the calendar.');
    }


});


let optionsWrapper = document.querySelector('.options-inputs-wrapper');
let optionsTitle = document.querySelector('.options-title-wrapper');
optionsTitle.addEventListener('click', () => {
    optionsWrapper.classList.toggle('opened')
    optionsTitle.classList.toggle('opened')
})


// -----------
// MOBILE FORM

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
