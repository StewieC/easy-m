// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {

    // Mobile Menu Toggle
    const mobileMenuIcon = document.getElementById('mobileMenuIcon');
    const mobileDropdownMenu = document.getElementById('mobileDropdownMenu');
    const closeMobileMenu = document.getElementById('closeMobileMenu');

    if (mobileMenuIcon && mobileDropdownMenu) {
        mobileMenuIcon.addEventListener('click', () => {
            mobileDropdownMenu.classList.toggle('open');
            mobileMenuIcon.classList.toggle('open');
            // Optional: Prevent body scroll when menu is open
            document.body.classList.toggle('overflow-hidden-mobile');
        });
    }
    if (closeMobileMenu && mobileDropdownMenu) {
        closeMobileMenu.addEventListener('click', () => {
            mobileDropdownMenu.classList.remove('open');
            mobileMenuIcon.classList.remove('open');
            document.body.classList.remove('overflow-hidden-mobile');
        });
    }
    
    // Close mobile menu if clicking outside of it
    document.addEventListener('click', function(event) {
        if (mobileDropdownMenu && mobileDropdownMenu.classList.contains('open')) {
            const isClickInsideMenu = mobileDropdownMenu.contains(event.target);
            const isClickOnIcon = mobileMenuIcon.contains(event.target);
            if (!isClickInsideMenu && !isClickOnIcon) {
                mobileDropdownMenu.classList.remove('open');
                mobileMenuIcon.classList.remove('open');
                document.body.classList.remove('overflow-hidden-mobile');
            }
        }
    });


    // Notification Bell Toggle
    const notificationBell = document.getElementById('notificationBell');
    const notificationDropdown = document.getElementById('notificationDropdown');

    if (notificationBell && notificationDropdown) {
        notificationBell.addEventListener('click', function(event) {
            event.stopPropagation(); // Prevent click from bubbling up to document
            notificationDropdown.classList.toggle('show');
        });

        // Close notification dropdown when clicking outside
        document.addEventListener('click', function(event) {
            if (notificationDropdown.classList.contains('show') && !notificationBell.contains(event.target)) {
                notificationDropdown.classList.remove('show');
            }
        });
    }

    // Auto-dismiss messages after a few seconds
    const messages = document.querySelectorAll('.messages-container .message-item');
    messages.forEach(function(message, index) {
        // Stagger the fade out for multiple messages
        setTimeout(() => {
            message.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            message.style.opacity = '0';
            message.style.transform = 'translateX(20px)';
            setTimeout(() => message.remove(), 500); // Remove from DOM after transition
        }, 5000 + (index * 500)); // 5 seconds + 0.5s stagger
    });
    
    // Apply .form-input class to Django's default form fields if not already applied by widget attrs
    // This targets fields rendered by {{ form.as_p }} or {{ form.field_name }}
    const formFields = document.querySelectorAll(
        'form input[type="text"], form input[type="email"], form input[type="password"], form input[type="number"], form input[type="url"], form input[type="tel"], form input[type="date"], form select, form textarea'
    );
    formFields.forEach(field => {
        if (!field.classList.contains('form-input') && !field.classList.contains('form-checkbox')) {
            // Check if it's inside a div that already has specific styling (like a custom widget)
            if (!field.closest || !field.closest('div[class*="custom-widget-wrapper"]')) {
                 field.classList.add('form-input');
            }
        }
    });
    const checkboxFields = document.querySelectorAll('form input[type="checkbox"]');
    checkboxFields.forEach(field => {
        if (!field.classList.contains('form-checkbox')) {
             if (!field.closest || !field.closest('div[class*="custom-widget-wrapper"]')) {
                field.classList.add('form-checkbox');
             }
        }
    });


    // Add an active class to the current nav link based on URL
    // This is an alternative/enhancement to the Django template logic
    const currentPath = window.location.pathname;
    const sidebarNavLinks = document.querySelectorAll('.sidebar-nav .nav-link');
    sidebarNavLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active'); // Ensure only current is active
        }
    });
    // For mobile dropdown as well
    const mobileNavLinks = document.querySelectorAll('.dropdown-menu .nav-link');
     mobileNavLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active'); // You might need a specific .active style for mobile if different
        } else {
            link.classList.remove('active');
        }
    });

});