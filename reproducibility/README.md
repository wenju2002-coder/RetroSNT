# Preview artifacts

`seed42/` contains frozen split indices, vocabularies, preprocessing counts, and
input hashes. These are reference artifacts, not executable preprocessing code.
Only descriptive machine-local path metadata was normalized; the indices and
vocabularies were not changed.

`source_manifest.json` records the partial-release scope, upstream data provenance,
selected archived run metadata and hashes, and the seed pool used for selection.
Omitted checkpoint hashes identify the original weights but do not provide them.

`release_checksums.json` records the current preview files, excluding itself.
The public checks audit these artifacts; they do not evaluate the unreleased model.
No full-model test report or full-model source code is included in this preview.
