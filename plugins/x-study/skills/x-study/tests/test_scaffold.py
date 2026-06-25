import json, os, unittest
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))

class TestScaffold(unittest.TestCase):
    def test_plugin_manifest_valid(self):
        with open(os.path.join(ROOT, "plugins/x-study/.claude-plugin/plugin.json")) as f:
            m = json.load(f)
        for key in ("name", "version", "description", "author"):
            self.assertIn(key, m)
        self.assertEqual(m["name"], "x-study")

    def test_registered_in_marketplace(self):
        with open(os.path.join(ROOT, ".claude-plugin/marketplace.json")) as f:
            mp = json.load(f)
        entry = next((x for x in mp["plugins"] if x["name"] == "x-study"), None)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["source"], "./plugins/x-study")

if __name__ == "__main__":
    unittest.main()
