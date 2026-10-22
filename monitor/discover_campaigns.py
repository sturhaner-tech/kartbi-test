#!/usr/bin/env python3
"""Discover *candidate links* on bank campaign index pages. Never publish campaign terms."""
import datetime
import json
import pathlib
import re
import urllib.parse
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
MONITOR = ROOT / 'monitor'
INDEXES = json.loads((MONITOR / 'sources.json').read_text(encoding='utf-8'))
BASELINE = MONITOR / 'discovery_baseline.json'
REPORT = MONITOR / 'discovery_report.json'
PUBLIC = ROOT / 'data' / 'discovery_status.json'
AGENT = 'KartbiDiscovery/0.1 (candidate link review only)'
MAX_HTML = 500_000
MAX_LINKS = 300

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href')
            if href:
                self.hrefs.append(href)

def candidates(html, index_url):
    parser = Links()
    parser.feed(html)
    host = urllib.parse.urlsplit(index_url).hostname
    result = set()
    for href in parser.hrefs:
        url = urllib.parse.urljoin(index_url, href)
        parts = urllib.parse.urlsplit(url)
        if parts.scheme != 'https' or parts.hostname != host:
            continue
        path = parts.path.rstrip('/') or '/'
        if path == urllib.parse.urlsplit(index_url).path.rstrip('/'):
            continue
        # Only links in campaign sections or URLs explicitly containing campaign words.
        if not re.search(r'kampanya|campaign|firsat', path, re.I):
            continue
        # Strip tracking query strings and fragments; never follow candidate links.
        result.add(urllib.parse.urlunsplit(('https', parts.netloc.lower(),path,'','')))
    return sorted(result)[:MAX_LINKS]

def check(index, robots_cache):
    bank = index['bank']; url = index['url']
    item = {'bank':bank, 'index':url, 'status':'unavailable','new_links':[], 'total_links':0}
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != 'https' or not parts.hostname:
        item['status'] = 'invalid_url'; return item, None
    origin = f'{parts.scheme}://{parts.netloc}'
    try:
        if origin not in robots_cache:
            robot = urllib.robotparser.RobotFileParser()
            robot.set_url(origin + '/robots.txt')
            robot.read()
            robots_cache[origin] = robot
        if not robots_cache[origin].can_fetch(AGENT, url):
            item['status'] = 'robots_disallowed'; return item, None
        req = urllib.request.Request(url,headers={'User-Agent':AGENT,'Accept':'text/html'})
        with urllib.request.urlopen(req,timeout=12) as response:
            if 'text/html' not in response.headers.get('Content-Type','').lower():
                raise ValueError('Non-HTML response')
            data = response.read(MAX_HTML + 1)
        if len(data) > MAX_HTML:
            raise ValueError('Page exceeds size limit')
        links = candidates(data.decode('utf-8',errors='replace'),url)
        item.update(status='ok',total_links=len(links))
        return item, links
    except Exception as exc:
        item['reason'] = str(exc)[:150]
        return item, None

def main():
    try:
        old = json.loads(BASELINE.read_text(encoding='utf-8')) if BASELINE.exists() else {}
        if not isinstance(old,dict): old={}
    except (OSError,ValueError): old={}
    updated = dict(old); rows=[]; robots={}
    for index in INDEXES:
        row, links = check(index,robots)
        url = index['url']
        if links is not None:
            if url not in old:
                row['status']='baseline_created'
                row['new_links']=[]
            else:
                row['new_links']=sorted(set(links)-set(old[url]))
            # Preserve unseen links in baseline to avoid false rediscovery when a site paginates.
            updated[url] = sorted(set(old.get(url,[]))|set(links))
        rows.append(row)
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    report={'checked_at':now,'banks_checked':len(rows),'new_link_count':sum(len(x['new_links']) for x in rows), 'results':rows,
            'notice':'Candidate URLs only. A link is not a verified campaign; no automatic terms or reward publication.'}
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    BASELINE.write_text(json.dumps(updated,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    PUBLIC.write_text(json.dumps({'checkedAt':now,'newLinkCount':report['new_link_count'],'banks':[{'bank':x['bank'],'status':x['status'],'newLinkCount':len(x['new_links'])} for x in rows]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'banks_checked':len(rows),'new_link_count':report['new_link_count'],'status':[{'bank':r['bank'],'status':r['status']} for r in rows]},ensure_ascii=False))

if __name__=='__main__':main()
