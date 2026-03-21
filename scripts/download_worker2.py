import os
import requests
import json
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
PDF_DIR = '/Users/hmc123/Documents/optimization/docs/research/papers/pdfs/'
os.makedirs(PDF_DIR, exist_ok=True)

papers = {
    'TSP-2': {'doi': '10.1016/j.oceaneng.2009.10.011', 'url': None},
    'HVTM-3': {'doi': '10.1016/j.ocecoaman.2015.02.014', 'url': None},
    'CCP-1': {'doi': '10.1080/03088839.2010.486644', 'url': None},
    'SAA-M1': {'doi': None, 'url': 'https://commons.wmu.se/all_dissertations/3448/'}
}

results = {}

for name, info in papers.items():
    results[name] = 'Failed'
    try:
        pdf_url = None
        if info['doi']:
            # Try SemanticScholar
            r = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{info['doi']}?fields=openAccessPdf", headers=HEADERS, timeout=10, verify=False)
            if r.status_code == 200:
                data = r.json()
                if data and data.get('openAccessPdf') and data['openAccessPdf'].get('url'):
                    pdf_url = data['openAccessPdf']['url']
            
            # If not found, try CrossRef
            if not pdf_url:
                cr = requests.get(f"https://api.crossref.org/works/{info['doi']}", headers=HEADERS, timeout=10, verify=False)
                if cr.status_code == 200:
                    cdata = cr.json()
                    if 'message' in cdata and 'link' in cdata['message']:
                        for link in cdata['message']['link']:
                            if link.get('content-type') == 'application/pdf':
                                pdf_url = link['URL']
                                break
        
        if info['url'] and not pdf_url:
            page = requests.get(info['url'], headers=HEADERS, timeout=10, verify=False)
            if page.status_code == 200:
                # WMU commons uses this pattern for download links
                match = re.search(r'href="([^"]+/download/)"', page.text)
                if match:
                    pdf_url = match.group(1)
                else:
                    match = re.search(r'href="([^"]+\.pdf[^"]*)"', page.text)
                    if match:
                        pdf_url = match.group(1)
                if pdf_url and not pdf_url.startswith('http'):
                    if pdf_url.startswith('/'):
                        from urllib.parse import urlparse
                        parsed = urlparse(info['url'])
                        pdf_url = f"{parsed.scheme}://{parsed.netloc}{pdf_url}"
                    else:
                        pdf_url = info['url'].rstrip('/') + '/' + pdf_url
        
        if pdf_url:
            print(f"Found PDF URL for {name}: {pdf_url}")
            pdf_r = requests.get(pdf_url, headers=HEADERS, timeout=30, verify=False)
            if pdf_r.status_code == 200 and b'%PDF' in pdf_r.content[:10]:
                filepath = os.path.join(PDF_DIR, f"{name}.pdf")
                with open(filepath, 'wb') as f:
                    f.write(pdf_r.content)
                results[name] = 'Success'
            else:
                print(f"Failed to download valid PDF for {name} from {pdf_url}")
    except Exception as e:
        print(f"Error processing {name}: {e}")

# Update status
status_file = '/Users/hmc123/Documents/optimization/docs/research/papers/download_status.md'
new_status = "\n### Worker 2 Results (SemanticScholar/CrossRef/Direct)\n\n"
for name, status in results.items():
    new_status += f"- {name}: {status}\n"

with open(status_file, 'a') as f:
    f.write(new_status)

print(json.dumps(results))
