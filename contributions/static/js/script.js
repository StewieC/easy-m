// Ensure sidebar is hidden on small screens by default
window.addEventListener('resize', () => {
    const sidebar = document.querySelector('.sidebar');
    if (window.innerWidth <= 1023) {
        sidebar.classList.remove('active');
    } else {
        sidebar.classList.add('active');
    }
});

// Run on initial load
if (window.innerWidth <= 1023) {
    document.querySelector('.sidebar').classList.remove('active');
} else {
    document.querySelector('.sidebar').classList.add('active');
}

function toggleDropdown() {
    const dropdown = document.querySelector('.dropdown-menu');
    dropdown.classList.toggle('hidden');
}

function toggleNotifications() {
    const notificationDropdown = document.querySelector('.notification-dropdown');
    notificationDropdown.classList.toggle('hidden');
}