# Sum up 27 November's world news in one image

[![make.fun](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/jinan86/news-image-20261127-v2/rank.svg)](https://make.fun/bounty/news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/jinan86/news-image-20261127-v2/reward.svg)](https://make.fun/bounty/news-image-20261127)

Entry for the [make.fun bounty "Sum up 27 November's world news in one image"](https://make.fun/bounty/news-image-20261127).

`main.py` (Python 3.13, standard library only, no network) draws a one-page
newspaper front page — masthead, date, lead story, columns, and an
"Also Today" strip — and writes it to `/output/entry.png` (1024x1024,
deterministic: two runs produce byte-identical output).

## The day in the image

**Friday, 27 November 2026** — lead story: New Zealand's final election
count, with about 400,000 special votes to settle the incumbent
centre-right coalition's razor-slim majority. Also: Zelenskyy warns of a
major new Russian attack on Ukraine's power grid; Rodrigo Duterte goes on
trial at the ICC on Monday; Black Friday shoppers spend cautiously as
inflation bites; plus Poundland's collapse, Norse Atlantic halting flights,
a tanker capsizing off Ibiza, the Macy's parade moving to Saturday, UK net
migration falling to 77,000, and Depardieu to stand trial.

Sources: Reuters, AP, BBC.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see [LICENSE](LICENSE).
