import re

content = open(r'D:\Python\AI Real Estate Advisor\Data\data_crawl\raw_pages\home-17e16fc1.html', encoding='utf-8').read()
head_match = re.search(r'<head[^>]*>(.*?)</head>', content, re.IGNORECASE | re.DOTALL)
if head_match:
    head = head_match.group(1)
    links = re.findall(r'<link[^>]*rel=[\'"]stylesheet[\'"][^>]*>', head, re.IGNORECASE)
    print(f'Found {len(links)} stylesheets')
    styles = re.findall(r'<style[^>]*>.*?</style>', head, re.IGNORECASE | re.DOTALL)
    print(f'Found {len(styles)} style tags')
    for link in links:
        if "wp-content/themes" in link or "wp-content/plugins" in link:
            print("Stylesheet:", re.search(r'href=[\'"]([^\'"]+)[\'"]', link).group(1) if re.search(r'href=[\'"]([^\'"]+)[\'"]', link) else link)
