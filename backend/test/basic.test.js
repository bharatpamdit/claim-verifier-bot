import test from "node:test";
import assert from "node:assert/strict";
import { parseUrl } from "../src/workflow.js";

test("accepts a standard public GitHub repository URL", () => {
  assert.deepEqual(parseUrl("https://github.com/openai/codex"), { owner: "openai", repo: "codex" });
});

test("normalizes a .git suffix", () => {
  assert.deepEqual(parseUrl("https://github.com/openai/codex.git"), { owner: "openai", repo: "codex" });
});

test("rejects non-GitHub hosts, credentials, and extra path segments", () => {
  for (const url of ["http://github.com/a/b", "https://github.com.evil.test/a/b", "https://user@github.com/a/b", "https://github.com/a/b/tree/main"]) {
    assert.throws(() => parseUrl(url), /GitHub|github\.com/i);
  }
});

test("rejects malformed owner and repository names", () => {
  for (const url of ["https://github.com/../repo", "https://github.com/owner/..", "https://github.com/a b/repo"]) {
    assert.throws(() => parseUrl(url), /valid|Use/i);
  }
});
