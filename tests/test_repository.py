"""确保已发布技能的入口元信息、六节和本地reference链接未在分发时丢失。"""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    ROOT / "skills/reporting/method-selection-router/SKILL.md",
    ROOT / "skills/methods-core/t-test/SKILL.md",
    ROOT / "skills/methods-core/chi-square/SKILL.md",
)


class SkillDistributionTests(unittest.TestCase):
    def test_published_skill_names_descriptions_and_six_sections(self):
        names = set()
        for path in SKILLS:
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"))
                parts = text.split("---", 2)
                self.assertEqual(len(parts), 3)
                fields = dict(re.findall(r"^(name|description):\s*(.+)$", parts[1], flags=re.M))
                self.assertEqual(set(fields), {"name", "description"})
                self.assertEqual(fields["name"], path.parent.name)
                self.assertNotIn(fields["name"], names)
                names.add(fields["name"])
                sections = re.findall(r"^## ([1-6])\.\s+.+$", parts[2], flags=re.M)
                self.assertEqual(sections, [str(number) for number in range(1, 7)])

    def test_relative_links_and_reference_files_are_present(self):
        for skill in SKILLS:
            for path in [skill, *skill.parent.glob("references/*.md")]:
                with self.subTest(path=path.relative_to(ROOT)):
                    for target in re.findall(r"\]\(([^\s)]+)\)", path.read_text(encoding="utf-8")):
                        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                            continue
                        destination = (path.parent / target.split("#", 1)[0]).resolve()
                        self.assertTrue(destination.is_relative_to(ROOT), target)
                        self.assertTrue(destination.exists(), f"{path.relative_to(ROOT)} -> {target}")
        for method, files in {"t-test": ["assumptions.md", "examples.md"],
                              "chi-square": ["conditions.md", "examples.md"]}.items():
            for filename in files:
                self.assertTrue((ROOT / "skills/methods-core" / method / "references" / filename).is_file())


if __name__ == "__main__":
    unittest.main()
