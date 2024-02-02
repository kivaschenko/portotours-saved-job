function changeLanguage(selectedLanguage) {

    // Update the URL with the selected language if pathname exists
    if (languages[selectedLanguage]) {
        let newPathname = languages[selectedLanguage];
        window.location.pathname = newPathname;
    }

    let defaultLanguageElement = document.getElementById('defaultLanguage');
    // Remove the 'active' class from all language icons
    defaultLanguageElement.querySelectorAll('.language-icon').forEach(function (icon) {
        icon.classList.remove('active');
    });

    let selectedLanguageIcon = defaultLanguageElement.querySelector('.language-icon-' + selectedLanguage);
    if (selectedLanguageIcon) {
        selectedLanguageIcon.classList.add('active');
    }
}

function onPageLoad() {
    // Get the default language element
    let defaultLanguageElement = document.getElementById('defaultLanguage');

    // Get the language options list
    let languageOptionsList = document.getElementById('languageOptions');

    // Attach click event to each language option
    languageOptionsList.querySelectorAll('li').forEach(function (option) {
        option.addEventListener('click', function () {
            // Get the selected language code from the data attribute
            let selectedLanguage = option.getAttribute('data-language');

            // Call the changeLanguage function with the selected language
            changeLanguage(selectedLanguage);
        });
    });

    let currentUrl = window.location.href;
    // Modify the content of the default language element

    let languageMatch = currentUrl.match(/\/([a-z]{2})\//);

    if (languageMatch) {
        let selectedLanguage = languageMatch[1];
        // Remove the 'active' class from all images
        document.querySelectorAll('.language-icon').forEach(function (icon) {
            icon.classList.remove('active');
        });
        // Find image with the appropriate class and add the 'active' class to it
        let selectedIcon = document.querySelector('.language-icon-' + selectedLanguage);
        if (selectedIcon) {
            selectedIcon.classList.add('active');
        }
    }
}

// Register the onPageLoad function to be executed on window.onload
window.onload = onPageLoad