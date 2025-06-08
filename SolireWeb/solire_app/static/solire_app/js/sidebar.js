// Sidebar toggle functionality
const toggleBtn = document.getElementById('toggleSidebar');
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');
const sidebarOverlay = document.getElementById('sidebarOverlay');

toggleBtn.addEventListener('click', function() {
    if (window.innerWidth <= 768) {
        // Mobile behavior
        sidebar.classList.toggle('show');
        sidebarOverlay.classList.toggle('show');
    } else {
        // Desktop behavior
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('expanded');
    }
});

// Close sidebar when clicking overlay on mobile
sidebarOverlay.addEventListener('click', function() {
    sidebar.classList.remove('show');
    sidebarOverlay.classList.remove('show');
});

// Handle window resize
window.addEventListener('resize', function() {
    if (window.innerWidth > 768) {
        sidebar.classList.remove('show');
        sidebarOverlay.classList.remove('show');
    }
});

// Navigation link active state
const navLinks = document.querySelectorAll('.nav-link');
navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        navLinks.forEach(l => l.classList.remove('active'));
        this.classList.add('active');
    });
});