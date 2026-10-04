import re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from package_release import public_files,audit,PATTERNS
class PackageTests(unittest.TestCase):
    def test_public_audit(self):self.assertEqual(audit(public_files()),[])
    def test_secret_pattern(self):self.assertIsNotNone(re.search(PATTERNS['credential'],'ghp_'+'a'*36))
    def test_personal_path_pattern(self):self.assertIsNotNone(re.search(PATTERNS['personal-path'],'C:'+ '/Users/'+'example/file.txt'))
    def test_no_private_outputs(self):
        for p in public_files():self.assertFalse(set(p.relative_to(ROOT).parts)&{'.qa','outputs','dist','private-inputs'})
if __name__=='__main__':unittest.main()
