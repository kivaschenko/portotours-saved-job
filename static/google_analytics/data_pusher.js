function trackButtonClick(url, items) {
    // Capture the current URL at the time of the click
    let clickPlace = window.location.href;
    items['item_list_name'] = clickPlace;

    let itemsArray = [items];
    window.dataLayer.push({ecommerce: null});  // Clear the previous ecommerce object.
    window.dataLayer.push({
        event: "select_item",
        ecommerce: {
            items: itemsArray,
        }
    });

    setTimeout(function () {
        window.open(url, '_blank');
    }, 200);
}


