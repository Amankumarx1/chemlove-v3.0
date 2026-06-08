/* --- ChemLove Keyboard Navigation Tracker --- */
(function() {
    function handleFirstTab(e) {
        if (e.key === 'Tab') {
            document.body.classList.add('keyboard-navigation');
            window.removeEventListener('keydown', handleFirstTab);
            window.addEventListener('mousedown', handleMouseDownOnce);
        }
    }
    
    function handleMouseDownOnce() {
        document.body.classList.remove('keyboard-navigation');
        window.removeEventListener('mousedown', handleMouseDownOnce);
        window.addEventListener('keydown', handleFirstTab);
    }
    
    window.addEventListener('keydown', handleFirstTab);
})();

/* Browser Focus Persistence */
document.addEventListener('click', function(e) {
    if (
        e.target.closest('.sidebar-link') ||
        e.target.closest('.admin-tab-btn')
    ) {
        document.activeElement?.blur();
    }
});

