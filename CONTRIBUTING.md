# Contributing

Thanks for helping improve 菲比啾比.

## Before opening a pull request

1. Keep changes focused on this repository.
2. Do not add official game files, scraped sticker packs, or artwork without a documented license.
3. Run the asset build and validation commands from the README.
4. Confirm every used sprite cell contains artwork and every unused cell is fully transparent.
5. Keep the pet ID stable as `feibi-jiubi`.

## Contributor attribution

GitHub contributor data should reflect people who actually authored commits in this repository.

- Use your own verified Git name and email.
- Add `Co-authored-by` only when that person materially contributed and agreed to be credited.
- Do not add AI tools, generators, or copied upstream identities as commit co-authors.
- If work is adapted from another project, preserve its license and attribution in a dedicated notice instead of fabricating contributor entries.

Before publishing a release, maintainers should inspect:

```bash
git shortlog -sne --all
git log --format="%an <%ae>" | sort -u
```

After pushing, compare those results with the GitHub contributors endpoint.
