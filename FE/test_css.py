import re
content = open(r'D:\Python\AI Real Estate Advisor\Data\data_crawl\raw_pages\home-17e16fc1.html', encoding='utf-8').read()
links = re.findall(r'<link[^>]*rel=[\'"]stylesheet[\'"][^>]*href=[\'"]([^\'"]+)[\'"]', content, re.IGNORECASE)
print(f'Total links: {len(links)}')
for l in links[:10]:
    print(l)
