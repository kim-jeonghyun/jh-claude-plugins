import os, unittest
HERE = os.path.dirname(__file__)
SKILL = os.path.join(HERE, "..", "SKILL.md")

class TestSkillMeta(unittest.TestCase):
    def test_frontmatter_and_description(self):
        with open(SKILL, encoding="utf-8") as f:
            text = f.read()
        self.assertTrue(text.startswith("---"))
        block = text.split("---", 2)[1]
        self.assertIn("name: x-study", block)
        desc = [l for l in block.splitlines() if l.startswith("description:")]
        self.assertEqual(len(desc), 1)
        self.assertLess(len(desc[0].split("description:", 1)[1].strip()), 120)

if __name__ == "__main__":
    unittest.main()
