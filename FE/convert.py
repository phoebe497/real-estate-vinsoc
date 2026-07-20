import re
import os
import json

def process_html_for_injection(html):
    # Extract just the body content
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.IGNORECASE | re.DOTALL)
    if body_match:
        html = body_match.group(1)
        
    # Remove scripts to prevent execution issues or syntax errors
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<noscript[^>]*>.*?</noscript>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # We don't want the original header/footer since we have our own layout.tsx Header and Footer.
    # The original site has <header id="header"> and <footer id="socket"> etc.
    # Let's try to remove the WP header and footer if they exist to avoid duplication.
    html = re.sub(r'<header[^>]*id=[\'"]header[\'"].*?</header>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<footer[^>]*id=[\'"]footer[\'"].*?</footer>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<footer[^>]*id=[\'"]socket[\'"].*?</footer>', '', html, flags=re.DOTALL | re.IGNORECASE)
    # Remove #wpadminbar
    html = re.sub(r'<div[^>]*id=[\'"]wpadminbar[\'"].*?</div>', '', html, flags=re.DOTALL | re.IGNORECASE)

    # Replace absolute URLs with relative routes
    html = html.replace('https://vinhomeoceanpark.com.vn/chung-cu/', '/chung-cu/')
    html = html.replace('https://vinhomeoceanpark.com.vn/chung-cu', '/chung-cu')
    html = html.replace('https://vinhomeoceanpark.com.vn/biet-thu/', '/biet-thu/')
    html = html.replace('https://vinhomeoceanpark.com.vn/biet-thu', '/biet-thu')
    # For subdivisions (the original site puts them at root e.g. /the-zenpark/)
    html = html.replace('https://vinhomeoceanpark.com.vn/the-zenpark/', '/phan-khu/the-zenpark/')
    html = html.replace('https://vinhomeoceanpark.com.vn/the-zurich/', '/phan-khu/the-zurich/')
    html = html.replace('https://vinhomeoceanpark.com.vn/the-beverly/', '/phan-khu/the-beverly/')
    html = html.replace('https://vinhomeoceanpark.com.vn/masteri-waterfront/', '/phan-khu/masteri-waterfront/')
    html = html.replace('https://vinhomeoceanpark.com.vn/the-pavilion/', '/phan-khu/the-pavilion/')
    html = html.replace('https://vinhomeoceanpark.com.vn/the-sapphire/', '/phan-khu/the-sapphire/')
    html = html.replace('https://vinhomeoceanpark.com.vn/the-ocean-view/', '/phan-khu/the-ocean-view/')
    html = html.replace('https://vinhomeoceanpark.com.vn/the-london/', '/phan-khu/the-london/')
    html = html.replace('https://vinhomeoceanpark.com.vn/the-paris/', '/phan-khu/the-paris/')
    html = html.replace('https://vinhomeoceanpark.com.vn/masteri-lakeside/', '/phan-khu/masteri-lakeside/')
    html = html.replace('https://vinhomeoceanpark.com.vn/the-senique-hanoi/', '/phan-khu/the-senique-hanoi/')
    
    # Strip protocol from asset links or leave them as is (images will load from vinhomeoceanpark.com.vn if not downloaded)
    # The user said "Về phần ảnh thì hãy xử lý như bạn đề xuất" meaning using local paths or original links. 
    # Leaving them as original absolute URLs to vinhomeoceanpark is safest for now to ensure they render immediately.
    
    # Fix WordPress Lazy Loading for images
    def img_repl(m):
        img_tag = m.group(0)
        lazy_src = re.search(r'data-lazy-src=[\'"]([^\'"]+)[\'"]', img_tag)
        if lazy_src:
            real_src = lazy_src.group(1)
            # Remove any existing src
            img_tag = re.sub(r'src=[\'"][^\'"]*[\'"]', '', img_tag)
            # Add the real src
            img_tag = img_tag.replace('<img ', f'<img src="{real_src}" ')
            
        # Strip srcset and lazy attributes that break loading without JS
        img_tag = re.sub(r'srcset=[\'"][^\'"]*[\'"]', '', img_tag)
        img_tag = re.sub(r'data-lazy-srcset=[\'"][^\'"]*[\'"]', '', img_tag)
        img_tag = re.sub(r'sizes=[\'"][^\'"]*[\'"]', '', img_tag)
        img_tag = re.sub(r'data-lazy-sizes=[\'"][^\'"]*[\'"]', '', img_tag)
        img_tag = re.sub(r'data-lazy-src=[\'"][^\'"]*[\'"]', '', img_tag)
        img_tag = re.sub(r'decoding=[\'"]async[\'"]', '', img_tag)
        img_tag = re.sub(r'loading=[\'"]lazy[\'"]', '', img_tag)
        # Remove lazyload classes
        img_tag = img_tag.replace('lazyload', '')
        
        return img_tag
    html = re.sub(r'<img[^>]+>', img_repl, html, flags=re.IGNORECASE)
    
    # Fix WordPress background lazy loading
    def bg_repl(m):
        tag = m.group(0)
        bg = re.search(r'data-bg=[\'"]([^\'"]+)[\'"]', tag)
        if bg:
            real_bg = bg.group(1)
            if 'style=' in tag:
                # Append to existing inline style
                tag = re.sub(r'style=[\'"]([^\'"]*)[\'"]', r'style="\1 background-image: url(' + real_bg + ');"', tag)
            else:
                # Just add style attribute
                tag = tag.replace('>', f' style="background-image: url({real_bg});">')
        return tag
    html = re.sub(r'<div[^>]+data-bg=[^>]+>', bg_repl, html, flags=re.IGNORECASE)
    
    return html

def convert_file(input_path, output_path, component_name):
    with open(input_path, encoding='utf-8') as f:
        content = f.read()

    processed_html = process_html_for_injection(content)
    
    # We will pass the HTML string securely by JSON encoding it to avoid backtick/quote escaping issues in JS
    html_json = json.dumps(processed_html)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f'''export default function {component_name}() {{
  return (
    <div 
      className="{component_name.lower()}-container"
      dangerouslySetInnerHTML={{{{ __html: {html_json} }}}}
    />
  );
}}
''')

# Convert Home page
convert_file(
    r'D:\Python\AI Real Estate Advisor\Data\data_crawl\raw_pages\home-17e16fc1.html',
    r'src\app\page.tsx',
    'HomePage'
)

# Convert Chung Cu page
os.makedirs(r'src\app\chung-cu', exist_ok=True)
convert_file(
    r'D:\Python\AI Real Estate Advisor\Data\data_crawl\raw_pages\chung-cu-869871e7.html',
    r'src\app\chung-cu\page.tsx',
    'ChungCuPage'
)

# Convert Subdivision pages
subdivisions = [
    'the-zenpark', 'the-zurich', 'the-beverly', 'masteri-waterfront', 
    'the-pavilion', 'the-sapphire', 'the-ocean-view', 'the-london', 
    'the-paris', 'masteri-lakeside', 'the-senique-hanoi'
]

# We need to map subdivision name to the actual filename
raw_files = os.listdir(r'D:\Python\AI Real Estate Advisor\Data\data_crawl\raw_pages')
for sub in subdivisions:
    # Find the file that starts with the subdivision name
    matching_files = [f for f in raw_files if f.startswith(sub + '-')]
    if matching_files:
        file_name = matching_files[0]
        out_dir = rf'src\app\phan-khu\{sub}'
        os.makedirs(out_dir, exist_ok=True)
        convert_file(
            os.path.join(r'D:\Python\AI Real Estate Advisor\Data\data_crawl\raw_pages', file_name),
            os.path.join(out_dir, 'page.tsx'),
            sub.replace('-', ' ').title().replace(' ', '') + 'Page'
        )
