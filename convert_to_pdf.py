"""
Convert Markdown to PDF using HTML intermediate
"""
import markdown2
import os

# Read the markdown file
md_file = "COMPREHENSIVE_TEST_ANALYSIS.md"
with open(md_file, 'r', encoding='utf-8') as f:
    md_content = f.read()

# Convert markdown to HTML with extras
html_content = markdown2.markdown(md_content, extras=[
    'tables', 
    'fenced-code-blocks', 
    'code-friendly',
    'cuddled-lists',
    'header-ids'
])

# Create a full HTML document with styling
full_html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Verity Systems - Comprehensive Test Analysis Report</title>
    <style>
        @page {{
            margin: 1in;
            size: letter;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: white;
        }}
        h1 {{
            color: #1a5f7a;
            border-bottom: 3px solid #1a5f7a;
            padding-bottom: 10px;
            font-size: 28px;
        }}
        h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #eee;
            padding-bottom: 8px;
            margin-top: 30px;
            font-size: 22px;
        }}
        h3 {{
            color: #34495e;
            font-size: 18px;
            margin-top: 20px;
        }}
        h4 {{
            color: #555;
            font-size: 16px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
            font-size: 14px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 10px 12px;
            text-align: left;
        }}
        th {{
            background-color: #1a5f7a;
            color: white;
            font-weight: 600;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 13px;
        }}
        pre {{
            background-color: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 13px;
            line-height: 1.4;
        }}
        pre code {{
            background: none;
            color: inherit;
            padding: 0;
        }}
        blockquote {{
            border-left: 4px solid #1a5f7a;
            margin: 15px 0;
            padding: 10px 20px;
            background: #f9f9f9;
        }}
        hr {{
            border: none;
            border-top: 2px solid #eee;
            margin: 30px 0;
        }}
        .pass {{ color: #27ae60; font-weight: bold; }}
        .fail {{ color: #e74c3c; font-weight: bold; }}
        strong {{
            color: #2c3e50;
        }}
        ul, ol {{
            padding-left: 25px;
        }}
        li {{
            margin-bottom: 5px;
        }}
        .header-info {{
            background: linear-gradient(135deg, #1a5f7a 0%, #2980b9 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .header-info p {{
            margin: 5px 0;
        }}
        .emoji {{
            font-size: 1.1em;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>'''

# Save as HTML first
html_file = "COMPREHENSIVE_TEST_ANALYSIS.html"
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(full_html)

print(f"✅ HTML file created: {html_file}")
print(f"   Size: {os.path.getsize(html_file):,} bytes")
print(f"\n📄 To create PDF:")
print(f"   1. Open {html_file} in your browser")
print(f"   2. Press Ctrl+P (Print)")
print(f"   3. Select 'Save as PDF' as destination")
print(f"   4. Click Save")
print(f"\n   Or open this file directly and print to PDF!")
