# Synthetic voice and image: consent and disclosure

Status: rules set by the company (ADR 0008). Not legal advice; laws on synthetic media differ by place and platform and change. Check the platform's current policy before publishing.

## Whose voice or face

- Only the founder's own, and only after they write a consent record: whose voice, that it is their own, what it may be used for, the date. Store the record in the `private` trail tier.
- Another person's voice or likeness is out of scope for this company's tools. Do not build it, do not test it.

## Where training happens

- Train and keep voice models on the company's own machine (the offline i9 is the intended place). Raw recordings and the trained model stay local and are never committed, uploaded to a third party or placed in a trail frame.
- Which voice or image model to use, its license and its quality are OPEN. None is chosen or tested here.

## Disclosure

- Any published piece with a synthetic voice or image says so in plain words, in the content itself, not only in a settings flag. The script's `## Disclosure` section holds that sentence.
- Do not present synthetic content as a live recording or a real event.

## Never

Fake testimonials, fake news-style clips, or any content meant to make people believe the founder said or did something they did not.
