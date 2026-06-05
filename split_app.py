import os, re

with open('chemlove1.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract styles and scripts
style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
script_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)

style = style_match.group(1) if style_match else ''
script = script_match.group(1) if script_match else ''

# Remove styles and scripts from html
html = re.sub(r'<style>.*?</style>', '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/style.css\') }}">', content, flags=re.DOTALL)
html = re.sub(r'<script>.*?</script>', '<script src="{{ url_for(\'static\', filename=\'js/script.js\') }}"></script>', html, flags=re.DOTALL)

# Add Inter font to the html
html = re.sub(r'family=DM\+Sans:wght@400;500;600;700;800', 'family=Inter:wght@400;500;600;700;800', html)

# Update colors in style
style = re.sub(r'--primary:\s*#[a-fA-F0-9]+;', '--primary: #10B981;', style)
style = re.sub(r'--secondary:\s*#[a-fA-F0-9]+;', '--secondary: #8B5CF6;', style)
style = re.sub(r'--tertiary:\s*#[a-fA-F0-9]+;', '--tertiary: #38BDF8;', style)
style = re.sub(r'--neutral:\s*#[a-fA-F0-9]+;', '--neutral: #717973;', style)
style = re.sub(r'--accent:\s*#[a-fA-F0-9]+;', '--accent: #8B5CF6;', style)
style = re.sub(r'DM Sans', 'Inter', style)
style = re.sub(r'--bg:\s*#[a-fA-F0-9]+;', '--bg: #09090e;', style)
style = re.sub(r'--bg-gradient:\s*radial-gradient\(circle at top right, #[a-fA-F0-9]+ 0%, #[a-fA-F0-9]+ 50%\);', '--bg-gradient: radial-gradient(circle at top right, #1a202c 0%, #09090e 50%);', style)

os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('templates', exist_ok=True)

with open('static/css/style.css', 'w', encoding='utf-8') as f:
    f.write(style)

with open('static/js/script.js', 'w', encoding='utf-8') as f:
    f.write(script)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
