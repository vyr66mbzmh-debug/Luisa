"""Offline inventories must close image dependencies and reject incomplete practice."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('offline_manifest',Path(__file__).resolve().parents[1]/'scripts/offline_manifest.py')
offline=importlib.util.module_from_spec(spec);spec.loader.exec_module(offline)

class OfflineInventory(unittest.TestCase):
    def fixture(self,root,missing=False):
        files={'index.html':'<title>Luisa</title>','release.json':'{"version":"0.26"}',
               'teaching-catalogue.js':'window.LUISA_TEACHING={};',
               'content/test.json':json.dumps([{'question':'<img src="assets/diagram.svg">','steps':['Answer']}]),
               'assets/diagram.svg':'<svg xmlns="http://www.w3.org/2000/svg"><image href="detail.svg"/></svg>'}
        if not missing:files['assets/detail.svg']='<svg xmlns="http://www.w3.org/2000/svg"/>'
        files['textbook-catalogue.json']=json.dumps({'books':[{'id':'test','title':'Test','course':'test','chapters':[{'id':'1','title':'One','resources':[]}]}],'questions':[{'skill':'test','targets':[{'book':'test','chapter':'1'}]}]})
        entries={}
        for name,data in files.items():
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data)
            entries[name]={'sha256':hashlib.sha256(data.encode()).hexdigest(),'bytes':len(data.encode())}
        return entries

    def test_nested_svg_is_required_and_hashed_PWA_001(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);entries=self.fixture(root);result=offline.generate(root,entries,'0.26')
            self.assertIn('assets/detail.svg',result['packs'][0]['files'])
            self.assertEqual(result['files']['assets/detail.svg'],entries['assets/detail.svg'])
            self.assertIn('Teaching slides',result['packs'][0]['unavailable'])
            self.assertIn('offline-catalogue.json',entries)

    def test_missing_nested_dependency_fails_PWA_001(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);entries=self.fixture(root,missing=True)
            with self.assertRaisesRegex(ValueError,'Unresolved nested offline dependency'):
                offline.generate(root,entries,'0.26')

    def test_print_and_practice_PDFs_required_LIB_028(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);entries=self.fixture(root)
            def put(name,data):
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data)
                entries[name]={'sha256':hashlib.sha256(data.encode()).hexdigest(),'bytes':len(data)}
            put('data.js','window.FMQ_LIBRARY='+json.dumps({'courses':[{'id':'maths-a-level','books':[{'id':'test','title':'Test','topics':[{'printoutPath':'topic.pdf','skills':[{'id':'test','printoutPath':'skill.pdf','questions':[1]}]}]}]}]})+';')
            for name in ['topic.pdf','skill.pdf','practice.pdf']:put(name,'%PDF-fixture')
            cat=json.loads((root/'textbook-catalogue.json').read_text());cat['books'][0]['chapters'][0]['resources']=[{'type':'practice','access':'available','url':'practice.pdf'}]
            put('textbook-catalogue.json',json.dumps(cat))
            result=offline.generate(root,entries,'0.28')
            self.assertTrue({'topic.pdf','skill.pdf','practice.pdf'}<=set(result['packs'][0]['files']))
            del entries['skill.pdf']
            with self.assertRaisesRegex(ValueError,'Offline print PDF missing'):offline.generate(root,entries,'0.28')

    def test_inventory_revision_changes_with_actual_bytes_PWA_001(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);entries=self.fixture(root);first=offline.generate(root,entries,'0.26')
            content='<svg><!-- revised --></svg>';p=root/'assets/detail.svg';p.write_text(content)
            entries['assets/detail.svg']={'sha256':hashlib.sha256(content.encode()).hexdigest(),'bytes':len(content)}
            second=offline.generate(root,entries,'0.26')
            self.assertNotEqual(first['revision'],second['revision'])

if __name__=='__main__':unittest.main()
