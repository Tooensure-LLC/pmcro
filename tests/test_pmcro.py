import asyncio, importlib.util, json, pathlib, re, shutil, subprocess, sys, tempfile, unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("pmcro", REPO / "tools/pmcro.py")
pmcro = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pmcro)
RECORD = REPO / "plugins/pmcro-core/skills/trail-player/scripts/record.py"


class Sandbox(unittest.TestCase):
    """Copy the repo plugins into a temp tree and point the validator at it."""

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        shutil.copytree(REPO / "plugins", self.tmp / "plugins")
        self.old = (pmcro.ROOT, pmcro.PLUGINS)
        pmcro.ROOT, pmcro.PLUGINS = self.tmp, self.tmp / "plugins"
        self.skill = self.tmp / "plugins/pmcro-dotnet/skills/maf-local-skills"

    def tearDown(self):
        pmcro.ROOT, pmcro.PLUGINS = self.old
        shutil.rmtree(self.tmp)

    def errors(self):
        errs = []
        for p in pmcro.plugin_dirs():
            pmcro.load_plugin(p, errs)
            for sk in (p / "skills").iterdir():
                pmcro.check_skill(sk, errs)
        return errs

    def edit(self, rel, fn):
        f = self.tmp / rel
        f.write_text(fn(f.read_text()))


class ValidatorMustPass(Sandbox):
    def test_clean_tree_has_no_errors(self):
        self.assertEqual(self.errors(), [])


class ValidatorMustFail(Sandbox):
    def expect(self, fragment):
        errs = self.errors()
        self.assertTrue(any(fragment in e for e in errs), f"{fragment!r} not in {errs}")

    def test_non_spec_key(self):
        self.edit("plugins/pmcro-dotnet/skills/maf-local-skills/SKILL.md", lambda t: t.replace("license: MIT", "license: MIT\nmodel: x", 1))
        self.expect("non-spec frontmatter")

    def test_name_dir_mismatch(self):
        self.edit("plugins/pmcro-dotnet/skills/maf-local-skills/SKILL.md", lambda t: t.replace("name: maf-local-skills", "name: other", 1))
        self.expect("must equal directory")

    def test_long_description(self):
        self.edit("plugins/pmcro-dotnet/skills/maf-local-skills/SKILL.md", lambda t: t.replace("description: ", "description: " + "x" * 1100 + " ", 1))
        self.expect("1-1024")

    def test_too_many_lines(self):
        self.edit("plugins/pmcro-dotnet/skills/maf-local-skills/SKILL.md", lambda t: t + "\n" * 600)
        self.expect("limit 500")

    def test_missing_reference(self):
        (self.skill / "references/maf-api.md").unlink()
        self.expect("missing or outside")

    def test_nested_reference(self):
        (self.skill / "references/deep").mkdir()
        (self.skill / "references/deep/x.md").write_text("x")
        self.expect("one level deep")

    def test_secret(self):
        (self.skill / "references/maf-api.md").write_text("key sk-" + "a" * 30)
        self.expect("credential-shaped")

    def test_absolute_path(self):
        (self.skill / "references/maf-api.md").write_text("see /home/bob/x")
        self.expect("absolute path")

    def test_symlink(self):
        (self.skill / "assets/link.json").symlink_to(self.skill / "SKILL.md")
        self.expect("symlink")

    def test_bad_semver(self):
        self.edit("plugins/pmcro-core/plugin.json", lambda t: re.sub(r'"version": "[^"]+"', '"version": "latest"', t))
        self.expect("semver")

    def test_reserved_plugin_name(self):
        shutil.move(self.tmp / "plugins/pmcro-core", self.tmp / "plugins/claude-core")
        self.edit("plugins/claude-core/plugin.json", lambda t: t.replace("pmcro-core", "claude-core"))
        self.expect("reserved")

    def test_skills_path_escape(self):
        self.edit("plugins/pmcro-core/plugin.json", lambda t: t.replace("./skills/", "../x/"))
        self.expect("must start with ./")


class AdaptersAreCurrent(unittest.TestCase):
    def test_committed_adapters_match_generator(self):
        self.assertEqual(pmcro.cmd_gen(check=True), 0)

    def test_claude_manifest_has_no_schema_key(self):
        m = json.loads((REPO / "plugins/pmcro-core/.claude-plugin/plugin.json").read_text())
        self.assertNotIn("$schema", m)


class DocsLaw(Sandbox):
    """Each documentation rule has a must-fail case."""

    def setUp(self):
        super().setUp()
        for d in ("docs", "tools"):
            shutil.copytree(REPO / d, self.tmp / d)
        for f in ("README.md", "AGENTS.md"):
            shutil.copy(REPO / f, self.tmp / f)

    def docs_errors(self):
        errs = []
        pmcro.check_docs(errs)
        return errs

    def expect(self, fragment):
        errs = self.docs_errors()
        self.assertTrue(any(fragment in e for e in errs), f"{fragment!r} not in {errs}")

    def test_clean_tree_passes(self):
        self.assertEqual(self.docs_errors(), [])

    def test_missing_plugin_readme(self):
        (self.tmp / "plugins/pmcro-core/README.md").unlink()
        self.expect("README.md required")

    def test_readme_missing_section(self):
        self.edit("plugins/pmcro-core/README.md", lambda t: t.replace("## Status", "## Notes"))
        self.expect("missing section")

    def test_readme_must_name_every_skill(self):
        self.edit("plugins/pmcro-core/README.md", lambda t: t.replace("trail-player", "tp"))
        self.expect("not documented")

    def test_changelog_needs_current_version(self):
        self.edit("plugins/pmcro-core/plugin.json", lambda t: re.sub(r'"version": "[^"]+"', '"version": "9.9.9"', t))
        self.expect("CHANGELOG.md")

    def test_script_needs_docstring(self):
        (self.tmp / "plugins/pmcro-core/skills/trail-player/scripts/record.py").write_text("print('x')\n")
        self.expect("module docstring")

    def test_script_must_be_mentioned_in_its_skill(self):
        self.edit("plugins/pmcro-core/skills/trail-player/SKILL.md", lambda t: t.replace("record.py", "writer"))
        self.expect("not mentioned")

    def test_tool_needs_docstring(self):
        (self.tmp / "tools/extra.py").write_text("x = 1\n")
        self.expect("tools/extra.py")

    def test_doc_must_be_indexed(self):
        (self.tmp / "docs/orphan.md").write_text("orphan")
        self.expect("does not link")


def _check_script():
    p = REPO / "plugins/pmcro-content/skills/content-script/scripts/check_script.py"
    s = importlib.util.spec_from_file_location("check_script", p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m.check


GOOD = """---
title: T
duration_min: 1
synthetic_voice: false
synthetic_image: false
---
## Script
""" + " ".join(["word"] * 150) + """
## Claims
| Claim | Source |
| --- | --- |
| Water is wet | opinion |
## Disclosure
"""


class ContentScriptChecker(unittest.TestCase):
    def errs(self, text):
        return _check_script()(text)[0]

    def test_good_script_has_no_errors(self):
        self.assertEqual(self.errs(GOOD), [])

    def test_missing_front_matter(self):
        self.assertTrue(any("front matter" in e for e in self.errs("## Script\nhi")))

    def test_wrong_length(self):
        self.assertTrue(any("words" in e for e in self.errs(GOOD.replace("duration_min: 1", "duration_min: 5"))))

    def test_claim_without_source(self):
        self.assertTrue(any("no source" in e for e in self.errs(GOOD.replace("opinion", ""))))

    def test_no_claims_at_all(self):
        self.assertTrue(any("Claims" in e for e in self.errs(GOOD.replace("| Water is wet | opinion |\n", ""))))

    def test_synthetic_voice_needs_disclosure(self):
        bad = GOOD.replace("synthetic_voice: false", "synthetic_voice: true")
        self.assertTrue(any("Disclosure" in e for e in self.errs(bad)))
        ok = bad + "This video uses a synthetic voice.\n"
        self.assertEqual(self.errs(ok), [])

    def test_private_tier_marker_refused(self):
        self.assertTrue(any("private" in e for e in self.errs(GOOD + "\ntier: private\n")))
        self.assertTrue(any("private" in e for e in self.errs(GOOD + "\nsee .trail-local/private/0001\n")))

    def test_never_prints_a_checker_verdict(self):
        src = (REPO / "plugins/pmcro-content/skills/content-script/scripts/check_script.py").read_text()
        body = src.split('"""', 2)[2]
        self.assertNotRegex(body, r'print\(.*\b(PASS|LOOP|HALT)\b')


def _check_landing():
    p = REPO / "plugins/pmcro-cloudflare/skills/landing-page/scripts/check_landing.py"
    s = importlib.util.spec_from_file_location("check_landing", p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m.check


PAGE = """<html><head><title>T</title><meta name="description" content="d"></head><body>
<p>We earn a commission on purchases through links here.</p>
<a href="https://net.example/o?ref=1" rel="sponsored nofollow">Buy</a>
<a href="/privacy">Privacy policy</a></body></html>"""


class LandingPageChecker(unittest.TestCase):
    def errs(self, html, domains=("net.example",)):
        return _check_landing()(html, domains)[0]

    def test_good_page_has_no_errors(self):
        self.assertEqual(self.errs(PAGE), [])

    def test_shipped_template_passes(self):
        t = (REPO / "plugins/pmcro-cloudflare/skills/landing-page/assets/landing-template.html").read_text()
        self.assertEqual(self.errs(t, ("example-network.com",)), [])

    def test_missing_title_and_meta(self):
        self.assertTrue(any("title" in e for e in self.errs(PAGE.replace("<title>T</title>", ""))))
        self.assertTrue(any("meta" in e for e in self.errs(PAGE.replace('<meta name="description" content="d">', ""))))

    def test_affiliate_link_needs_sponsored(self):
        self.assertTrue(any("sponsored" in e for e in self.errs(PAGE.replace("sponsored nofollow", "nofollow"))))

    def test_disclosure_must_come_before_first_affiliate_link(self):
        late = PAGE.replace("<p>We earn a commission on purchases through links here.</p>", "")
        late = late.replace("</body>", "<p>We earn a commission.</p></body>")
        self.assertTrue(any("disclosure" in e for e in self.errs(late)))

    def test_ref_query_key_detected_without_domain_list(self):
        no_rel = PAGE.replace(' rel="sponsored nofollow"', "")
        self.assertTrue(any("sponsored" in e for e in self.errs(no_rel, ())))

    def test_income_promises_refused(self):
        self.assertTrue(any("income" in e for e in self.errs(PAGE.replace("Buy", "Guaranteed income, get rich"))))

    def test_privacy_link_required(self):
        self.assertTrue(any("privacy" in e for e in self.errs(PAGE.replace("Privacy policy", "Terms"))))

    def test_token_refused(self):
        self.assertTrue(any("credential" in e for e in self.errs(PAGE + "ghp_" + "a" * 36)))

    def test_never_prints_a_checker_verdict(self):
        src = (REPO / "plugins/pmcro-cloudflare/skills/landing-page/scripts/check_landing.py").read_text()
        self.assertNotRegex(src.split('"""', 2)[2], r'print\(.*\b(PASS|LOOP|HALT)\b')


QUEUE = REPO / "plugins/pmcro-core/skills/inbox/scripts/queue.py"


class InboxQueue(unittest.TestCase):
    def setUp(self):
        self.repo = pathlib.Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        (self.repo / ".gitignore").write_text(".trail-local/\n")

    def tearDown(self):
        shutil.rmtree(self.repo)

    def q(self, *args):
        return subprocess.run([sys.executable, str(QUEUE), *args], cwd=self.repo, capture_output=True, text=True)

    def add(self, text, tier="private", pri="2", source="founder"):
        return self.q("add", "--tier", tier, "--text", text, "--priority", pri, "--source", source)

    def test_add_then_list(self):
        self.assertIn("queued #0001", self.add("hello").stdout)
        self.assertIn("queued", self.q("list", "--tier", "private").stdout)

    def test_duplicate_text_returns_existing_item(self):
        self.add("same")
        r = self.add("same")
        self.assertIn("duplicate", r.stdout)
        self.assertEqual(len(list((self.repo / ".trail-local/private/inbox").glob("0*.json"))), 1)

    def test_next_is_priority_then_oldest(self):
        self.add("low", pri="3")
        self.add("old normal", pri="2")
        self.add("urgent", pri="0")
        self.assertIn("urgent", self.q("next", "--tier", "private").stdout)
        self.q("claim", "0003", "--tier", "private", "--by", "planner")
        self.assertIn("old normal", self.q("next", "--tier", "private").stdout)

    def test_second_claim_refused(self):
        self.add("work")
        self.assertEqual(self.q("claim", "0001", "--tier", "private", "--by", "a").returncode, 0)
        r = self.q("claim", "0001", "--tier", "private", "--by", "b")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("already claimed", r.stderr)

    def test_done_requires_claim(self):
        self.add("work")
        r = self.q("done", "0001", "--tier", "private", "--by", "maker")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("must be claimed", r.stderr)

    def test_full_lifecycle_and_log_is_append_only(self):
        self.add("work")
        self.q("claim", "0001", "--tier", "private", "--by", "planner")
        self.q("done", "0001", "--tier", "private", "--by", "planner", "--note", "ok", "--ref", "0007")
        d = self.repo / ".trail-local/private/inbox"
        events = [json.loads(x)["event"] for x in (d / "0001.events.jsonl").read_text().splitlines()]
        self.assertEqual(events, ["queued", "claimed", "done"])
        self.assertIn("done", self.q("list", "--tier", "private", "--status", "done").stdout)
        self.assertNotIn("0001", self.q("next", "--tier", "private").stdout)

    def test_message_text_is_stored_verbatim_and_never_rewritten(self):
        self.add("  Messy   words ,, as typed  ")
        d = self.repo / ".trail-local/private/inbox"
        before = (d / "0001.json").read_text()
        self.q("claim", "0001", "--tier", "private", "--by", "x")
        self.assertEqual((d / "0001.json").read_text(), before)
        self.assertEqual(json.loads(before)["text"], "  Messy   words ,, as typed  ")

    def test_private_refused_when_not_gitignored(self):
        (self.repo / ".gitignore").write_text("")
        r = self.add("secret")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not gitignored", r.stderr)

    def test_empty_message_refused(self):
        self.assertNotEqual(self.add("   ").returncode, 0)

    def test_public_tier_goes_to_trail_dir(self):
        self.add("announce", tier="public")
        self.assertTrue((self.repo / "trail/public/inbox/0001.json").is_file())


class UpstreamPins(Sandbox):
    def setUp(self):
        super().setUp()
        self.up = self.tmp / "upstream.json"
        shutil.copy(REPO / "upstream.json", self.up)

    def check(self, mutate):
        data = json.loads(self.up.read_text())
        mutate(data["upstreams"])
        self.up.write_text(json.dumps(data))
        errs = []
        pmcro.check_upstreams(errs)
        return errs

    def test_shipped_pins_are_clean(self):
        self.assertEqual(self.check(lambda u: None), [])

    def test_branch_instead_of_sha_refused(self):
        errs = self.check(lambda u: u[0].update(sha="main"))
        self.assertTrue(any("40-character" in e for e in errs))

    def test_short_or_uppercase_sha_refused(self):
        self.assertTrue(self.check(lambda u: u[0].update(sha=u[0]["sha"][:7])))
        self.assertTrue(self.check(lambda u: u[0].update(sha=u[0]["sha"].upper())))

    def test_duplicate_name_refused(self):
        errs = self.check(lambda u: u[1].update(name=u[0]["name"]))
        self.assertTrue(any("duplicate" in e for e in errs))

    def test_clash_with_local_plugin_refused(self):
        errs = self.check(lambda u: u[0].update(name="pmcro-core"))
        self.assertTrue(any("duplicate" in e for e in errs))

    def test_path_escape_refused(self):
        self.assertTrue(self.check(lambda u: u[0].update(path="../x")))


class UpstreamEntriesInMarketplace(unittest.TestCase):
    def test_claude_file_lists_pinned_git_subdir_entries(self):
        m = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
        subdir = [p for p in m["plugins"] if isinstance(p["source"], dict)]
        self.assertEqual(len(subdir), len(pmcro.upstreams()))
        self.assertIn("dotnet-maui", {p["name"] for p in subdir})
        for p in subdir:
            self.assertEqual(p["source"]["source"], "git-subdir")
            self.assertRegex(p["source"]["sha"], r"^[0-9a-f]{40}$")

    def test_other_hosts_get_local_plugins_only(self):
        for f in (".cursor-plugin", ".github/plugin"):
            m = json.loads((REPO / f / "marketplace.json").read_text())
            self.assertTrue(all(isinstance(p["source"], str) for p in m["plugins"]), f)


class MafProgressiveDisclosure(unittest.TestCase):
    def test_all_skills_reachable_with_files(self):
        try:
            from agent_framework import FileSkillsSource, SkillsSourceContext
        except ImportError:
            self.skipTest("agent-framework not installed")
        found = {}
        for d in (REPO / "plugins").glob("*/skills"):
            for s in asyncio.run(FileSkillsSource(d).get_skills(SkillsSourceContext(None))):
                found[s.frontmatter.name] = s
        expected = {"orchestrate", "plan", "make", "check", "reflect", "trail-player", "maf-local-skills", "mcp-local-models", "content-script", "landing-page", "inbox",
                    "ceo", "cfo", "chief-of-staff", "chro", "clo", "cmo", "coo", "cro", "cto"}
        self.assertEqual(set(found), expected)
        tp = found["trail-player"]
        self.assertEqual([r.name for r in tp._resources], ["references/tiers.md"])
        self.assertEqual([r.name for r in tp._scripts], ["scripts/record.py"])


class TrailPlayerGuards(unittest.TestCase):
    def setUp(self):
        self.repo = pathlib.Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        (self.repo / "e.txt").write_text("body")

    def tearDown(self):
        shutil.rmtree(self.repo)

    def run_rec(self, *args):
        return subprocess.run([sys.executable, str(RECORD), *args, "--body-file", str(self.repo / "e.txt")],
                              cwd=self.repo, capture_output=True, text=True)

    def test_private_refused_when_not_ignored(self):
        r = self.run_rec("--tier", "private", "--kind", "habit")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not gitignored", r.stderr)

    def test_private_written_when_ignored(self):
        (self.repo / ".gitignore").write_text(".trail-local/\n")
        r = self.run_rec("--tier", "private", "--kind", "habit")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_roundtable_needs_seats(self):
        (self.repo / ".gitignore").write_text(".trail-local/\n")
        r = self.run_rec("--tier", "roundtable", "--kind", "secret")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("seats", r.stderr)

    def test_entries_are_numbered_and_never_overwritten(self):
        (self.repo / ".gitignore").write_text(".trail-local/\n")
        self.run_rec("--tier", "private", "--kind", "note")
        self.run_rec("--tier", "private", "--kind", "note")
        names = sorted(p.name for p in (self.repo / ".trail-local/private").glob("*.json"))
        self.assertEqual(names, ["0001-note.json", "0002-note.json"])


def _load_mcp():
    p = REPO / "plugins/pmcro-dotnet/skills/mcp-local-models/scripts/load_mcp.py"
    s = importlib.util.spec_from_file_location("load_mcp", p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


ECHO = {"servers": {"echo": {
    "transport": "stdio", "command": sys.executable, "args": [str(REPO / "tests/fixtures/echo_mcp.py")],
    "roles": {"checker": {"allowed_tools": ["read_note"]},
              "maker": {"allowed_tools": ["read_note", "write_note"], "approval": "always_require"}}}}}


class McpConfigRules(unittest.TestCase):
    def errs(self, **server):
        cfg = {"servers": {"s": {"transport": "http", "url": "https://x.example/mcp",
                                 "roles": {"maker": {"allowed_tools": ["a"]}}, **server}}}
        return _load_mcp().check(cfg)

    def test_clean_config_passes(self):
        self.assertEqual(self.errs(), [])
        self.assertEqual(_load_mcp().check(ECHO), [])

    def test_inline_token_refused(self):
        self.assertTrue(any("credential" in e for e in self.errs(note="ghp_" + "a" * 36)))

    def test_plain_http_refused_but_loopback_ok(self):
        self.assertTrue(any("https" in e for e in self.errs(url="http://remote.example/mcp")))
        self.assertEqual(self.errs(url="http://localhost:8080/mcp"), [])

    def test_missing_allow_list_refused(self):
        self.assertTrue(any("allowed_tools" in e for e in self.errs(roles={"maker": {}})))

    def test_env_name_must_be_a_name_not_a_value(self):
        self.assertTrue(any("NAME" in e for e in self.errs(headers_from_env={"Authorization": "secret value"})))

    def test_shipped_example_passes(self):
        cfg = json.loads((REPO / "plugins/pmcro-dotnet/skills/mcp-local-models/assets/mcp-servers.example.json").read_text())
        self.assertEqual(_load_mcp().check(cfg), [])


class McpThroughMaf(unittest.TestCase):
    """Real MCP calls over stdio: the Checker role must not even see the write tool."""

    def names(self, role):
        try:
            import agent_framework  # noqa: F401
        except ImportError:
            self.skipTest("agent-framework not installed")

        async def go():
            out = []
            for tool in _load_mcp().build_tools(ECHO, role):
                async with tool:
                    out += [(f.name, getattr(f, "approval_mode", None)) for f in tool.functions]
            return out
        return asyncio.run(go())

    def test_checker_sees_only_read_tool(self):
        self.assertEqual([n for n, _ in self.names("checker")], ["read_note"])

    def test_maker_sees_both_and_needs_approval(self):
        got = dict(self.names("maker"))
        self.assertEqual(set(got), {"read_note", "write_note"})
        self.assertTrue(all(v == "always_require" for v in got.values()))

    def test_unlisted_role_gets_nothing(self):
        self.assertEqual(self.names("reflector"), [])


if __name__ == "__main__":
    unittest.main()
