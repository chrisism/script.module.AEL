import sys, re

addon_file = sys.argv[1]
changelog_file = sys.argv[2]
addon_xml = '' 
changelog_txt = ''

with open(addon_file, 'r') as f:
    addon_xml = f.read()
with open(changelog_file, 'r') as f:
    changelog_txt = f.read()

changelog_txt = changelog_txt.replace('\n', '[CR]')
addon_xml = re.sub(r'<news>(.*)?</news>', f'<news>{changelog_txt}</news>', addon_xml)
with open(addon_file, 'w') as f:
    f.write(addon_xml)