# Releasing

Releases are published automatically by the [Release workflow](.github/workflows/release.yml). You never need to create a release by hand — just push a tag.

## How to release

1. **Bump the version** in [`custom_components/ue_boom/manifest.json`](custom_components/ue_boom/manifest.json) (`"version"`), following [semantic versioning](https://semver.org). Keep it below `1.0.0` until the integration is considered stable (e.g. `0.2.0`).

2. **Commit and push** to `main`:

   ```bash
   git add -A
   git commit -m "Your change"
   git push origin main
   ```

3. **Tag and push the tag**:

   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

   Pushing the tag triggers the workflow, which automatically creates a GitHub release. The release notes are generated from the **commit messages since the previous tag**.

## Important notes

- HACS follows **releases/tags**, so only a new tag makes an update available to users — commits alone are not enough.
- Keep the `version` in `manifest.json` in sync with the tag (e.g. `v0.2.0` ↔ `"0.2.0"`).
- The release notes are auto-generated from commit messages. If you need finer control, edit the notes on the release page after it is created.
