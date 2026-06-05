// Theme Controller System for ChemLove Ecosystem

// Apply theme to document
function applyTheme(theme) {
    const html = document.documentElement;
    if (theme === 'dark') {
        html.classList.add('dark');
        html.classList.remove('light');
    } else if (theme === 'light') {
        html.classList.add('light');
        html.classList.remove('dark');
    } else {
        // System preference
        const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (systemDark) {
            html.classList.add('dark');
            html.classList.remove('light');
        } else {
            html.classList.add('light');
            html.classList.remove('dark');
        }
    }
}

// Fetch and apply theme on load
async function initializeTheme() {
    try {
        const res = await fetch('/api/theme_preference');
        if (res.ok) {
            const data = await res.json();
            const theme = data.theme || 'system';
            applyTheme(theme);
            
            // Set active state in selectors if present on page
            const themeSelector = document.getElementById('theme-preference-select');
            if (themeSelector) {
                themeSelector.value = theme;
            }
        }
    } catch (e) {
        console.error('Failed to load theme preference', e);
        // Fallback to local storage or dark by default
        applyTheme('dark');
    }
}

// Save theme preference
async function saveThemePreference(theme) {
    applyTheme(theme);
    try {
        await fetch('/api/theme_preference', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ theme })
        });
    } catch (e) {
        console.error('Failed to sync theme preference with database', e);
    }
}

// Listen for system color scheme changes if system theme is selected
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    fetch('/api/theme_preference')
        .then(res => res.json())
        .then(data => {
            if (data.theme === 'system') {
                applyTheme('system');
            }
        }).catch(() => {});
});

// Boot theme
document.addEventListener('DOMContentLoaded', () => {
    initializeTheme();
});
