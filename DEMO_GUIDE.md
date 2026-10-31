# IssueLens presentation guide

## Stage-safe path

Open `http://127.0.0.1:5173`, click **Try the guided demo**, then click **Analyze** on the sample issue. The prepared issue fixture shows two separate claims, exact source line references, an inconsistency, and evidence still needed. Open the PR tab for a second prepared example that highlights an untested TTL boundary and keeps the verdict uncertain. Both work without GitHub access or a network connection.

The page labels this as prepared sample data and says no AI call was made. Keep that disclosure visible when presenting it. Use the sample as a product walkthrough or fallback, not as a live model result.

## Live path

1. Start the backend, Python analyzer, Ollama, and frontend using the commands below.
2. Enter a public GitHub repository URL and a read-only public-repository token in the app.
3. Connect, choose an issue or PR, and click **Analyze**.
4. Show the claims, source snippets and line numbers, missing evidence, verdict, and limitations.

Live analysis needs GitHub API access and the local Ollama service. If either is unavailable, use the guided sample rather than spending stage time troubleshooting.

## Local startup

Recommended on presentation day: from the project folder run `./start-demo.sh`. It starts only services that are not already responding, checks the local model and health endpoints, opens the app, and stays in the foreground. Press Ctrl+C to stop services started by that script.

Manual fallback: open separate terminal tabs and run:

```sh
cd backend && node src/server.js
```

```sh
cd analyzer && .venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8001
```

```sh
ollama serve
```

```sh
cd frontend && npm run dev -- --host 0.0.0.0
```

Make sure `qwen2.5-coder:3b` is already available to Ollama before the event. Then open `http://127.0.0.1:5173`.

## 45-second talk track

> “IssueLens checks the claims in an issue, instead of judging who wrote it. We split the report into technical claims, search repository code for candidate evidence, and use a local model to assess what the evidence supports. Here, the first claim says expired cache entries are still returned. Lines 32–35 show the code deleting an expired entry and returning undefined, so that claim conflicts with the implementation. A second claim about when expiry is calculated is supported by the code. We still call out the missing fake-clock test; static evidence is not a reproduction. Maintainers get evidence and uncertainty, not an unsupported yes/no.”

For the guided sample, replace “local model” with “prepared sample” so the demo remains accurate.

## Be precise with judges

- The guided sample is illustrative fixture data, not a live GitHub repository, AI inference, or test run.
- Live mode uses static source matching plus local Ollama assessment; candidate matches are not proof.
- This version does not execute contributor code or tests. It does not claim sandboxed reproduction.
- “Confirmed”, “Invalid”, and “Cannot Reproduce” are assessments; the linked evidence and limitations should guide maintainer review.
