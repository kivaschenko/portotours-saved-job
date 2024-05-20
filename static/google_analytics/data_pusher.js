function trackButtonClick(url, items, clickPlace) {
    items['item_list_name'] = clickPlace;
    let itemsArray = [items];
    console.log('items', items);
    window.dataLayer.push({ecommerce: null});  // Clear the previous ecommerce object.
    window.dataLayer.push({
        event: "view_item",
        ecommerce: {
            items: itemsArray,
        }
    });
    setTimeout(function () {
        window.open(url, '_blank');
    }, 200);
}
