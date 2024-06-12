const model = {
    'languages': [],
    'events': [],
    'bookingData': {
        'adults': 0,
        'children': 0,
        'language_code': null,
        'customer_id': customerId,
        'session_key': sessionKey,
        'event_id': null,
        'parent_experience_id': parentExperienceId,
        'options': optionExtras,
    },
    'selectedDate': null,
    'googleItems': Object.assign(
        ecommerceItems,
        {'currency': 'EUR', 'price': 1.0, 'quantity': 1, 'item_variant': "EN"}
    ),
    'cart_not_empty': cartNotEmpty,
};

const view = {
    seedDataToForm: function () {
        let form = document.getElementById("bookingForm");
    },

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

    renderCalendar: function (date) {
        const calendarGrid = document.getElementById('calendarGrid');
        const currentMonthDisplay = document.getElementById('currentMonth');
        const prevMonthBtn = document.getElementById('prevMonth');
        const nextMonthBtn = document.getElementById('nextMonth');
        const selectedDate = model.selectedDate;
        calendarGrid.innerHTML = '';
        currentMonthDisplay.textContent = this.getMonthYearString(date);

        const today = new Date();
        prevMonthBtn.disabled = date.getMonth() === today.getMonth() && date.getFullYear() === today.getFullYear();

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
        calendarGrid.addEventListener('click', controller.handleDateClick);
    },

    createCalendarDay: function (date, inactive = false) {
        const dayElement = document.createElement('div');
        dayElement.classList.add('calendar-day');
        if (inactive) {
            dayElement.classList.add('inactive');
        } else {
            const isoDate = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate())).toISOString();
            const eventsForDate = model.events.filter(event => event.date === isoDate.split('T')[0]);
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
        calendarGrid.appendChild(dayElement);
    },

    getMonthYearString: function (date) {
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
        const month = monthNames[date.getMonth()];
        const year = date.getFullYear();
        return `${month} ${year}`;
    },

    updateTotalPriceDisplay: function (totalAdultPrice, totalChildPrice) {
        const adultTotalPriceElement = document.getElementById('adultTotalPrice');
        const childTotalPriceElement = document.getElementById('childTotalPrice');
        if (adultTotalPriceElement && childTotalPriceElement) {
            adultTotalPriceElement.textContent = `€${totalAdultPrice.toFixed(2)}`;
            childTotalPriceElement.textContent = `€${totalChildPrice.toFixed(2)}`;
        }
    },
    
    updateOptionQuantityDisplay: function (optionId, quantity) {
        const input = document.getElementById(`option_${optionId}`);
        if (input) {
            input.value = quantity;
        }
    }
};

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
            alert('Total participants exceed the maximum allowed participants for this event.');
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
                alert(`Quantity for ${option.name} exceeds the maximum allowed quantity.`);
                return false;
            }
        }
        return true;
    },
    
    handleFormSubmit: async function () {
        console.log("Run submitting process...");
        if (!controller.validateParticipantLimits() || !controller.validateOptionLimits()) {
            return;
        }

        const bookingData = model.bookingData;
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

        try {
            const response = await fetch('/create-group-product-without-booking/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify(bookingData)
            });

            if (response.ok) {
                if (model.cart_not_empty) {
                    const languageSlug = model.bookingData.language_code.toLowerCase();
                    window.dataLayer.push({ ecommerce: null });
                    window.dataLayer.push({
                        event: "add_to_cart",
                        ecommerce: [model.googleItems],
                    });
                    setTimeout(() => {
                        window.location.href = `/my-cart/${languageSlug}/`;
                    }, 200);
                } else {
                    const result = await response.json();
                    fillPopupData(result);
                    openPopup();
                }
            } else {
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
                    alert(`You cannot select more than ${option.max_quantity} of ${option.name}.`);
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
                        priceElement.innerHTML = `€${option.price * option.quantity}`;
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
        document.querySelectorAll('.time-selection input[type="radio"]').forEach(input => {
            input.addEventListener('click', function () {
                controller.performValidation();
                const selectedDate = document.querySelector('.calendar-day.selected-date');
                if (selectedDate) {
                    controller.updateTotalPrice(selectedDate.dataset.date, this.value);
                }
            });
        });
    },

    updateTotalPrice: function () {
        const selectedDateElement = document.querySelector('.calendar-day.selected-date');
        const selectedTimeInput = document.querySelector('input[name="time"]:checked');
        if (selectedDateElement && selectedTimeInput) {
            const selectedDate = selectedDateElement.dataset.date;
            const selectedTime = selectedTimeInput.value;
            const selectedEvent = model.events.find(event => event.date === selectedDate && event.time === selectedTime);
            if (selectedEvent) {
                const adultPrice = selectedEvent.adult_price;
                const childPrice = selectedEvent.child_price;
                const adultCount = parseInt(document.getElementById('adultTicketCount').value);
                const childCount = parseInt(document.getElementById('childTicketCount').value);
                model.googleItems.quantity = adultCount + childCount;
                const totalAdultPrice = adultPrice * adultCount;
                const totalChildPrice = childPrice * childCount;
                view.updateTotalPriceDisplay(totalAdultPrice, totalChildPrice);
                let totalOptionPrice = 0;
                model.bookingData.options.forEach(option => {
                    totalOptionPrice += option.price * option.quantity;
                });
                const totalPrice = totalAdultPrice + totalChildPrice + totalOptionPrice;
                model.googleItems.price = totalPrice;
                document.getElementById('submitBtn').textContent = `€${totalPrice.toFixed(2)} add to cart`;
            } else {
                console.error('Selected event not found.');
            }
        }
    },

    resetPricesAndButton: function () {
        document.getElementById('adultTotalPrice').textContent = '€0';
        document.getElementById('childTotalPrice').textContent = '€0';
        document.getElementById('submitBtn').textContent = 'Add to Cart';
    },

    handleDateClick: function (event) {
        const clickedDateElement = event.target;
        const clickedDate = clickedDateElement.dataset.date;
        const timeSelection = document.querySelector('.time-selection');
        timeSelection.innerHTML = '';
        if (clickedDate) {
            const eventsForDate = model.events.filter(event => event.date === clickedDate);
            eventsForDate.sort((a, b) => new Date('1970/01/01 ' + a.time) - new Date('1970/01/01 ' + b.time));
            if (document.querySelectorAll('.calendar-day.selected-date').length === 1) {
                controller.resetPricesAndButton();
            }
            if (eventsForDate.length > 0) {
                if (eventsForDate.length === 1) {
                    const timeInput = document.createElement('input');
                    timeInput.type = 'radio';
                    timeInput.id = eventsForDate[0].experience_event_id;
                    timeInput.name = 'time';
                    timeInput.value = eventsForDate[0].time;
                    timeInput.checked = true;
                    const timeLabel = document.createElement('label');
                    timeLabel.htmlFor = eventsForDate[0].experience_event_id;
                    timeLabel.textContent = eventsForDate[0].time;
                    timeSelection.appendChild(timeInput);
                    timeSelection.appendChild(timeLabel);
                } else {
                    eventsForDate.forEach(event => {
                        const timeInput = document.createElement('input');
                        timeInput.type = 'radio';
                        timeInput.id = event.experience_event_id;
                        timeInput.name = 'time';
                        timeInput.value = event.time;
                        const timeLabel = document.createElement('label');
                        timeLabel.htmlFor = event.experience_event_id;
                        timeLabel.textContent = event.time;
                        timeSelection.appendChild(timeInput);
                        timeSelection.appendChild(timeLabel);
                        timeInput.addEventListener('change', function () {
                            controller.performValidation();
                        });
                    });
                }
            } else {
                const noEventsMessage = document.createElement('p');
                noEventsMessage.textContent = 'No experiences available for this date.';
                timeSelection.appendChild(noEventsMessage);
            }
            document.querySelectorAll('.calendar-day').forEach(day => {
                day.classList.remove('selected-date');
            });
            clickedDateElement.classList.add('selected-date');
            model.selectedDate = clickedDate;
            controller.updateTotalPrice();
            controller.handleTimeSelection();
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

        if (parseInt(adultTicketCount) > 0) {
            languageSelection.classList.remove('disabled');
        } else {
            languageSelection.classList.add('disabled');
            submitBtn.disabled = true;
            return;
        }

        if (document.querySelector('input[name="language"]:checked')) {
            optionTitle.classList.remove('disabled');
            optionSelection.classList.remove('disabled');
            submitBtn.disabled = false;
        } else {
            submitBtn.disabled = true;
            return;
        }
    },

    // changeOptionQuantity: function (optionId, amount) {
    //     const option = model.bookingData.options.find(opt => opt.id === optionId);
    //     const price = document.getElementById(`option_price_${optionId}`);
    //     if (option) {
    //         option.quantity = Math.max(0, option.quantity + amount);
    //         view.updateOptionQuantityDisplay(optionId, option.quantity);
    //         if (option.price > 0) {
    //             price.innerHTML = `€${option.price * option.quantity}`;
    //         } else {
    //             price.innerHTML = 'FREE';
    //         }
    //     }
    //     controller.updateTotalPrice();
    // },

    updateBookingData: function () {
        const selectedDateElement = document.querySelector('.calendar-day.selected-date');
        const selectedTimeInput = document.querySelector('input[name="time"]:checked');
        if (selectedDateElement && selectedTimeInput) {
            const selectedDate = selectedDateElement.dataset.date;
            const selectedTime = selectedTimeInput.value;
            const selectedEvent = model.events.find(event => event.date === selectedDate && event.time === selectedTime);
            if (selectedEvent) {
                model.bookingData.event_id = selectedEvent.experience_event_id;
            } else {
                console.error('Selected event not found.');
            }
        } else {
            console.error('Selected date or time not found.');
        }
        model.bookingData.adults = parseInt(document.getElementById('adultTicketCount').value);
        model.bookingData.children = parseInt(document.getElementById('childTicketCount').value);
        const selectedLanguage = document.querySelector('input[name="language"]:checked');
        if (selectedLanguage) {
            model.bookingData.language_code = selectedLanguage.value;
        } else {
            console.error('No language selected.');
        }
    },

    resetBookingData: function () {
        model.bookingData.language_code = null;
        model.bookingData.event_id = null;
    },
};

async function fetchEventData(parentExperienceId, url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        handleEventData(data.result);
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

function handleEventData(data) {
    if (data.hasOwnProperty('languages') && data.hasOwnProperty('events')) {
        model.languages = data.languages;
        model.events = data.events;
        view.showOnlyAllowedLanguages();
        const currentDate = new Date();
        view.renderCalendar(currentDate);
    } else {
        const currentDate = new Date();
        view.renderCalendar(currentDate);
    }
}

function openPopup() {
    const popupWrapper = document.querySelector('.upsale-popup-wrapper');
    popupWrapper.classList.add('opened');
}

function closePopup() {
    const popupWrapper = document.querySelector('.upsale-popup-wrapper');
    popupWrapper.classList.remove('opened');
}

function fillPopupData(data) {
    const popupWrapper = document.querySelector('.upsale-popup-wrapper');
    const tourNameElement = popupWrapper.querySelector('.tour-name');
    const tourInfoListElement = popupWrapper.querySelector('.tour-info-list');
    tourNameElement.textContent = data.tourName;
    tourInfoListElement.innerHTML = '';
    data.tourInfo.forEach(info => {
        const listItem = document.createElement('li');
        listItem.textContent = info;
        tourInfoListElement.appendChild(listItem);
    });
}

document.querySelector('.close-popup-btn').addEventListener('click', closePopup);

document.addEventListener('DOMContentLoaded', async function () {
    let fetchUrl;
    if (cartNotEmpty) {
        fetchUrl = `/actual-experience-events-with-discount/${parentExperienceId}/`;
    } else {
        fetchUrl = `/actual-experience-events/${parentExperienceId}/`;
    }
    await fetchEventData(parentExperienceId, fetchUrl);

    const submitBtn = document.getElementById('submitBtn');
    const ticketSelection = document.querySelector('.ticket-selection');
    const languageSelection = document.querySelector('.language-selection');

    submitBtn.disabled = true;
    ticketSelection.classList.add('disabled');
    languageSelection.classList.add('disabled');

    controller.handleTicketsIncrementDecrement();
    controller.handleOptionIncrementDecrement();
    controller.handleTimeSelection();

    document.getElementById('submitBtn').addEventListener('click', function (e) {
        // TODO: Check this moment!
            e.preventDefault();
            controller.updateBookingData();
            controller.handleFormSubmit();
    });

    document.getElementById('calendarGrid').addEventListener('click', function () {
        controller.resetBookingData();
        controller.performValidation();
    });

    document.querySelectorAll('input[name="time"]').forEach(input => {
        input.addEventListener('change', controller.performValidation);
    });

    document.getElementById('adultTicketCount').addEventListener('input', controller.performValidation);

    document.querySelectorAll('input[name="language"]').forEach(input => {
        input.addEventListener('change', controller.performValidation);
    });

    const currentDate = new Date();
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
    optionsWrapper.classList.toggle('opened');
    optionsTitle.classList.toggle('opened');
});


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
