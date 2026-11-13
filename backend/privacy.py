"""Fail-closed public egress. No raw retrieved text crosses this boundary."""
import hashlib
import re

def words(text):
    return re.findall(r"[\w]+", text.casefold())

class PublicRelease:
    def __init__(self, chunks, display_allowlist=None, metadata_allowlist=None):
        self.display = set(display_allowlist or [])
        self.metadata = set(metadata_allowlist or [])
        # Long exact passages are blocked even in no-RAG answers (memorisation).
        # This is a conservative overlap guard, not a proof against all leakage.
        self.restricted = set()
        for c in chunks:
            if c['id'] not in self.display:
                w = words(c['text'])
                self.restricted.update(tuple(w[i:i+8]) for i in range(max(0, len(w)-7)))

    def release(self, answer, chunks, checked, citation_re):
        public_citations = []
        for item in checked['citations']:
            matching = [c for c in chunks if c['id'] in self.metadata]
            # Resolver is passed by caller for exact per-chunk binding.
            match = next((c for c in matching if self.resolver(item['citation'], [c])['n_supported']), None)
            shown = item['citation'] if match else '[Source reference restricted]'
            answer = answer.replace(item['citation'], shown)
            public_citations.append({'citation': shown, 'resolves': bool(match and item['supported']),
                'source_id': match['id'] if match else None,
                'section': match['meta']['section_id'] if match else None,
                'page': match['meta']['page'] if match else None,
                'evidence_excerpt': match['text'] if match and match['id'] in self.display else None,
                'excerpt_status': 'Source reference available; policy excerpt restricted.'})
        w = words(answer)
        if any(tuple(w[i:i+8]) in self.restricted for i in range(max(0, len(w)-7))):
            return None, [], []
        evidence = []
        for c in chunks:
            if c['id'] in self.metadata:
                evidence.append({'source_id': c['id'], 'section': c['meta']['section_id'],
                    'page': c['meta']['page'], 'excerpt': c['text'] if c['id'] in self.display else None})
        return answer, public_citations, evidence
