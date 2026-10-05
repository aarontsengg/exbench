# Repository identity audit

All 61 dataset repository names resolved through the public GitHub API. Initial checks were performed on 2026-10-04; eight rate-limited checks completed on 2026-10-05. The snapshot records repository IDs, redirects, fork flags and source URLs.

Results: 60 distinct current repository IDs. The only duplicated ID is 54749959: commanded/commanded and slashdotdash/commanded. That duplicate is already merged in the sampler. No additional shared-cap violation was found in the saved 30-pair candidate sample; maximum selected tasks per current GitHub ID is five.

## Renamed repositories

- `dashbitco/broadway_cloud_pub_sub` → `elixir-broadway/broadway_cloud_pub_sub` (ID 179568604).
- `jeregrine/jsonapi` → `beam-community/jsonapi` (ID 37813375).
- `keathley/norm` → `elixir-toniq/norm` (ID 177801621).
- `lexhide/xandra` → `whatyouhide/xandra` (ID 59223100).
- `plataformatec/broadway` → `elixir-broadway/broadway` (ID 156210099).
- `plataformatec/mox` → `dashbitco/mox` (ID 104735813).
- `slashdotdash/commanded` → `commanded/commanded` (ID 54749959).

## Historical identity caveat

`keathley/finch` currently resolves to repository ID 804509115, a fork of `sneako/finch` (ID 217153245). The current-name check does not establish which repository hosted the historical task. Verify the selected Finch task’s base commit and PR lineage before runtime validation. No other dataset name currently resolves to either Finch ID, so this does not create an additional identified cap collision.

These checks establish current GitHub identities, not complete historical lineage or absence of shared code across independent repositories. The 30 pairs remain provisional pending control reviews and runtime validation. No paid model calls.
