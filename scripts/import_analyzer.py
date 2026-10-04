"""Extract supplied Analyzer 1.0 DNA for host review, never infer product facts."""
import argparse,json
from pathlib import Path

def extract(data):
    if data.get('schema_version')!='1.0' or not isinstance(data.get('claims'),dict):raise ValueError('Unsupported Analyzer schema')
    result={'kind':'analyzer_handoff','dna':{},'limitations':['上游结论需复核；未附原始材料时不能验证原图或全文原创性。']}
    evidence={x['id']:x for x in data.get('evidence',[])}
    for key,cid in data.get('dna',{}).items():
        claim=data['claims'].get(cid)
        if not isinstance(claim,dict):
            result['limitations'].append('Missing claim: '+str(cid));continue
        ids=claim.get('evidence_ids',[])
        result['dna'][key]={'text':claim.get('text'),'upstream_type':claim.get('type'),'upstream_claim_id':cid,'evidence_ids':ids,'evidence':[evidence[e] for e in ids if e in evidence]}
        if any(e not in evidence for e in ids):result['limitations'].append('Missing evidence for '+str(cid))
    if not result['dna']:result['limitations'].append('未获取到可导入DNA，由宿主询问或根据已给原文提炼。')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--output',required=True);a=p.parse_args()
    Path(a.output).write_text(json.dumps(extract(json.loads(Path(a.input).read_text(encoding='utf-8-sig'))),ensure_ascii=False,indent=2),encoding='utf-8')
