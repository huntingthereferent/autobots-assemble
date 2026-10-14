#!/usr/bin/env python3
"""Verify archived original file bytes and stage reconstruction locally."""
import hashlib, json, tempfile, unittest
from pathlib import Path
from assemble import reconstruct
ROOT=Path(__file__).resolve().parent
class ArchiveVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.m=json.loads((ROOT/'MANIFEST.json').read_text(encoding='utf-8'))
    def test_exact_original_payload_count_and_stage_sizes(self):
        self.assertEqual(len(self.m['files']),281)
        self.assertEqual([s['added_file_count'] for s in self.m['stages']],[201]+[8]*10)
        self.assertEqual([s['cumulative_file_count'] for s in self.m['stages']],[201+8*k for k in range(11)])
    def test_all_original_file_digests(self):
        for name,v in self.m['files'].items():
            with self.subTest(name=name):
                self.assertEqual(Path(name).name,name)
                b=(ROOT/v['path']).read_bytes()
                self.assertEqual(hashlib.sha256(b).hexdigest(),v['sha256'])
                self.assertEqual(len(b),v['size'])
    def test_each_checkpoint_assembles_without_misplacing_old_files(self):
        with tempfile.TemporaryDirectory() as temp:
            for stage in range(20,31):
                dest=Path(temp)/str(stage)
                reconstruct(stage,dest)
                self.assertEqual(len(list(dest.iterdir())),201+8*(stage-20))
                for name,row in self.m['files'].items():
                    if row['stage']<=stage:
                        self.assertEqual(hashlib.sha256((dest/name).read_bytes()).hexdigest(),row['sha256'])
                    else:self.assertFalse((dest/name).exists())
    def test_assembler_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'working';p.mkdir()
            (p/'keep.txt').write_text('no overwrite')
            with self.assertRaises(FileExistsError):reconstruct(30,p)
            self.assertEqual((p/'keep.txt').read_text(),'no overwrite')
if __name__=='__main__':unittest.main()
