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

    def test_directory_reference_ok_when_it_exists_and_refused_when_missing(self):
        f = "plugins/pmcro-dotnet/skills/maf-local-skills/SKILL.md"
        self.edit(f, lambda t: t + "\nSee `assets/` for examples.\n")
        self.assertEqual(self.errors(), [])
        self.edit(f, lambda t: t + "\nSee `assets/nope/` too.\n")
        self.assertTrue(any("missing or outside" in e for e in self.errors()))

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
        return self.q("add", "--tier", tier, "--text", text, "--priority", pri, "--source", source, "--reason", "test")

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

    def test_priority_zero_needs_a_reason(self):
        r = self.q("add", "--tier", "private", "--text", "urgent", "--priority", "0")
        self.assertEqual(r.returncode, 1)
        self.assertIn("needs --reason", r.stderr)

    def test_reprioritize_is_logged_and_changes_order(self):
        self.add("first", pri="2")
        self.add("second", pri="2")
        self.assertIn("first", self.q("next", "--tier", "private").stdout)
        r = self.q("reprioritize", "0002", "--tier", "private", "--priority", "1", "--reason", "unblocks others", "--by", "planner")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("second", self.q("next", "--tier", "private").stdout)
        self.assertIn("p1 queued", self.q("list", "--tier", "private").stdout)
        events = (self.repo / ".trail-local/private/inbox/0002.events.jsonl").read_text()
        self.assertIn("unblocks others", events)
        self.assertEqual(self.q("claim", "0002", "--tier", "private", "--by", "x").returncode, 0)

    def test_reprioritize_rules(self):
        self.add("founder item", pri="1")
        no_reason = self.q("reprioritize", "0001", "--tier", "private", "--priority", "0", "--reason", " ", "--by", "planner")
        self.assertEqual(no_reason.returncode, 1)
        lower = self.q("reprioritize", "0001", "--tier", "private", "--priority", "3", "--reason", "meh", "--by", "planner")
        self.assertEqual(lower.returncode, 1)
        self.assertIn("only the founder may lower", lower.stderr)
        self.assertEqual(self.q("reprioritize", "0001", "--tier", "private", "--priority", "3", "--reason", "decided", "--by", "founder").returncode, 0)
        self.q("claim", "0001", "--tier", "private", "--by", "a")
        self.q("done", "0001", "--tier", "private", "--by", "a")
        self.assertEqual(self.q("reprioritize", "0001", "--tier", "private", "--priority", "0", "--reason", "x", "--by", "a").returncode, 1)

    def test_stale_lists_only_old_queued_items(self):
        self.add("fresh")
        self.assertIn("empty", self.q("list", "--tier", "private", "--stale", "14").stdout)
        f = self.repo / ".trail-local/private/inbox/0001.json"
        m = json.loads(f.read_text()); m["time"] = "2020-01-01T00:00:00+00:00"; f.write_text(json.dumps(m))
        self.assertIn("fresh", self.q("list", "--tier", "private", "--stale", "14").stdout)

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


class NewPluginScaffold(DocsLaw):
    def run_new(self, name="pmcro-demo", skill=None):
        return pmcro.cmd_new_plugin(name, "Demo plugin.", skill or "demo", "Use when demoing the scaffold.")

    def test_scaffold_creates_a_plugin_that_passes_every_rule(self):
        self.assertEqual(self.run_new(), 0)
        self.assertEqual(self.errors(), [])
        self.assertEqual(self.docs_errors(), [])
        self.assertTrue((self.tmp / "plugins/pmcro-demo/.claude-plugin/plugin.json").is_file())

    def test_scaffold_refuses_bad_name_and_reserved_word(self):
        self.assertEqual(self.run_new("Bad_Name"), 2)
        self.assertEqual(self.run_new("claude-demo"), 2)

    def test_scaffold_refuses_existing_plugin(self):
        self.assertEqual(self.run_new("pmcro-core"), 2)

    def test_scaffold_refuses_overlong_skill_description(self):
        self.assertEqual(pmcro.cmd_new_plugin("pmcro-demo", "d", "demo", "x" * 1100), 2)

    def test_scaffolded_skill_still_carries_visible_todos(self):
        self.run_new()
        self.assertIn("TODO", (self.tmp / "plugins/pmcro-demo/skills/demo/SKILL.md").read_text())


class CloudflareMcpConfig(unittest.TestCase):
    PATH = REPO / "plugins/pmcro-cloudflare/skills/landing-page/assets/cloudflare-mcp-servers.json"
    CHANGING = re.compile(r"create|delete|start|cancel|kill|write|update|put|deploy|purge|edit|remove", re.I)

    def cfg(self):
        return json.loads(self.PATH.read_text())

    def test_config_passes_the_mcp_checker(self):
        self.assertEqual(_load_mcp().check(self.cfg()), [])

    def test_no_allow_list_contains_a_changing_tool(self):
        for name, s in self.cfg()["servers"].items():
            for role, r in s["roles"].items():
                for tool in r["allowed_tools"]:
                    self.assertIsNone(self.CHANGING.search(tool), f"{name}/{role}: {tool}")

    def test_checker_role_has_no_more_tools_than_maker_where_both_exist(self):
        for name, s in self.cfg()["servers"].items():
            if "checker" in s["roles"] and "maker" in s["roles"]:
                self.assertLessEqual(set(s["roles"]["checker"]["allowed_tools"]), set(s["roles"]["maker"]["allowed_tools"]), name)

    def test_code_mode_server_is_not_configured(self):
        self.assertNotIn("mcp.cloudflare.com/mcp", json.dumps([s["url"] for s in self.cfg()["servers"].values() if s["url"].split("//")[1].startswith("mcp.")]))

    def test_every_server_uses_https_and_an_env_var_name(self):
        for name, s in self.cfg()["servers"].items():
            self.assertTrue(s["url"].startswith("https://"), name)
            self.assertEqual(s["headers_from_env"], {"Authorization": "CLOUDFLARE_MCP_AUTH"}, name)


FIG = REPO / "plugins/pmcro-figma/skills/figma-plugin-factory/scripts"


def _fig(name):
    s = importlib.util.spec_from_file_location(name, FIG / f"{name}.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


class FigmaRenderer(unittest.TestCase):
    def setUp(self):
        self.r = _fig("render_template")
        self.meta = json.loads((self.r.ROOT / "grid-frames/template.json").read_text())
        self.tmp = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def render(self, **given):
        d, meta = self.r.load("grid-frames")
        vals = self.r.values(meta, {k: str(v) for k, v in given.items()})
        return self.r.render((d / "code.ts.tmpl").read_text(), vals), self.r.render((d / "ui.html.tmpl").read_text(), vals)

    def test_defaults_render_and_lint_clean(self):
        code, ui = self.render()
        self.assertEqual(_fig("lint_plugin").lint(code, ui), [])

    def test_int_out_of_range_refused(self):
        with self.assertRaises(SystemExit):
            self.render(count=101)

    def test_non_integer_refused(self):
        with self.assertRaises(SystemExit):
            self.render(count="abc")

    def test_unknown_parameter_refused(self):
        with self.assertRaises(SystemExit):
            self.render(nonsense=1)

    def test_multiline_string_refused(self):
        with self.assertRaises(SystemExit):
            self.render(prefix="a\nb")

    def test_hostile_text_cannot_break_out_of_html_or_script(self):
        code, ui = self.render(prefix='"><script>alert(1)</script>', plugin_title="x */ evil(); /*")
        self.assertNotIn("<script>alert(1)</script>", ui)
        self.assertNotIn("*/ evil", code)

    def test_js_filter_escapes_script_close_and_quotes(self):
        out = self.r.fmt('a"b</script>', "js")
        self.assertNotIn("</", out)
        self.assertTrue(out.startswith('"') and out.endswith('"'))

    def test_template_limits_match_code_clamps(self):
        code, _ = self.render()
        for p in self.meta["params"]:
            if p["type"] == "int" and p["name"] in ("columns", "width", "height", "gap"):
                self.assertIn(f"{p['min']}, {p['max']}", code, p["name"])

    def test_unknown_template_refused(self):
        with self.assertRaises(SystemExit):
            self.r.load("nope")


class FigmaLinter(unittest.TestCase):
    def setUp(self):
        self.lint = _fig("lint_plugin").lint
        r = _fig("render_template")
        d, meta = r.load("grid-frames")
        v = r.values(meta, {})
        self.code, self.ui = r.render((d / "code.ts.tmpl").read_text(), v), r.render((d / "ui.html.tmpl").read_text(), v)

    def has(self, rule, code=None, ui=None):
        errs = self.lint(self.code if code is None else code, self.ui if ui is None else ui)
        self.assertTrue(any(rule in e for e in errs), f"{rule} not in {errs}")

    def test_F001_show_ui(self):
        self.has("F001", code=self.code.replace("figma.showUI(__html__", "figma.showUI('x'"))

    def test_F002_structure(self):
        self.has("F002", ui=self.ui.replace("<fig-footer>", "<div>"))

    def test_F003_network(self):
        self.has("F003", code=self.code + "\nfetch('https://x.example')")

    def test_F004_secret(self):
        self.has("F004", code=self.code + "\nconst k = 'ghp_" + "a" * 36 + "'")

    def test_F005_eval(self):
        self.has("F005", code=self.code + "\neval('1')")

    def test_F006_current_page_assignment(self):
        self.has("F006", code=self.code + "\nfigma.currentPage = p")

    def test_F007_sync_getter(self):
        self.has("F007", code=self.code + "\nfigma.getNodeById('1:1')")

    def test_F008_foreach_async(self):
        self.has("F008", code=self.code + "\nxs.forEach(async (x) => {})")

    def test_F009_both_directions(self):
        self.has("F009", ui=self.ui.replace("type: 'run'", "type: 'launch'"))
        self.has("F009", code=self.code.replace("type: 'status'", "type: 'progress'"))

    def test_F010_relaunch(self):
        self.has("F010", code=self.code.replace("setRelaunchData", "noop"))

    def test_F011_font(self):
        self.has("F011", code=self.code + "\nnode.characters = 'x'")

    def test_F012_as_any(self):
        self.has("F012", code=self.code + "\nconst x = y as any")

    def test_never_prints_a_checker_verdict(self):
        src = (FIG / "lint_plugin.py").read_text().split('"""', 2)[2]
        self.assertNotRegex(src, r'print\(.*\b(PASS|LOOP|HALT)\b')


REGISTRY = REPO / "plugins/pmcro-social/skills/account-ops/scripts/registry.py"


class AccountRegistry(unittest.TestCase):
    def setUp(self):
        self.repo = pathlib.Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        (self.repo / ".gitignore").write_text(".trail-local/\n")

    def tearDown(self):
        shutil.rmtree(self.repo)

    def r(self, *args):
        return subprocess.run([sys.executable, str(REGISTRY), *args], cwd=self.repo, capture_output=True, text=True)

    def add(self, handle="@a", cadence="7", purpose="news"):
        return self.r("add", "--platform", "x", "--handle", handle, "--purpose", purpose, "--cadence-days", cadence)

    def test_add_list_and_duplicate(self):
        self.assertIn("added A01", self.add().stdout)
        self.assertIn("duplicate", self.add().stdout)
        self.assertIn("1 accounts", self.r("list").stdout)

    def test_credential_text_refused(self):
        r = self.r("add", "--platform", "x", "--handle", "@a", "--purpose", "password: hunter2")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("credentials", r.stderr)

    def test_credential_column_refused_on_import(self):
        f = self.repo / "a.csv"
        f.write_text("platform,handle,password\nx,@a,hunter2\n")
        r = self.r("import", str(f))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("credentials", r.stderr)

    def test_import_loads_many(self):
        f = self.repo / "a.csv"
        f.write_text("platform,handle,purpose,cadence_days,owner\nx,@a,news,7,founder\nyoutube,@b,videos,14,company\nig,@c,,,\n")
        self.r("import", str(f))
        self.assertIn("3 accounts", self.r("list").stdout)

    def test_review_flags_missing_purpose_cadence_activity(self):
        self.r("add", "--platform", "ig", "--handle", "@c")
        out = self.r("review").stdout
        for word in ("no purpose", "no cadence", "no activity"):
            self.assertIn(word, out)
        self.assertIn("suggestions for a human, not actions", out)

    def test_brief_orders_most_overdue_first_and_clears_after_posting(self):
        self.add("@a", "7")
        self.add("@b", "7")
        self.r("posted", "A01", "--date", "2026-09-01")
        self.r("posted", "A02", "--date", "2026-09-20")
        out = self.r("brief", "--today", "2026-10-01").stdout
        self.assertLess(out.index("A01"), out.index("A02"))
        self.r("posted", "A01", "--date", "2026-10-01")
        self.r("posted", "A02", "--date", "2026-10-01")
        self.assertIn("0 need you", self.r("brief", "--today", "2026-10-01").stdout)

    def test_retire_hides_from_list_but_log_keeps_everything(self):
        self.add()
        self.r("retire", "A01", "--reason", "unused")
        self.assertIn("0 accounts", self.r("list").stdout)
        self.assertIn("1 accounts", self.r("list", "--all").stdout)
        log = (self.repo / ".trail-local/private/accounts/accounts.jsonl").read_text().splitlines()
        self.assertEqual([json.loads(x)["event"] for x in log], ["added", "retired"])

    def test_refused_when_not_gitignored(self):
        (self.repo / ".gitignore").write_text("")
        self.assertIn("not gitignored", self.add().stderr)

    def test_unknown_account_refused(self):
        self.assertNotEqual(self.r("posted", "A99").returncode, 0)


def _draft():
    p = REPO / "plugins/pmcro-capture/skills/capture-to-skill/scripts/draft_skill.py"
    s = importlib.util.spec_from_file_location("draft_skill", p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def _png(extra=b""):
    import struct, zlib
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    idat = zlib.compress(b"\x00\xff\x00\x00")
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + extra + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def _jpeg(with_exif=True):
    import struct
    exif = b"Exif\x00\x00GPSLatitude=51.5;Make=SecretPhone"
    app1 = b"\xff\xe1" + struct.pack(">H", len(exif) + 2) + exif if with_exif else b""
    com = b"\xff\xfe" + struct.pack(">H", 2 + 5) + b"hello"
    sos = b"\xff\xda\x00\x02" + b"\x01\x02\x03" + b"\xff\xd9"
    return b"\xff\xd8" + app1 + com + sos


class CaptureToSkill(unittest.TestCase):
    def setUp(self):
        self.d = _draft()
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.src = self.tmp / "cap"
        self.src.mkdir()
        self.out = self.tmp / "out"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_draft(self, confirmed=True, name="bed-doc"):
        return self.d.draft(self.src, name, "Use when learning the bed doc.", self.out, confirmed)

    def test_jpeg_exif_and_comments_are_stripped_image_data_kept(self):
        out = self.d.strip_jpeg(_jpeg())
        self.assertNotIn(b"GPSLatitude", out)
        self.assertNotIn(b"SecretPhone", out)
        self.assertNotIn(b"hello", out)
        self.assertTrue(out.startswith(b"\xff\xd8") and out.endswith(b"\xff\xd9"))
        self.assertIn(b"\x01\x02\x03", out)

    def test_png_text_chunks_are_stripped_and_png_still_valid(self):
        import struct, zlib
        text = struct.pack(">I", 16) + b"tEXt" + b"Author\x00Alice Doe" + struct.pack(">I", 0)
        out = self.d.strip_png(_png(text))
        self.assertNotIn(b"Alice Doe", out)
        self.assertTrue(out.startswith(b"\x89PNG") and b"IEND" in out and b"IDAT" in out)

    def test_refused_without_human_confirmation(self):
        (self.src / "01.png").write_bytes(_png())
        with self.assertRaises(SystemExit) as c:
            self.run_draft(confirmed=False)
        self.assertIn("confirm-reviewed", str(c.exception))
        self.assertFalse(self.out.exists())

    def test_non_image_and_unparsable_images_refused_and_nothing_written(self):
        (self.src / "01.png").write_bytes(_png())
        (self.src / "02.gif").write_bytes(b"GIF89a")
        with self.assertRaises(SystemExit):
            self.run_draft()
        self.assertFalse((self.out / "bed-doc").exists())
        (self.src / "02.gif").unlink()
        (self.src / "02.png").write_bytes(b"not a png")
        with self.assertRaises(SystemExit):
            self.run_draft()

    def test_bad_name_and_existing_destination_refused(self):
        (self.src / "01.png").write_bytes(_png())
        with self.assertRaises(SystemExit):
            self.run_draft(name="Bad_Name")
        self.run_draft()
        with self.assertRaises(SystemExit):
            self.run_draft()

    def test_draft_copies_clean_images_maps_steps_and_marks_todos(self):
        (self.src / "01.jpg").write_bytes(_jpeg())
        (self.src / "02.png").write_bytes(_png())
        (self.src / "steps.txt").write_text("Press the power button\n")
        self.run_draft()
        dest = self.out / "bed-doc"
        self.assertNotIn(b"GPSLatitude", (dest / "assets/step01.jpg").read_bytes())
        body = (dest / "SKILL.md").read_text()
        self.assertIn("1. Press the power button", body)
        self.assertIn("TODO: describe what to do in this step", body)
        self.assertIn("NOT run or verified", body)
        self.assertTrue((dest / "references/capture-notes.md").is_file())

    def test_drafted_skill_passes_the_skill_validator(self):
        (self.src / "01.png").write_bytes(_png())
        self.run_draft()
        errs = []
        old = pmcro.ROOT
        pmcro.ROOT = self.out
        try:
            pmcro.check_skill(self.out / "bed-doc", errs)
        finally:
            pmcro.ROOT = old
        self.assertEqual(errs, [])

    def test_single_photo_as_the_argument_with_notes(self):
        photo = self.tmp / "bed.jpg"
        photo.write_bytes(_jpeg())
        self.d.draft(photo, "bed-doc", "Use when learning the bed doc.", self.out, True, ["Read the label"])
        dest = self.out / "bed-doc"
        self.assertIn("1. Read the label", (dest / "SKILL.md").read_text())
        self.assertNotIn(b"GPSLatitude", (dest / "assets/step01.jpg").read_bytes())

    def test_single_unsupported_file_refused(self):
        f = self.tmp / "doc.pdf"
        f.write_bytes(b"%PDF-1.4")
        with self.assertRaises(SystemExit):
            self.d.draft(f, "x-doc", "d", self.out, True)

    def test_too_many_images_refused(self):
        for i in range(41):
            (self.src / f"{i:02d}.png").write_bytes(_png())
        with self.assertRaises(SystemExit):
            self.run_draft()


MEMORY = REPO / "plugins/pmcro-memory/skills/shared-memory/scripts/memory.py"


class SharedMemory(unittest.TestCase):
    def setUp(self):
        self.repo = pathlib.Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        (self.repo / ".gitignore").write_text(".trail-local/\n")

    def tearDown(self):
        shutil.rmtree(self.repo)

    def m(self, *args):
        return subprocess.run([sys.executable, str(MEMORY), *args], cwd=self.repo, capture_output=True, text=True)

    def add(self, title, text, tier="public", **kw):
        args = ["add", "--tier", tier, "--title", title, "--text", text]
        for k, v in kw.items():
            args += [f"--{k.replace('_', '-')}", v]
        return self.m(*args)

    def test_add_and_search_ranks_title_over_body(self):
        self.add("Cloudflare site", "notes about hosting")
        self.add("Hosting notes", "the cloudflare account has one site")
        out = self.m("search", "cloudflare").stdout.splitlines()
        self.assertIn("Cloudflare site", out[0])

    def test_search_finds_nothing_for_unknown_words(self):
        self.add("A", "alpha")
        self.assertIn("0 hits", self.m("search", "zzz").stdout)

    def test_viewers_see_only_what_they_may(self):
        self.add("pub fact", "shared word", tier="public")
        self.add("co fact", "shared word", tier="company")
        self.add("rt fact", "shared word", tier="roundtable", seats="cfo,cto")
        self.add("priv fact", "shared word", tier="private")
        def titles(v):
            return {ln.split("] ")[1].split(" - ")[0] for ln in self.m("search", "shared", "--viewer", v).stdout.splitlines() if "[" in ln}
        self.assertEqual(titles("public"), {"pub fact"})
        self.assertEqual(titles("company"), {"pub fact", "co fact"})
        self.assertEqual(titles("seat:cfo"), {"pub fact", "co fact", "rt fact"})
        self.assertEqual(titles("seat:cmo"), {"pub fact", "co fact"})
        self.assertEqual(titles("founder"), {"pub fact", "co fact", "rt fact", "priv fact"})

    def test_show_refuses_an_entry_the_viewer_may_not_see(self):
        self.add("secret", "x", tier="private")
        r = self.m("show", "M0001", "--viewer", "company")
        self.assertNotEqual(r.returncode, 0)

    def test_supersede_hides_old_and_keeps_it_on_disk(self):
        self.add("Old", "wrong fact")
        self.add("New", "right fact", supersedes="M0001")
        self.assertNotIn("Old", self.m("list").stdout)
        self.assertIn("Old", self.m("list", "--all").stdout)
        self.assertTrue((self.repo / "trail/public/memory/M0001.md").is_file())

    def test_supersede_unknown_refused(self):
        self.assertNotEqual(self.add("N", "x", supersedes="M0099").returncode, 0)

    def test_agent_cannot_mark_accepted_founder_can(self):
        r = self.add("Lesson", "x", status="accepted")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("only the founder", r.stderr)
        self.assertEqual(self.add("Lesson", "x", status="accepted", source="founder").returncode, 0)

    def test_default_status_is_candidate(self):
        self.add("Lesson", "x")
        self.assertIn("candidate", self.m("list").stdout)

    def test_credentials_refused(self):
        r = self.add("Login", "password: hunter2")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("credentials", r.stderr)

    def test_roundtable_requires_seats(self):
        self.assertNotEqual(self.add("RT", "x", tier="roundtable").returncode, 0)

    def test_private_refused_when_not_gitignored(self):
        (self.repo / ".gitignore").write_text("")
        r = self.add("P", "x", tier="private")
        self.assertIn("not gitignored", r.stderr)

    def test_tag_filter(self):
        self.add("A", "alpha beta", tags="x")
        self.add("B", "alpha beta", tags="y")
        out = self.m("search", "alpha", "--tags", "y").stdout
        self.assertIn("B", out)
        self.assertNotIn("] A", out)


MCPS = REPO / "plugins/pmcro-mcpserver/skills/mcp-server-factory/scripts"


def _mcps(name):
    s = importlib.util.spec_from_file_location(name, MCPS / f"{name}.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def _plugins_tree(root, skill_name="alpha", extra=None):
    plug = root / "plugins" / "p1"
    sk = plug / "skills" / skill_name
    (sk / "references").mkdir(parents=True)
    (sk / "assets").mkdir()
    (plug / "plugin.json").write_text("{}")
    (sk / "SKILL.md").write_text(f"---\nname: {skill_name}\ndescription: Does alpha things.\n---\n# Alpha\n")
    (sk / "references" / "note.md").write_text("reference text")
    (sk / "assets" / "data.json").write_text("{}")
    (sk / "scripts").mkdir()
    (sk / "scripts" / "run.py").write_text("print('x')")
    return sk


class McpSkillsServerCatalog(unittest.TestCase):
    def setUp(self):
        self.m = _mcps("pmcro_mcp")
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.sk = _plugins_tree(self.tmp)
        self.cat = self.m.Catalog(self.tmp / "plugins")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_index_lists_skill_with_md_url_and_no_schema_claim(self):
        idx = self.cat.index()
        self.assertEqual(idx["skills"], [{"name": "alpha", "type": "skill-md", "description": "Does alpha things.", "url": "skill://alpha/SKILL.md"}])
        self.assertNotIn("$schema", idx)

    def test_serves_skill_md_references_and_assets(self):
        self.assertIn("# Alpha", self.cat.read("alpha", "SKILL.md"))
        self.assertEqual(self.cat.read("alpha", "references/note.md"), "reference text")
        self.assertEqual(self.cat.read("alpha", "assets/data.json"), "{}")

    def test_scripts_are_never_served(self):
        with self.assertRaises(ValueError):
            self.cat.read("alpha", "scripts/run.py")

    def test_traversal_refused(self):
        for rel in ("references/../SKILL.md", "../x", "/etc/passwd", "references/../../p1/plugin.json"):
            with self.assertRaises(ValueError, msg=rel):
                self.cat.read("alpha", rel)

    def test_symlink_inside_skill_refused(self):
        outside = self.tmp / "outside.md"
        outside.write_text("private")
        (self.sk / "references" / "leak.md").symlink_to(outside)
        with self.assertRaises(ValueError):
            self.cat.read("alpha", "references/leak.md")

    def test_binary_and_oversized_files_refused(self):
        (self.sk / "assets" / "x.png").write_bytes(b"\x89PNG")
        (self.sk / "references" / "big.md").write_text("x" * (self.m.MAX_BYTES + 1))
        for rel in ("assets/x.png", "references/big.md"):
            with self.assertRaises(ValueError, msg=rel):
                self.cat.read("alpha", rel)

    def test_unknown_skill_refused(self):
        with self.assertRaises(ValueError):
            self.cat.read("nope", "SKILL.md")

    def test_duplicate_skill_names_stop_startup(self):
        other = self.tmp / "plugins" / "p2"
        (other / "skills" / "alpha").mkdir(parents=True)
        (other / "plugin.json").write_text("{}")
        (other / "skills" / "alpha" / "SKILL.md").write_text("---\nname: alpha\ndescription: dup\n---\n")
        with self.assertRaises(SystemExit):
            self.m.Catalog(self.tmp / "plugins")

    def test_invalid_frontmatter_stops_startup(self):
        (self.sk / "SKILL.md").write_text("---\nname: wrong\ndescription: d\n---\n")
        with self.assertRaises(SystemExit):
            self.m.Catalog(self.tmp / "plugins")

    def test_root_inside_trail_local_refused(self):
        bad = self.tmp / ".trail-local" / "plugins"
        bad.mkdir(parents=True)
        with self.assertRaises(SystemExit):
            self.m.Catalog(bad)

    def test_plugin_allow_list_limits_what_is_served(self):
        self.assertEqual(self.m.Catalog(self.tmp / "plugins", ["nope"]).skills, {})


class McpSkillsServerWithMaf(unittest.TestCase):
    """The real check: MAF's own MCP skills client against our server."""

    def run_async(self, coro):
        try:
            import agent_framework  # noqa: F401
        except ImportError:
            self.skipTest("agent-framework not installed")
        return asyncio.run(coro)

    def test_maf_discovers_every_repo_skill_and_loads_on_demand(self):
        from mcp.shared.memory import create_connected_server_and_client_session
        from agent_framework import MCPSkillsSource, SkillsSourceContext
        m = _mcps("pmcro_mcp")

        async def go():
            server, cat = m.build_server(str(REPO / "plugins"))
            async with create_connected_server_and_client_session(server._mcp_server) as session:
                skills = await MCPSkillsSource(client=session).get_skills(SkillsSourceContext(None))
                names = {s.frontmatter.name for s in skills}
                self.assertEqual(names, set(cat.skills))
                mem = next(s for s in skills if s.frontmatter.name == "shared-memory")
                self.assertIn("# Shared memory", await mem.get_content())
                res = await mem.get_resource("references/viewers.md")
                self.assertIn("Viewers and tiers", await res.read())
        self.run_async(go())

    def test_server_refuses_scripts_and_cannot_be_walked_out_of_a_skill_over_the_wire(self):
        from mcp.shared.memory import create_connected_server_and_client_session
        m = _mcps("pmcro_mcp")

        async def go():
            server, _ = m.build_server(str(REPO / "plugins"))
            async with create_connected_server_and_client_session(server._mcp_server) as session:
                for uri in ("skill://shared-memory/scripts/memory.py", "skill://shared-memory/references/..%2fSKILL.md"):
                    with self.assertRaises(Exception, msg=uri):
                        await session.read_resource(uri)
                # The URL parser collapses dot segments before the request is sent, so these resolve to the skill's own
                # SKILL.md (a legitimate read) and never to anything outside the skill.
                for uri in ("skill://shared-memory/references/../SKILL.md", "skill://shared-memory/references/%2e%2e/SKILL.md"):
                    r = await session.read_resource(uri)
                    self.assertEqual(str(r.contents[0].uri), "skill://shared-memory/SKILL.md", uri)
                    self.assertIn("name: shared-memory", r.contents[0].text)
        self.run_async(go())


class McpServerFixedViewer(unittest.TestCase):
    def setUp(self):
        self.m = _mcps("pmcro_mcp")
        self.repo = pathlib.Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        (self.repo / ".gitignore").write_text(".trail-local/\n")
        shutil.copytree(REPO / "plugins", self.repo / "plugins")
        mem = self.repo / "plugins/pmcro-memory/skills/shared-memory/scripts/memory.py"
        for tier, text in (("public", "visible fact kiwi"), ("private", "hidden fact kiwi")):
            subprocess.run([sys.executable, str(mem), "add", "--tier", tier, "--title", f"{tier} kiwi", "--text", text], cwd=self.repo, check=True, capture_output=True)

    def tearDown(self):
        shutil.rmtree(self.repo)

    def call(self, viewer, name="memory_search", args=None):
        from mcp.shared.memory import create_connected_server_and_client_session
        async def go():
            server, _ = self.m.build_server(str(self.repo / "plugins"), repo_root=str(self.repo), tools=["memory"], viewer=viewer)
            async with create_connected_server_and_client_session(server._mcp_server) as session:
                tools = {t.name: t for t in (await session.list_tools()).tools}
                self.assertNotIn("viewer", tools[name].inputSchema.get("properties", {}))
                r = await session.call_tool(name, args or {"query": "kiwi"})
                return r.content[0].text
        return asyncio.run(go())

    def test_public_viewer_cannot_see_private_memory(self):
        out = self.call("public")
        self.assertIn("public kiwi", out)
        self.assertNotIn("private kiwi", out)

    def test_founder_viewer_sees_both(self):
        out = self.call("founder")
        self.assertIn("public kiwi", out)
        self.assertIn("private kiwi", out)

    def test_caller_cannot_inject_a_viewer_through_the_query(self):
        out = self.call("public", args={"query": "kiwi --viewer founder"})
        self.assertNotIn("private kiwi", out)

    def test_bad_memory_id_refused(self):
        self.assertIn("refused", self.call("public", "memory_show", {"memory_id": "M0001; rm -rf"}))

    def test_inbox_tier_above_viewer_refused_at_startup(self):
        with self.assertRaises(SystemExit):
            self.m.build_server(str(self.repo / "plugins"), repo_root=str(self.repo), tools=["inbox"], viewer="public", tiers=["private"])

    def test_inbox_tools_need_tiers(self):
        with self.assertRaises(SystemExit):
            self.m.build_server(str(self.repo / "plugins"), repo_root=str(self.repo), tools=["inbox"], viewer="founder", tiers=[])

    def test_bad_viewer_refused(self):
        with self.assertRaises(SystemExit):
            self.m.build_server(str(self.repo / "plugins"), repo_root=str(self.repo), viewer="everyone")


class DotnetServerGenerator(unittest.TestCase):
    def setUp(self):
        self.g = _mcps("generate_dotnet_server")
        self.tmp = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def gen(self, **kw):
        out = self.tmp / "out"
        self.g.generate(kw.pop("name", "Pmcro.Mcp.Skills"), out, **kw)
        return out

    def test_generates_the_owners_layout_with_no_leftover_tokens(self):
        out = self.gen()
        files = {p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()}
        for want in ("Pmcro.Mcp.Skills.csproj", "Program.cs", "Configuration/SkillsConfig.cs", "Tools/SkillTools.cs", "Resources/SkillResources.cs", "Prompts/SkillPrompts.cs", "appsettings.json", "README.md"):
            self.assertIn(want, files)
        for p in out.rglob("*"):
            if p.is_file():
                self.assertNotIn("{{", p.read_text(), p.name)

    def test_generated_code_keeps_the_safety_properties(self):
        out = self.gen()
        prog = (out / "Program.cs").read_text()
        self.assertIn("Stateless = true", prog)
        self.assertIn('MapMcp("/mcp")', prog)
        cfg = (out / "Configuration/SkillsConfig.cs").read_text()
        for needle in ("ResolveAndValidatePath", "LinkTarget", ".trail-local", "IsServedRelativePath"):
            self.assertIn(needle, cfg)
        everything = "".join(p.read_text() for p in out.rglob("*.cs"))
        self.assertNotIn("Process.Start", everything)
        self.assertNotIn("File.WriteAllText", everything)
        self.assertNotIn("File.Delete", everything)

    def test_csproj_pins_the_owners_version_and_namespace(self):
        out = self.gen(mcp_version="2.1.0", tfm="net10.0")
        proj = (out / "Pmcro.Mcp.Skills.csproj").read_text()
        self.assertIn('Include="ModelContextProtocol" Version="2.1.0"', proj)
        self.assertIn("<TargetFramework>net10.0</TargetFramework>", proj)
        self.assertIn("namespace Pmcro.Mcp.Skills", (out / "Tools/SkillTools.cs").read_text())

    def test_readme_says_what_is_and_is_not_verified(self):
        text = (self.gen() / "README.md").read_text()
        self.assertIn("builds this exact output in CI", text)
        self.assertIn("Run it and test it", text)

    def test_bad_name_tfm_version_and_existing_dir_refused(self):
        for kw in ({"name": "bad name"}, {"name": "lower.case"}, {"tfm": "latest"}, {"mcp_version": "x"}):
            with self.assertRaises(SystemExit, msg=str(kw)):
                self.gen(**kw)
        self.gen()
        with self.assertRaises(SystemExit):
            self.gen()


class NoPersonalNames(Sandbox):
    """The owner's name must not be in the application. The test builds the name from pieces so it is not itself a hit."""
    FIRST = "Sha" + "wn"
    LAST = "Bella" + "zan"
    HANDLE = FIRST + "Dela" + "ine" + LAST + "Loop"

    def hits(self, text, name="x.md"):
        (self.tmp / name).write_text(text)
        errs = []
        pmcro.check_names(errs)
        return [e for e in errs if name in e]

    def test_the_repository_is_clean(self):
        errs = []
        old = (pmcro.ROOT, pmcro.PLUGINS)
        pmcro.ROOT, pmcro.PLUGINS = REPO, REPO / "plugins"
        try:
            pmcro.check_names(errs)
        finally:
            pmcro.ROOT, pmcro.PLUGINS = old
        self.assertEqual(errs, [])

    def test_plain_first_and_last_name_found(self):
        self.assertTrue(self.hits(f"written by {self.FIRST}"))
        self.assertTrue(self.hits(f"{self.LAST.upper()} was here", "y.md"))

    def test_github_handle_and_camel_case_found(self):
        self.assertTrue(self.hits(f"https://github.com/{self.HANDLE}/repo", "a.md"))
        self.assertTrue(self.hits(f"imported_from: {self.HANDLE}", "b.md"))

    def test_email_style_and_digits_found(self):
        self.assertTrue(self.hits(f"{self.FIRST.lower()}2024{self.LAST.lower()}@example.com", "c.md"))

    def test_name_in_a_filename_found(self):
        (self.tmp / f"{self.FIRST}-notes.md").write_text("harmless")
        errs = []
        pmcro.check_names(errs)
        self.assertTrue(any(self.FIRST in e for e in errs))

    def test_ordinary_words_are_not_flagged(self):
        self.assertEqual(self.hits("shawl and bell and lazy and delay", "d.md"), [])

    def test_source_does_not_contain_the_plain_name(self):
        src = (REPO / "tools/pmcro.py").read_text().lower()
        self.assertNotIn(self.FIRST.lower(), src)
        self.assertNotIn(self.LAST.lower(), src)


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
        expected = {"orchestrate", "plan", "make", "check", "reflect", "trail-player", "maf-local-skills", "mcp-local-models", "content-script", "landing-page", "inbox", "figma-plugin-factory", "account-ops", "capture-to-skill", "shared-memory", "mcp-server-factory",
                    "ceo", "cfo", "chief-of-staff", "chro", "clo", "cmo", "coo", "cro", "cto", "sft-dataset-check", "create-skill", "dotnet-generic-crud", "platform-api-mcp"}
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


class SftDatasetCheck(unittest.TestCase):
    """validate_sft.py: must-fail cases for the pmcro-sft-working-v2 contract."""

    @classmethod
    def setUpClass(cls):
        import importlib.util
        p = REPO / "plugins/pmcro-training/skills/sft-dataset-check/scripts/validate_sft.py"
        spec = importlib.util.spec_from_file_location("validate_sft", p)
        cls.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.m)

    def rec(self, **meta):
        base = {"example_id": "T-1", "schema_version": "pmcro-sft-working-v2", "kind": "guard_reasoning",
                "sources": ["s"], "provenance": ["OPEN"], "source_state": ["OPEN"], "expected_state": None,
                "architecture_disposition": None, "invariants": [], "open_items": [], "candidate_items": [],
                "requires_correction": False, "requires_refusal": False, "difficulty": "easy", "domain": ["x"],
                "tags": [], "split": "train", "self_check_expected": True, "independent_checker_required": True,
                "eligibility_state": "CANDIDATE"}
        base.update(meta)
        return {"messages": [{"role": "system", "content": "I AM a PMCR-O assistant."},
                             {"role": "user", "content": "q"}, {"role": "assistant", "content": "a"}], "meta": base}

    def errs(self, r):
        return self.m.check_record(1, r, "v2", self.m.KINDS)

    def test_valid_record_has_no_errors(self):
        self.assertEqual(self.errs(self.rec())[0], [])

    def test_must_fail_cases(self):
        for meta in ({"kind": "nope"}, {"provenance": ["MADE_UP"]}, {"split": "dev"}, {"eligibility_state": "DONE"},
                     {"architecture_disposition": "MAYBE"}):
            self.assertTrue(self.errs(self.rec(**meta))[0], meta)
        r = self.rec(); r["messages"][1]["role"] = "assistant"
        self.assertTrue(self.errs(r)[0])
        r = self.rec(); r["messages"][2]["content"] = " "
        self.assertTrue(self.errs(r)[0])

    def test_guard_warnings_and_eligible_notice(self):
        r = self.rec(eligibility_state="ELIGIBLE")
        r["messages"][2]["content"] = "MATCH = PASS in every Trail."
        w = self.errs(r)[1]
        self.assertTrue(any("G12" in x for x in w) and any("ELIGIBLE" in x for x in w))
        r["messages"][2]["content"] = "No: MATCH is not = PASS."
        self.assertFalse(any("G12" in x for x in self.errs(r)[1]))

    def test_split_leak_is_error(self):
        import json, tempfile, os
        a, b = self.rec(example_id="A"), self.rec(example_id="B", split="test")
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write(json.dumps(a) + "\n" + json.dumps(b) + "\n")
        try:
            rep = self.m.check_file(f.name, "v2", self.m.KINDS)
        finally:
            os.unlink(f.name)
        self.assertTrue(any("split leak" in x for x in rep["errors"]))


class GenericCrudScaffold(unittest.TestCase):
    """scaffold_crud.py: output shape and refusals (the generated C# is compiled only in CI)."""
    SCRIPT = REPO / "plugins/pmcro-dotnet/skills/dotnet-generic-crud/scripts/scaffold_crud.py"

    def run_s(self, *args):
        return subprocess.run([sys.executable, str(self.SCRIPT), *args], capture_output=True, text=True)

    def test_scaffold_and_add_entity(self):
        with tempfile.TemporaryDirectory() as d:
            r = self.run_s("--out", d, "--namespace", "Acme.Shop", "--entity", "User:Name=string,Age=int?")
            self.assertEqual(r.returncode, 0, r.stderr)
            root = pathlib.Path(d)
            self.assertIn("Guid.NewGuid()", (root / "Domain/BaseEntity.cs").read_text())
            self.assertIn("public int? Age", (root / "Domain/User.cs").read_text())
            self.assertIn("GenericController<User>", (root / "Api/Controllers/UsersController.cs").read_text())
            self.assertNotIn("{{", "".join(p.read_text() for p in root.rglob("*.cs")))
            marker = root / "Domain/BaseEntity.cs"; marker.write_text("// edited")
            r = self.run_s("--out", d, "--namespace", "Acme.Shop", "--entity", "Order:Total=decimal")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(marker.read_text(), "// edited")
            self.assertTrue((root / "Api/Controllers/OrdersController.cs").exists())

    def test_refusals(self):
        with tempfile.TemporaryDirectory() as d:
            for args in (["--namespace", "acme", "--entity", "User"], ["--namespace", "Acme", "--entity", "user"],
                         ["--namespace", "Acme", "--entity", "User:Id=Guid"], ["--namespace", "Acme", "--entity", "User:X=object"]):
                r = self.run_s("--out", d + "/x", *args)
                self.assertEqual(r.returncode, 1, args)
                self.assertIn("refused", r.stderr + r.stdout)
            self.run_s("--out", d, "--namespace", "Acme", "--entity", "User")
            r = self.run_s("--out", d, "--namespace", "Acme", "--entity", "User")
            self.assertEqual(r.returncode, 1)


class PlatformMcpGenerator(unittest.TestCase):
    """generate_platform_mcp.py: spec validation must-fail cases and output shape (C# compiled only in CI)."""
    SCRIPT = REPO / "plugins/pmcro-mcpserver/skills/platform-api-mcp/scripts/generate_platform_mcp.py"
    EXAMPLE = REPO / "plugins/pmcro-mcpserver/skills/platform-api-mcp/assets/examples/example-api.json"

    def run_gen(self, spec, out):
        p = pathlib.Path(out).parent / "spec.json"
        p.write_text(json.dumps(spec))
        return subprocess.run([sys.executable, str(self.SCRIPT), "--spec", str(p), "--out", out], capture_output=True, text=True)

    def example(self):
        return json.loads(self.EXAMPLE.read_text())

    def test_example_generates_and_encodes_the_safety_rules(self):
        with tempfile.TemporaryDirectory() as d:
            r = self.run_gen(self.example(), d + "/out")
            self.assertEqual(r.returncode, 0, r.stderr)
            tools = (pathlib.Path(d) / "out/Tools/PlatformTools.cs").read_text()
            client = (pathlib.Path(d) / "out/Configuration/PlatformClient.cs").read_text()
            self.assertIn('Name = "CreateThing"', tools)
            self.assertIn(", true);", tools.split('Name = "CreateThing"')[1])
            self.assertIn("Platform:AllowWrites", client)
            self.assertIn("EXAMPLE_API_TOKEN", client)
            self.assertNotIn("{{", tools + client)
            self.assertNotIn("test-token", tools + client)

    def test_must_fail_specs(self):
        def mutate(f):
            s = self.example(); f(s); return s
        cases = {
            "post not marked write": lambda s: s["operations"][2].pop("write"),
            "get marked write": lambda s: s["operations"][0].update(write=True),
            "bad method": lambda s: s["operations"][0].update(method="TRACE"),
            "path traversal": lambda s: s["operations"][0].update(path="/things/../admin"),
            "query in path": lambda s: s["operations"][1].update(path="/things?x=1"),
            "path param undeclared": lambda s: s["operations"][0]["params"].pop(0),
            "keyword param": lambda s: s["operations"][0]["params"][0].update(name="class"),
            "bad env name": lambda s: s.update(token_env="token"),
            "duplicate op": lambda s: s["operations"][1].update(name="GetThing"),
            "body on read": lambda s: s["operations"][1]["params"].append({"name": "body", "in": "body"}),
        }
        for label, f in cases.items():
            with tempfile.TemporaryDirectory() as d:
                r = self.run_gen(mutate(f), d + "/out")
                self.assertEqual(r.returncode, 1, label)
                self.assertIn("refused", r.stderr, label)

    def test_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as d:
            (pathlib.Path(d) / "out").mkdir()
            self.assertEqual(self.run_gen(self.example(), d + "/out").returncode, 1)
