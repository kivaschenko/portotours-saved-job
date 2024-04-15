if (window.innerWidth > 768) {

    function changeLanguage(selectedLanguage) {
        let currentUrl = window.location.href;
        let replaceValue = '/' + selectedLanguage + '/';
        // Update the URL with the selected language
        let newUrl = currentUrl.replace(/\/[a-z]{2}\//, replaceValue);

        // Change the window location to the new URL
        window.location.href = newUrl;

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
            document.querySelectorAll('#defaultLanguage .language-icon').forEach(function (icon) {
                icon.classList.remove('active');
            });
            // Find image with the appropriate class and add the 'active' class to it
            let selectedIcon = document.querySelector('#defaultLanguage .language-icon-' + selectedLanguage);
            if (selectedIcon) {
                
                selectedIcon.classList.add('active');
            }
        } else {
            console.log('test language2')
            // If language slug is not found in the URL, set default language flag
            let defaultLanguageIcon = defaultLanguageElement.querySelector('.language-icon-en'); // Assuming 'en' for English
            if (defaultLanguageIcon) {
                defaultLanguageIcon.classList.add('active');
            }
        }
    }

    // Register the onPageLoad function to be executed on window.onload
    window.onload = onPageLoad
} else {

    function changeLanguage(selectedLanguage) {
        let currentUrl = window.location.href;
        let replaceValue = '/' + selectedLanguage + '/';
        // Update the URL with the selected language
        let newUrl = currentUrl.replace(/\/[a-z]{2}\//, replaceValue);

        // Change the window location to the new URL
        window.location.href = newUrl;

        let defaultLanguageElement = document.getElementById('mobileDefaultLanguage');
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
        let defaultLanguageElement = document.getElementById('mobileDefaultLanguage');

        // Get the language options list
        let languageOptionsList = document.getElementById('mobileLanguageOptions');

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
            console.log('test!!')
            let selectedLanguage = languageMatch[1];
            // Remove the 'active' class from all images
            document.querySelectorAll('.language-switcher-mobile .language-icon').forEach(function (icon) {
                icon.classList.remove('active');
            });
            // Find image with the appropriate class and add the 'active' class to it
            let selectedIcon = document.querySelector('.language-switcher-mobile .language-icon-' + selectedLanguage);
            if (selectedIcon) {
                selectedIcon.classList.add('active');
            }
        } else {
            // If language slug is not found in the URL, set default language flag
            let defaultLanguageIcon = defaultLanguageElement.querySelector('.language-icon-en'); // Assuming 'en' for English
            if (defaultLanguageIcon) {
                defaultLanguageIcon.classList.add('active');
            }
        }
    }

    // Register the onPageLoad function to be executed on window.onload
    window.onload = onPageLoad
}
