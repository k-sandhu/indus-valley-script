"""Retain HTML responses and headers locally; print candidate PDF links."""
import argparse, hashlib, json, re
from datetime import datetime, timezone
import requests
from acquire_sources import RAW

def fetch(identifier, url):
    record = {'id': identifier, 'url': url, 'retrieved_utc': datetime.now(timezone.utc).isoformat()}
    try:
        response = requests.get(url, timeout=45)
        (RAW / (identifier + '.html')).write_text(response.text, encoding='utf-8')
        record.update(status_code=response.status_code, final_url=response.url,
                      status='acquired' if response.ok else 'failed',
                      sha256=hashlib.sha256(response.content).hexdigest())
        links = re.findall(r'(?:href|content)=[\"\']([^\"\']*(?:pdf|bitstream)[^\"\']*)', response.text)
        record['candidate_links'] = links
    except Exception as error:
        record.update(status='failed', error=str(error))
    (RAW / (identifier + '.html-acquisition.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    return record

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('id'); parser.add_argument('url')
    args = parser.parse_args()
    print(json.dumps(fetch(args.id, args.url), ensure_ascii=True))
