# Tier details

- **public**: safe for anyone. Goals the company is happy to announce.
- **company**: internal direction every agent needs. It is committable, so the writer refuses it unless the repo is declared private (`git config pmcro.repoVisibility private`, set once and only if true). In a public repo use `roundtable` or `private`.
- **roundtable**: shared with named seats only. Each entry carries `seats: [...]` and a note: "Shared in confidence with the listed seats. Do not disclose, summarize to others, or use for training." This is a house rule, not a legal contract.
- **private**: founder only. No agent reads it unless the founder replays it in session. Never summarized into other tiers.

Widening a tier = new entry with `refs` to the old one, written only on explicit instruction. The old entry stays.

Numbering: each tier counts on its own from 0001 and the writer never reads another tier's folder, so a gap in `public` cannot reveal a `private` entry. A `--refs` number points inside the same tier.

Replay: `--replay` prints the tier asked for and cannot check who the caller is. Separation comes from where files are stored and what each session or seat is given, not from a login.

Refusals (every tier): credential-shaped text and absolute paths in the body or summary (EC-0001). Before each write the check is proven able to fail on a sample built by the writer's own serializer.
