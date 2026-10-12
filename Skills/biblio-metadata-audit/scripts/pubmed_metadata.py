"""Rechercher les notices incomplètes dans PubMed sans modifier Zotero."""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from audit_metadata import normalized

PUBMED_BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'


# --------------------------------------------------
def request(endpoint: str, params: dict[str, str | int]) -> bytes:
	"""Lire une réponse NCBI avec limitation de fréquence et reprise transitoire."""
	url = PUBMED_BASE_URL + endpoint + '?' + urllib.parse.urlencode(params)
	for attempt in range(3):
		time.sleep(0.4 + attempt)
		try:
			with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'ZoteroMetadataAudit/1.0'}), timeout=40) as response:
				return response.read()
		except Exception:
			if attempt == 2:
				raise


# --------------------------------------------------
def value(element: ET.Element | None) -> str:
	"""Extraire le texte Unicode d'un élément XML et de ses enfants."""
	return ''.join(element.itertext()).strip() if element is not None else ''


# --------------------------------------------------
def parse(data: bytes | str) -> list[dict[str, Any]]:
	"""Extraire les champs bibliographiques sans écrire dans la bibliothèque."""
	result = []
	for article in ET.fromstring(data).findall('PubmedArticle'):
		citation = article.find('MedlineCitation')
		a = citation.find('Article')
		ids = {e.get('IdType'): value(e) for e in article.findall('PubmedData/ArticleIdList/ArticleId')}
		date = a.find('Journal/JournalIssue/PubDate')
		dates = {e.tag: value(e) for e in date} if date is not None else {}
		authors = [
			{'lastName': value(e.find('LastName')), 'firstName': value(e.find('ForeName')), 'initials': value(e.find('Initials'))}
			for e in a.findall('AuthorList/Author')
			if e.find('LastName') is not None
		]
		result.append(
			{
				'pmid': value(citation.find('PMID')),
				'ids': ids,
				'title': value(a.find('ArticleTitle')),
				'authors': authors,
				'fields': {
					'DOI': ids.get('doi', ''),
					'publicationTitle': value(a.find('Journal/Title')),
					'journalAbbreviation': value(a.find('Journal/ISOAbbreviation')),
					'volume': value(a.find('Journal/JournalIssue/Volume')),
					'issue': value(a.find('Journal/JournalIssue/Issue')),
					'pages': ('-'.join(filter(None, [value(a.find('Pagination/StartPage')), value(a.find('Pagination/EndPage'))])))
					or value(a.find('Pagination/MedlinePgn'))
					or value(a.find('ELocationID[@EIdType="pii"]')),
					'ISSN': value(a.find('Journal/ISSN')),
					'language': value(a.find('Language')),
					'abstractNote': '\n'.join((e.get('Label', '') + ': ' if e.get('Label') else '') + value(e) for e in a.findall('Abstract/AbstractText')),
				},
				'pubdate': dates,
				'article_dates': [{**{e.tag: value(e) for e in d}, 'type': d.get('DateType', '')} for d in a.findall('ArticleDate')],
			}
		)
	return result


# --------------------------------------------------
def main(output: Path):
	"""Inventorier les correspondances exactes et conserver les cas non résolus."""
	records = json.loads((output / 'inventaire.json').read_text(encoding='utf-8'))
	issues = json.loads((output / 'corrections.json').read_text(encoding='utf-8'))['issues']
	keys = {r['key'] for r in issues if r['status'] == 'manquant'}
	targets = [i for i in records if i['key'] in keys and i['type'] == 'journalArticle']
	dois = [i['fields']['DOI'] for i in targets if i['fields'].get('DOI')]
	found = []
	for offset in range(0, len(dois), 25):
		term = ' OR '.join('"' + d + '"[AID]' for d in dois[offset : offset + 25])
		search = json.loads(request('esearch.fcgi', {'db': 'pubmed', 'term': term, 'retmode': 'json', 'retmax': 200}))
		ids = search['esearchresult']['idlist']
		if ids: found.extend(parse(request('efetch.fcgi', {'db': 'pubmed', 'id': ','.join(ids), 'retmode': 'xml'})))
		print('DOI batch', offset // 25 + 1, 'results', len(ids), flush=True)
	by_doi = {r['fields']['DOI'].casefold(): r for r in found if r['fields']['DOI']}
	output = {}
	for item in targets:
		localdoi = item['fields'].get('DOI', '').casefold()
		remote = by_doi.get(localdoi)
		if not remote:
			term = '"' + item['fields']['title'].rstrip('.') + '"[Title]'
			try:
				search = json.loads(request('esearch.fcgi', {'db': 'pubmed', 'term': term, 'retmode': 'json', 'retmax': 3}))
				ids = search['esearchresult']['idlist']
				candidates = parse(request('efetch.fcgi', {'db': 'pubmed', 'id': ','.join(ids), 'retmode': 'xml'})) if ids else []
				remote = max(candidates, key=lambda r: SequenceMatcher(None, normalized(item['fields']['title']), normalized(r['title'])).ratio(), default=None)
			except Exception as error:
				output[item['key']] = {'identity': 'error', 'error': str(error)}
				continue
		if not remote:
			output[item['key']] = {'identity': 'not_found'}
			continue
		score = SequenceMatcher(None, normalized(item['fields']['title']), normalized(remote['title'])).ratio()
		local = {normalized(a['lastName']) for a in item['creators'] if a['role'] == 'author' and a['fieldMode'] == 0}
		remote_names = {normalized(a['lastName']) for a in remote['authors']}
		overlap = len(local & remote_names) / len(local) if local else 0
		matching_doi = bool(localdoi and localdoi == remote['fields']['DOI'].casefold())
		conflict = bool(localdoi and remote['fields']['DOI'] and localdoi != remote['fields']['DOI'].casefold())
		trusted = score >= 0.94 and overlap >= 0.8 and not conflict
		output[item['key']] = {
			'identity': 'candidate',
			'title_score': round(score, 4),
			'author_overlap': overlap,
			'doi_match': matching_doi,
			'consistent_match': trusted,
			'source': 'https://pubmed.ncbi.nlm.nih.gov/' + remote['pmid'] + '/',
			'metadata': remote,
		}
	(output / 'sources-pubmed.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
	from collections import Counter

	print(json.dumps({'targets': len(targets), 'identities': dict(Counter(r['identity'] for r in output.values()))}), flush=True)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Prepare PubMed candidates without modifying Zotero.")
	parser.add_argument("--output", type=Path, required=True)
	arguments = parser.parse_args()
	main(arguments.output)
