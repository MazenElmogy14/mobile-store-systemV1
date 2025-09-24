document.addEventListener('DOMContentLoaded', () => {
    const themeToggleBtn = document.getElementById('theme-toggle');
    const body = document.body;
    const nav = document.querySelector('nav');

    // Function to update the icon based on the current theme
    const updateIcon = () => {
        const icon = themeToggleBtn.querySelector('i');
        if (body.classList.contains('light-mode')) {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
        } else {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        }
    };

    // Check for saved theme preference in local storage
    const savedTheme = localStorage.getItem('theme');

    if (savedTheme) {
        // If a theme is saved, use it
        body.classList.add(savedTheme);
        nav.classList.add(savedTheme);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
        // If no theme is saved, check system preference and default to light mode
        body.classList.add('light-mode');
        nav.classList.add('light-mode');
        localStorage.setItem('theme', 'light-mode');
    } else {
        // Otherwise, default to dark mode
        body.classList.add('dark-mode');
        nav.classList.add('dark-mode');
        localStorage.setItem('theme', 'dark-mode');
    }

    // Set the initial icon to match the theme
    updateIcon();

    // Add click listener to the theme toggle button
    themeToggleBtn.addEventListener('click', () => {
        if (body.classList.contains('light-mode')) {
            // Switch to dark mode
            body.classList.remove('light-mode');
            body.classList.add('dark-mode');
            nav.classList.remove('light-mode');
            nav.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark-mode');
        } else {
            // Switch to light mode
            body.classList.remove('dark-mode');
            body.classList.add('light-mode');
            nav.classList.remove('dark-mode');
            nav.classList.add('light-mode');
            localStorage.setItem('theme', 'light-mode');
        }
        // Update the icon to reflect the new theme
        updateIcon();
    });
});
