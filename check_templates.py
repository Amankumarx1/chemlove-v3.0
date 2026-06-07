from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('d:/Aman/Tools/Chemlove/v2/templates'))
try:
    env.get_template('student/chapter_view.html')
    print('chapter_view.html: OK')
except Exception as e:
    print(f'chapter_view.html: ERROR - {e}')
try:
    env.get_template('student/chapter_section.html')
    print('chapter_section.html: OK')
except Exception as e:
    print(f'chapter_section.html: ERROR - {e}')
