function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('active');
}

// Ensure sidebar is hidden on small screens by default
window.addEventListener('resize', () => {
    const sidebar = document.querySelector('.sidebar');
    if (window.innerWidth <= 1023 && !sidebar.classList.contains('active')) {
        sidebar.classList.remove('active');
    } else if (window.innerWidth > 1023) {
        sidebar.classList.add('active');
    }
});

// Run on initial load
if (window.innerWidth <= 1023) {
    document.querySelector('.sidebar').classList.remove('active');
} else {
    document.querySelector('.sidebar').classList.add('active');
}