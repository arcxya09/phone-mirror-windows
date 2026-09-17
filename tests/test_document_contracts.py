"""Document-contract checks only; no phone or Windows runtime is exercised."""
from __future__ import annotations
import copy
import json
import tempfile
import unittest
from pathlib import Path
from jsonschema import ValidationError
from tools.verify_docs import ROOT, check_package, local_link_errors, manifest_text, validate_contract


class DocumentContractTests(unittest.TestCase):
    def setUp(self):
        self.ipc = json.loads((ROOT / 'examples/ipc-insert-text.json').read_text(encoding='utf-8'))
        self.settings = json.loads((ROOT / 'examples/application-settings.json').read_text(encoding='utf-8'))

    def test_package_consistency(self):
        self.assertEqual([], check_package(ROOT))

    def test_settings_example(self):
        validate_contract(ROOT, self.settings, 'application-settings.schema.json')

    def test_no_automatic_clipboard_sync(self):
        self.settings['clipboardAutosync'] = True
        with self.assertRaises(ValidationError):
            validate_contract(ROOT, self.settings, 'application-settings.schema.json')

    def test_unknown_settings_field(self):
        self.settings['recordScreen'] = True
        with self.assertRaises(ValidationError):
            validate_contract(ROOT, self.settings, 'application-settings.schema.json')

    def test_text_example(self):
        validate_contract(ROOT, self.ipc, 'local-ipc.schema.json')

    def test_no_implicit_enter(self):
        self.ipc['payload']['appendEnter'] = True
        with self.assertRaises(ValidationError):
            validate_contract(ROOT, self.ipc, 'local-ipc.schema.json')

    def test_sequence_required(self):
        del self.ipc['inputSequence']
        with self.assertRaises(ValidationError):
            validate_contract(ROOT, self.ipc, 'local-ipc.schema.json')

    def test_sequence_overflow(self):
        self.ipc['inputSequence'] = str(1 << 64)
        with self.assertRaises(ValueError):
            validate_contract(ROOT, self.ipc, 'local-ipc.schema.json')

    def test_utf8_boundary(self):
        self.ipc['payload']['text'] = 'a' * 16384
        validate_contract(ROOT, self.ipc, 'local-ipc.schema.json')
        self.ipc['payload']['text'] = '中' * 6000
        with self.assertRaises(ValueError):
            validate_contract(ROOT, self.ipc, 'local-ipc.schema.json')

    def test_unknown_method(self):
        self.ipc['method'] = 'RunShell'
        with self.assertRaises(ValidationError):
            validate_contract(ROOT, self.ipc, 'local-ipc.schema.json')

    def test_empty_text(self):
        self.ipc['payload']['text'] = ''
        with self.assertRaises(ValidationError):
            validate_contract(ROOT, self.ipc, 'local-ipc.schema.json')

    def test_stop_has_no_text(self):
        stop = copy.deepcopy(self.ipc)
        stop.update(method='Stop', payload={})
        del stop['inputSequence']
        validate_contract(ROOT, stop, 'local-ipc.schema.json')
        stop['payload']['text'] = 'unexpected'
        with self.assertRaises(ValidationError):
            validate_contract(ROOT, stop, 'local-ipc.schema.json')

    def test_link_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'a.md').write_text('[bad](missing.md)\n', encoding='utf-8')
            self.assertEqual(1, len(local_link_errors(root)))
            (root / 'missing.md').write_text('test\n', encoding='utf-8')
            self.assertEqual([], local_link_errors(root))

    def test_manifest_changes_with_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / 'a.md'
            p.write_text('a\n', encoding='utf-8')
            first = manifest_text(root)
            p.write_text('b\n', encoding='utf-8')
            self.assertNotEqual(first, manifest_text(root))


if __name__ == '__main__':
    unittest.main()
