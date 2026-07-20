import urllib.request
import re
import os

print("Fetching homepage...")
req = urllib.request.Request(
    'https://vinhomeoceanpark.com.vn/', 
    headers={'User-Agent': 'Mozilla/5.0'}
)
try:
    html = urllib.request.urlopen(req).read().decode('utf-8')
except Exception as e:
    print("Error fetching HTML:", e)
    exit(1)

# Find CSS links
links = re.findall(r'<link[^>]*rel=[\'"]stylesheet[\'"][^>]*href=[\'"]([^\'"]+)[\'"]', html, re.IGNORECASE)
print(f"Found {len(links)} CSS links.")

main_css = ""
for link in links:
    if link.startswith('/'):
        link = 'https://vinhomeoceanpark.com.vn' + link
        
    print("Fetching CSS:", link)
    try:
        req_css = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
        css_content = urllib.request.urlopen(req_css).read().decode('utf-8')
        main_css += f"\n/* Source: {link} */\n" + css_content + "\n"
    except Exception as e:
        print("Error fetching CSS:", link, e)

# Extract inline styles from head
head_match = re.search(r'<head[^>]*>(.*?)</head>', html, re.IGNORECASE | re.DOTALL)
if head_match:
    styles = re.findall(r'<style[^>]*>(.*?)</style>', head_match.group(1), re.IGNORECASE | re.DOTALL)
    for s in styles:
        main_css += f"\n/* Inline style */\n{s}\n"

# Remove the display:none for data-lazy-src that hides images
main_css = re.sub(r'\[data-lazy-src\]\s*\{\s*display\s*:\s*none\s*!important;\s*\}', '', main_css)
main_css = re.sub(r'\.rll-youtube-player,\s*\[data-lazy-src\]\s*\{\s*display:\s*none\s*!important;\s*\}', '', main_css)

os.makedirs('public/css', exist_ok=True)
with open('public/css/vinhomes-style.css', 'w', encoding='utf-8') as f:
    f.write(main_css)

print("Saved main CSS to public/css/vinhomes-style.css")
