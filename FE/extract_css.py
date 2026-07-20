import re
import json

file_path = r'D:\Python\AI Real Estate Advisor\Data\data_crawl\raw_pages\home-17e16fc1.html'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

head_match = re.search(r'<head[^>]*>(.*?)</head>', content, re.IGNORECASE | re.DOTALL)
if head_match:
    head = head_match.group(1)
    css_content = ''
    links = re.findall(r'(<link[^>]*rel=[\'"]stylesheet[\'"][^>]*>)', head, re.IGNORECASE)
    for link in links:
        # replace relative paths with absolute to original server if needed, but they are mostly absolute
        css_content += link + '\n'
        
    styles = re.findall(r'(<style[^>]*>.*?</style>)', head, re.IGNORECASE | re.DOTALL)
    for style in styles:
        css_content += style + '\n'
        
    # Strip lazy load CSS rules that hide images without JS
    css_content = re.sub(r'\[data-lazy-src\]\{display:none !important;\}', '', css_content)
    css_content = re.sub(r'\.rll-youtube-player, \[data-lazy-src\]\{display:none !important;\}', '', css_content)
    
    with open('src/app/public-styles.tsx', 'w', encoding='utf-8') as f:
        f.write('export function PublicStyles() {\n')
        f.write('  return <div dangerouslySetInnerHTML={{ __html: ' + json.dumps(css_content) + ' }} />;\n')
        f.write('}\n')
