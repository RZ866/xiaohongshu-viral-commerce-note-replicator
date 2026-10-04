"""Exercise the real host installer, replacing HTTP only with this release ZIP."""
import argparse,importlib.util,subprocess,sys,tempfile
from pathlib import Path
def run(installer,package):
    installer=Path(installer);sys.path.insert(0,str(installer.parent));spec=importlib.util.spec_from_file_location('official_installer',installer);module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    requested=[]
    def local(url):requested.append(url);return Path(package).read_bytes()
    module._request=local;name='xiaohongshu-viral-commerce-note-replicator'
    with tempfile.TemporaryDirectory(prefix='replicator-install-test-') as tmp:
        args=['--url','https://github.com/example-owner/'+name,'--path','.','--name',name,'--method','download','--dest',tmp]
        assert module.main(args)==0
        for p in ['SKILL.md','scripts/generate_report.py','assets/report.html','references/originality-rules.md']:assert (Path(tmp)/name/p).is_file()
        assert not (Path(tmp)/name/'.qa').exists()
        assert requested==['https://codeload.github.com/example-owner/'+name+'/zip/main']
        output=Path(tmp)/'generated/report.html'
        subprocess.run([sys.executable,'scripts/generate_report.py','examples/text/input.json','--output',str(output),'--media-root','examples/media'],cwd=Path(tmp)/name,check=True,capture_output=True)
        assert 'ORIGINAL PLAN C' in output.read_text(encoding='utf-8')
        assert (output.parent/'original-notes.md').is_file()
        assert module.main(args)==1
    print('PASS real installer URL/root/copy/installed rendering/duplicate protection; local ZIP response, not a live GitHub installation')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--installer',required=True);p.add_argument('--package',required=True);a=p.parse_args();run(a.installer,a.package)
