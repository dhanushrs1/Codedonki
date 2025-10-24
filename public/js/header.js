// Header functionality for CodeDonki
document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu functionality
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    const mobileMenuOverlay = document.getElementById('mobileMenuOverlay');
    const mobileMenuClose = document.getElementById('mobileMenuClose');
    
    // Toggle mobile menu
    function toggleMobileMenu() {
        const isActive = mobileMenu.classList.contains('active');
        
        if (isActive) {
            closeMobileMenu();
        } else {
            openMobileMenu();
        }
    }
    
    // Open mobile menu
    function openMobileMenu() {
        mobileMenu.classList.add('active');
        mobileMenuOverlay.classList.add('active');
        mobileMenuToggle.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    // Close mobile menu
    function closeMobileMenu() {
        mobileMenu.classList.remove('active');
        mobileMenuOverlay.classList.remove('active');
        mobileMenuToggle.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    // Event listeners
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', toggleMobileMenu);
    }
    
    if (mobileMenuClose) {
        mobileMenuClose.addEventListener('click', closeMobileMenu);
    }
    
    if (mobileMenuOverlay) {
        mobileMenuOverlay.addEventListener('click', closeMobileMenu);
    }
    
    // Close mobile menu when clicking on nav links
    const mobileNavLinks = document.querySelectorAll('.mobile-nav-links a');
    mobileNavLinks.forEach(link => {
        link.addEventListener('click', () => {
            // Small delay to allow navigation to start
            setTimeout(closeMobileMenu, 100);
        });
    });
    
    // Close mobile menu on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && mobileMenu.classList.contains('active')) {
            closeMobileMenu();
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768 && mobileMenu.classList.contains('active')) {
            closeMobileMenu();
        }
    });
    
    // Admin detection and profile loading
    async function loadUserProfile() {
        try {
            const token = localStorage.getItem('token');
            if (!token) return;
            
            const response = await fetch('/api/profile', {
                headers: { 
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) return;
            
            const profile = await response.json();
            
            // Update desktop profile elements
            updateProfileElements(profile, 'desktop');
            
            // Update mobile profile elements
            updateProfileElements(profile, 'mobile');
            
            // Show admin panel if user is admin
            if (profile.role === 'admin') {
                showAdminPanel();
            }
            
        } catch (error) {
            console.error('Error loading user profile:', error);
        }
    }
    
    // Update profile elements
    function updateProfileElements(profile, type) {
        const prefix = type === 'mobile' ? 'mobile-' : '';
        
        // Update avatar
        const avatar = document.getElementById(`${prefix}avatar`);
        if (avatar && profile.avatar_url) {
            avatar.src = profile.avatar_url;
        }
        
        // Update username
        const username = document.getElementById(`${prefix}username`);
        if (username && profile.name) {
            username.textContent = profile.name;
        }
    }
    
    // Show admin panel buttons
    function showAdminPanel() {
        const adminPanelLi = document.getElementById('adminPanelLi');
        const mobileAdminPanelLi = document.getElementById('mobileAdminPanelLi');
        
        if (adminPanelLi) {
            adminPanelLi.style.display = 'block';
        }
        
        if (mobileAdminPanelLi) {
            mobileAdminPanelLi.style.display = 'block';
        }
    }
    
    // Initialize profile loading if user is logged in
    const userLoggedIn = document.querySelector('body').classList.contains('user-logged-in') || 
                        document.querySelector('.nav-links .btn-secondary');
    
    if (userLoggedIn) {
        loadUserProfile();
    }
    
    // Add smooth scroll behavior for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add loading states for navigation links
    const navLinks = document.querySelectorAll('.nav-links a, .mobile-nav-links a');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Only add loading state for internal links
            if (this.hostname === window.location.hostname) {
                this.style.opacity = '0.7';
                this.style.pointerEvents = 'none';
                
                // Reset after navigation
                setTimeout(() => {
                    this.style.opacity = '';
                    this.style.pointerEvents = '';
                }, 1000);
            }
        });
    });
});

// Utility function to check if user is admin
async function isUserAdmin() {
    try {
        const token = localStorage.getItem('token');
        if (!token) return false;
        
        const response = await fetch('/api/profile', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) return false;
        
        const profile = await response.json();
        return profile.role === 'admin';
    } catch (error) {
        console.error('Error checking admin status:', error);
        return false;
    }
}

// Export functions for use in other scripts
window.HeaderUtils = {
    isUserAdmin,
    toggleMobileMenu: () => {
        const mobileMenuToggle = document.getElementById('mobileMenuToggle');
        if (mobileMenuToggle) mobileMenuToggle.click();
    }
};
