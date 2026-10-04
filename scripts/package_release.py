"""Package the public allowlist; never include private task materials or QA caches."""
import hashlib,json,re,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NAME='xiaohongshu-viral-commerce-note-replicator'
FILES={'SKILL.md','README.md','LICENSE','CHANGELOG.md','VERSION','.gitignore','.gitattributes'}
DIRS={'agents','references','scripts','assets','examples','tests','.github'}
EXCLUDE={'.git','.qa','dist','outputs','private-inputs','__pycache__','.venv','node_modules'}
PATTERNS={
 'private-key':r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
 'credential':r'\b(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-(?:proj-)?[A-Za-z0-9_-]{35,})',
 'personal-path':r'(?i)(?:[A-Z]:[/\\](?:Users|用户)[/\\][A-Za-z0-9_.\u4e00-\u9fff -]+[/\\]|/(?:Users|home)/[A-Za-z0-9_.-]+/)',
 'secret-assignment':r'''(?i)(?:api[_-]?key|password|web_session|access_token)\s*[=:]\s*["']([A-Za-z0-9_-]{24,})["']''',
}
def public_files(root=ROOT):
    result=[]
    for p in root.rglob('*'):
        rel=p.relative_to(root)
        if any(x in EXCLUDE for x in rel.parts) or p.suffix=='.pyc':continue
        if p.is_symlink():raise ValueError('public symlink')
        if p.is_file() and (str(rel) in FILES or rel.parts[0] in DIRS):result.append(p)
    return sorted(result)
def audit(files,root=ROOT):
    found=[]
    for p in files:
        rel=p.relative_to(root).as_posix()
        if p.name.startswith('.env') or p.suffix=='.key' or any(x in p.name.lower() for x in ['credentials','cookies','secrets']):found.append((rel,'private filename'))
        if p.suffix.lower() in ('.png','.jpg','.jpeg','.webp'):
            if p.relative_to(root).parts[0] not in ('assets','examples'):found.append((rel,'unexpected image'))
            continue
        value=p.read_text(encoding='utf-8-sig')
        for key,pattern in PATTERNS.items():
            if re.search(pattern,value):found.append((rel,key))
    return found
def main():
    files=public_files();findings=audit(files)
    for name in ('SKILL.md','README.md','LICENSE','CHANGELOG.md','references/dna-migration-framework.md','references/originality-rules.md','references/html-report-spec.md','scripts/generate_report.py','tests/test_report.py'):
        if not (ROOT/name).is_file():findings.append((name,'missing'))
    if findings:print(json.dumps(findings));return 1
    dest=ROOT/'dist';dest.mkdir(exist_ok=True);archive=dest/(NAME+'-v'+(ROOT/'VERSION').read_text().strip()+'.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in files:z.write(p,NAME+'/'+p.relative_to(ROOT).as_posix())
    result={'files':len(files),'findings':findings,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'archive':archive.name,'scope':'Public allowlist pattern audit; original images reviewed manually, not a proof of all semantic privacy.'}
    (dest/'release-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result));return 0
if __name__=='__main__':sys.exit(main())
