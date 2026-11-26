# Input provenance

The reaction inputs come from [Retro-MTGR](https://github.com/zpczaizheli/Retro-MTGR).
The original directory spelling `USPT-50K` is retained in the archived configurations.
Raw reactions and auxiliary input files are not included in this preview.

Expected inputs and SHA-256 values:

| Input path | SHA-256 |
|---|---|
| `data/USPT-50K/50k-all.txt` | `82fb0969d7c11db3600359f73e01a1e1cf50195bcd5234ee4489c0831ee8b704` |
| `data/USPT-50K/other_data/Bond_Energy.txt` | `9a67ba90974b607e9013d615af2cb82c994e28f60759696c3a2f38da1e0fd784` |
| `data/USPT-50K/other_data/Labels.txt` | `e30e5b600f54fa63674dddeaf5267a3067840529b4a737b69ba70586d63c6a00` |

The fixed split indices refer to the original record order, using the first
35,370 records. Do not substitute another USPTO release or reorder reactions.
Obtaining the inputs alone does not enable model training in this partial release;
the neural and preprocessing implementations are intentionally withheld until the
planned complete release. Upstream licensing governs upstream data distribution.
