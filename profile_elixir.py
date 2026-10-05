import hashlib
import json
import re
from collections import Counter

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix

# Shared across OTP and control tasks.
repo_cap = 5

with open("repository_aliases.json") as file:
    repository_identity = json.load(file)


def canonical_repo(repo):
    name = repo.lower()
    return repository_identity["aliases"].get(name, name)


review_files = [
    "tag_audit/reviews.json",
    "tag_audit/borderline_eight/reviews.json",
    "tag_audit/remaining_otp/reviews.json",
    "tag_audit/selected_controls/reviews.json",
]

reviewed_tags = {}

for filename in review_files:
    with open(filename) as file:
        reviews = json.load(file)

    for review in reviews:
        if review["manual_tag"] is not None:
            reviewed_tags[review["instance_id"]] = review["manual_tag"]

sample_exclusions = json.loads(Path("sample_exclusions.json").read_text())

# Provisional rules—not a complete or manually validated OTP detector.
OTP_PATTERNS = [
    # Modules associated with processes and supervision.
    r"\b(?:GenServer|Supervisor|DynamicSupervisor|Task\.Supervisor|Agent|Registry|Process)\b",

    # Common OTP callback definitions or calls.
    r"\b(?:handle_call|handle_cast|handle_info|handle_continue|terminate|code_change|child_spec)\s*\(",

    # Process operations included in our provisional OTP definition.
    r"(?<![\w.])(?:send|spawn|spawn_link|spawn_monitor)\s*\(",
    r"\breceive\s+do\b",
]

OTP_REGEXES = [re.compile(pattern) for pattern in OTP_PATTERNS]


def get_changed_lines(patch):
    """Extract added and removed text from diff hunks."""
    changed_lines = []
    in_hunk = False

    for line in patch.splitlines():
        if line.startswith("diff --git "):
            in_hunk = False
        elif line.startswith("@@ "):
            in_hunk = True
        elif in_hunk and line.startswith(("+", "-")):
            changed_lines.append(line[1:])

    return changed_lines


def tag_patch(patch):
    """Classify a reference patch using the provisional regex rules."""
    changed_text = "\n".join(get_changed_lines(patch))

    if any(regex.search(changed_text) for regex in OTP_REGEXES):
        return "otp"

    if any(regex.search(patch) for regex in OTP_REGEXES):
        return "borderline"

    return "control"

def effective_tag(task):
    instance_id = task["instance_id"]

    if instance_id in reviewed_tags:
        return reviewed_tags[instance_id]

    return tag_patch(task["patch"])


# 1. Read the saved dataset configuration.
with open("dataset_config.json") as file:
    config = json.load(file)

dataset = config["dataset"]
revision = config["revision"]
filename = "data/train-00000-of-00001.parquet"

url = (
    f"https://huggingface.co/datasets/{dataset}"
    f"/resolve/{revision}/{filename}"
)


# 2. Read the local dataset. This does not download anything.
dataset_path = Path("train.parquet")

if dataset_path.stat().st_size != config["size_bytes"]:
    raise ValueError("Dataset file size does not match the pinned file.")

hasher = hashlib.sha256()

with dataset_path.open("rb") as file:
    while chunk := file.read(1024 * 1024):
        hasher.update(chunk)

actual_sha256 = hasher.hexdigest()

if actual_sha256 != config["sha256"]:
    raise ValueError("Dataset checksum does not match the pinned file.")

print("Dataset size and SHA-256 verified.")

parquet_file = pq.ParquetFile("train.parquet")

schema = parquet_file.schema_arrow

expected_types = {
    "instance_id": pa.string(),
    "repo": pa.string(),
    "language": pa.string(),
    "patch": pa.string(),
    "FAIL_TO_PASS": pa.list_(pa.string()),
    "PASS_TO_PASS": pa.list_(pa.string()),
}

for name, expected_type in expected_types.items():
    if name not in schema.names:
        raise ValueError(f"Missing dataset field: {name}")

    actual_type = schema.field(name).type

    if actual_type != expected_type:
        raise TypeError(
            f"{name}: expected {expected_type}, found {actual_type}"
        )

# Check the nested annotations we use for profiling.
meta_type = schema.field("meta").type
annotations_type = meta_type.field("llm_metadata").type

for name in ["code", "difficulty"]:
    if annotations_type.field(name).type != pa.string():
        raise TypeError(f"meta.llm_metadata.{name} must be a string")

print("Required dataset field types verified.")

table = parquet_file.read(
    columns=["instance_id", "repo", "language", "patch", "meta"]
)


# 3. Keep only Elixir tasks.
is_elixir = pc.equal(table["language"], "elixir")
elixir_tasks = table.filter(is_elixir)
tasks = elixir_tasks.to_pylist()

repos = elixir_tasks["repo"].to_pylist()
unique_repos = set(repos)
tasks_per_repo = Counter(repos)


# 4. Count upstream annotations and our provisional tags.
quality_counts = Counter()
difficulty_counts = Counter()
tag_counts = Counter()
otp_tasks_per_repo = Counter()
quality_a_tasks = []

for task in tasks:
    metadata = task.get("meta") or {}
    annotations = metadata.get("llm_metadata") or {}

    quality_counts[annotations.get("code")] += 1
    difficulty_counts[annotations.get("difficulty")] += 1

    tag = tag_patch(task["patch"])
    tag_counts[tag] += 1

    if tag == "otp":
        otp_tasks_per_repo[canonical_repo(task["repo"])] += 1

    if annotations.get("code") == "A":
        quality_a_tasks.append(task)

def patch_size_bucket(patch):
    size = len(get_changed_lines(patch))
    if size <= 10:
        return "small"
    if size <= 80:
        return "medium"
    return "large"


review_adjusted_counts = Counter()
review_adjusted_otp_repos = Counter()

for task in quality_a_tasks:
    tag = effective_tag(task)
    review_adjusted_counts[tag] += 1

    if tag == "otp":
        review_adjusted_otp_repos[canonical_repo(task["repo"])] += 1

otp_capacity = sum(
    min(count, repo_cap)
    for count in review_adjusted_otp_repos.values()
)

print("\nExact-A counts after applying reviewed labels:")
for tag in ["otp", "borderline", "control", "uncertain"]:
    print(tag, review_adjusted_counts[tag])

print("OTP repositories:", len(review_adjusted_otp_repos))
print(f"OTP capacity with cap {repo_cap}:", otp_capacity)

unreviewed_otp = [
    task
    for task in quality_a_tasks
    if effective_tag(task) == "otp"
    and task["instance_id"] not in reviewed_tags
]

print("\nUnreviewed OTP candidates:", len(unreviewed_otp))

# 5. Calculate the OTP capacity under the repository cap.
# This is an upper bound, not a selected or matched sample.
otp_capacity = sum(
    min(count, repo_cap)
    for count in otp_tasks_per_repo.values()
)


# 6. Repeat the tag and capacity counts for exact-A tasks only.
quality_a_tags = Counter()
quality_a_otp_repos = Counter()

for task in quality_a_tasks:
    tag = tag_patch(task["patch"])
    quality_a_tags[tag] += 1

    if tag == "otp":
        quality_a_otp_repos[canonical_repo(task["repo"])] += 1

quality_a_otp_capacity = sum(
    min(count, repo_cap)
    for count in quality_a_otp_repos.values()
)




# 7. Build the report from the calculated values.
report = {
    "dataset": dataset,
    "revision": revision,
    "source_url": url,
    "language": "elixir",
    "total_dataset_tasks": parquet_file.metadata.num_rows,
    "total_dataset_repositories": len(set(table["repo"].to_pylist())),
    "elixir_tasks": len(tasks),
    "elixir_repositories": len(unique_repos),
    "tasks_per_repository": dict(tasks_per_repo),
    "file_sha256": actual_sha256,
    "file_sha256_verified": True,
    "tagging_patterns": OTP_PATTERNS,
    "required_field_types_verified": True,
    "upstream_quality_counts": [
        {"code": code, "count": count}
        for code, count in quality_counts.most_common()
    ],
    "upstream_difficulty_counts": [
        {"difficulty": difficulty, "count": count}
        for difficulty, count in difficulty_counts.most_common()
    ],
    "all_quality_codes": {
        "tag_counts": {
            tag: tag_counts[tag]
            for tag in ["otp", "borderline", "control"]
        },
        "otp_repositories": len(otp_tasks_per_repo),
        "otp_tasks_per_repository": dict(otp_tasks_per_repo),
        "otp_capacity_after_cap": otp_capacity,
    },
    "exact_a_only": {
        "tasks": len(quality_a_tasks),
        "tag_counts": {
            tag: quality_a_tags[tag]
            for tag in ["otp", "borderline", "control"]
        },
        "otp_repositories": len(quality_a_otp_repos),
        "otp_tasks_per_repository": dict(quality_a_otp_repos),
        "otp_capacity_after_cap": quality_a_otp_capacity,
    },
    "repository_cap": repo_cap,
    "repository_identity": repository_identity,
    "review_adjusted_exact_a": {
        "review_files": review_files,
        "tasks": len(quality_a_tasks),
        "tag_counts": {
            tag: review_adjusted_counts[tag]
            for tag in ["otp", "borderline", "control", "uncertain"]
        },
        "otp_repositories": len(review_adjusted_otp_repos),
        "otp_tasks_per_repository": dict(review_adjusted_otp_repos),
        "otp_capacity_after_cap": sum(
            min(count, repo_cap) for count in review_adjusted_otp_repos.values()
        ),
        "unreviewed_otp_candidates": len(unreviewed_otp),
        "review_method": "Assistant static patch review; not independent human validation",
    },
    "limitations": [
        "Tags are provisional regex classifications.",
        "Markers can match documentation or unrelated names and miss OTP code.",
        "Current repository identities checked; Finch historical fork lineage remains unresolved.",
        "OTP capacity is before matching and gold-patch validation.",
        "The eventual repository cap must be shared across OTP and control tasks.",
        "Exact-A filtering uses upstream annotations without overrides.",
    ],
    "manual_review": {
        "instance_id": "tallarium__reverse_proxy_plug-186",
        "upstream_quality": "B4",
        "finding": (
            "Interface text specifies ArgumentError for streaming when "
            "the adapter lacks stream_response/1. The ambiguity concern "
            "depends on the information supplied to the agent."
        ),
        "eligibility_override": False,
    },
}


# 8. Check matching feasibility without saving a selected sample.
candidates = []

for task in quality_a_tasks:
    tag = effective_tag(task)
    if tag not in {"otp", "control"}:
        continue
    if task["instance_id"] in sample_exclusions:
        continue

    # Preserve the original control eligibility rule:
    # no OTP markers anywhere in the reference patch.
    if tag == "control" and tag_patch(task["patch"]) != "control":
        continue

    difficulty = task["meta"]["llm_metadata"]["difficulty"]
    if difficulty not in {"easy", "medium", "hard"}:
        continue

    candidates.append({
        "instance_id": task["instance_id"],
        "repo": task["repo"],
        "canonical_repo": canonical_repo(task["repo"]),
        "tag": tag,
        "bucket": (
            difficulty,
            patch_size_bucket(task["patch"]),
        ),
    })

buckets = sorted({task["bucket"] for task in candidates})
repositories = sorted({task["canonical_repo"] for task in candidates})

bucket_rows = {bucket: i for i, bucket in enumerate(buckets)}
repo_rows = {
    repo: len(buckets) + i
    for i, repo in enumerate(repositories)
}

n = len(candidates)
matrix = lil_matrix((len(buckets) + len(repositories), n))

for column, task in enumerate(candidates):
    # Equal OTP and control counts within each bucket.
    matrix[bucket_rows[task["bucket"]], column] = (
        1 if task["tag"] == "otp" else -1
    )

    # Both groups consume repository slots.
    matrix[repo_rows[task["canonical_repo"]], column] = 1

# SciPy minimizes: negative OTP count maximizes selected OTP tasks.
objective = np.array([
    -1 if task["tag"] == "otp" else 0
    for task in candidates
])

matching_capacity = {}

print("\nMaximum feasible matched pairs:")

for cap in [4, 5]:
    lower = np.concatenate([
        np.zeros(len(buckets)),
        np.zeros(len(repositories)),
    ])
    upper = np.concatenate([
        np.zeros(len(buckets)),
        np.full(len(repositories), cap),
    ])

    result = milp(
        c=objective,
        integrality=np.ones(n),
        bounds=Bounds(0, 1),
        constraints=LinearConstraint(matrix.tocsr(), lower, upper),
        options={"mip_rel_gap": 0.0},
    )

    if not result.success:
        raise RuntimeError(result.message)

    selected = np.rint(result.x).astype(int)
    pairs = sum(
        selected[i]
        for i, task in enumerate(candidates)
        if task["tag"] == "otp"
    )

    matching_capacity[str(cap)] = int(pairs)
    print(f"Cap {cap}: {pairs} pairs")

report["matching_feasibility"] = {
    "maximum_pairs_by_repository_cap": matching_capacity,
    "patch_size_buckets": {"small": "1-10", "medium": "11-80", "large": "81+"},
    "control_rule": "Reviewed/effective control and no regex markers anywhere in patch",
    "limitations": "Before runtime validation; Finch historical fork lineage remains unresolved",
    "sample_exclusions": sample_exclusions,
}

from scipy.sparse import vstack

target_pairs = 30

if matching_capacity[str(repo_cap)] < target_pairs:
    Path("elixir_profile.json").write_text(json.dumps(report, indent=2) + "\n")
    raise SystemExit(
        f"Only {matching_capacity[str(repo_cap)]} pairs feasible; "
        "saved profile, did not generate a sample."
    )

# Add a constraint requiring exactly 30 OTP tasks.
otp_row = np.array([
    1 if task["tag"] == "otp" else 0
    for task in candidates
])

selection_matrix = vstack(
    [matrix.tocsr(), otp_row.reshape(1, -1)],
    format="csr",
)

lower = np.concatenate([
    np.zeros(len(buckets)),
    np.zeros(len(repositories)),
    [target_pairs],
])

upper = np.concatenate([
    np.zeros(len(buckets)),
    np.full(len(repositories), repo_cap),
    [target_pairs],
])

rng = np.random.default_rng(42)

result = milp(
    c=rng.random(n),
    integrality=np.ones(n),
    bounds=Bounds(0, 1),
    constraints=LinearConstraint(selection_matrix, lower, upper),
    options={"mip_rel_gap": 0.0},
)

if not result.success:
    raise RuntimeError(result.message)

chosen = [
    task
    for task, value in zip(candidates, result.x)
    if value > 0.5
]

# Verify the selection before writing it.
repo_counts = Counter(task["canonical_repo"] for task in chosen)

assert len(chosen) == target_pairs * 2
assert len({task["instance_id"] for task in chosen}) == len(chosen)
assert max(repo_counts.values()) <= repo_cap

pairs = []

for bucket in buckets:
    otp = sorted(
        [
            task for task in chosen
            if task["tag"] == "otp" and task["bucket"] == bucket
        ],
        key=lambda task: task["instance_id"],
    )
    controls = sorted(
        [
            task for task in chosen
            if task["tag"] == "control" and task["bucket"] == bucket
        ],
        key=lambda task: task["instance_id"],
    )

    assert len(otp) == len(controls)

    for treatment, control in zip(otp, controls):
        pairs.append({
            "difficulty": bucket[0],
            "patch_size_bucket": bucket[1],
            "otp": treatment,
            "control": control,
        })

assert len(pairs) == target_pairs

sample = {
    "dataset": dataset,
    "revision": revision,
    "dataset_sha256": actual_sha256,
    "repository_cap": repo_cap,
    "repository_identity": repository_identity,
    "seed": 42,
    "selection_method": "MILP with seeded random task costs",
    "status": "candidate sample; pending control review and runtime validation",
    "pairs": pairs,
    "tasks_per_repository": dict(sorted(repo_counts.items())),
}

sample_path = Path("candidate_pairs.json")

# Preserve an existing sample rather than silently replacing it.
if sample_path.exists():
    existing = json.loads(sample_path.read_text())
    if existing.get("repository_identity") != repository_identity:
        raise ValueError("Existing sample uses different repository identities; archive it before resampling.")
    print("Kept existing candidate_pairs.json.")
else:
    sample_path.write_text(
        json.dumps(sample, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Saved {len(pairs)} candidate pairs to {sample_path}.")

# Validate the persisted sample, not just the optimizer's fresh solution.
saved = json.loads(sample_path.read_text())
eligible = {task["instance_id"]: task for task in candidates}
source_tasks = {task["instance_id"]: task for task in tasks}
if (saved["dataset"], saved["revision"], saved["dataset_sha256"], saved["repository_cap"]) != (
    dataset, revision, actual_sha256, repo_cap
):
    raise ValueError("Saved sample configuration differs from the pinned configuration")
seen = set()
validated_repos = Counter()
balance = Counter()
reviewed_selected = 0
for pair in saved["pairs"]:
    bucket = (pair["difficulty"], pair["patch_size_bucket"])
    for group in ["otp", "control"]:
        entry = pair[group]
        instance_id = entry["instance_id"]
        current = eligible.get(instance_id)
        if instance_id in seen or current is None:
            raise ValueError(f"Duplicate or ineligible selected task: {instance_id}")
        if (current["tag"] != group or current["bucket"] != bucket
                or tuple(entry["bucket"]) != bucket or entry["tag"] != group
                or entry["repo"] != current["repo"]
                or entry["canonical_repo"] != current["canonical_repo"]):
            raise ValueError(f"Saved metadata or group mismatch: {instance_id}")
        if instance_id in reviewed_tags:
            if reviewed_tags[instance_id] != group:
                raise ValueError(f"Review disagrees with sample: {instance_id}")
            reviewed_selected += 1
        seen.add(instance_id)
        validated_repos[current["canonical_repo"]] += 1
        balance[(group, *bucket)] += 1
if len(saved["pairs"]) != target_pairs or len(seen) != 2 * target_pairs:
    raise ValueError("Saved sample does not contain 30 distinct pairs")
if max(validated_repos.values()) > repo_cap:
    raise ValueError("Saved sample exceeds shared repository cap")
if dict(validated_repos) != saved["tasks_per_repository"]:
    raise ValueError("Saved repository counts are stale")
for review_file in review_files:
    for review in json.loads(Path(review_file).read_text()):
        if review["instance_id"] in seen and review.get("patch_sha256"):
            patch = source_tasks[review["instance_id"]]["patch"]
            if hashlib.sha256(patch.encode()).hexdigest() != review["patch_sha256"]:
                raise ValueError(f"Reviewed patch hash mismatch: {review['instance_id']}")
saved["status"] = (
    "labels reviewed; pending runtime validation and historical repository lineage check"
    if reviewed_selected == len(seen) else "candidate sample; incomplete label review"
)
saved["validation"] = {
    "unique_tasks": len(seen), "reviewed_tasks": reviewed_selected,
    "exact_a_and_matching_buckets_verified": True,
    "shared_repository_cap_verified": True,
    "runtime_validated": False,
    "balance": [dict(group=g, difficulty=d, patch_size_bucket=b, count=c)
                for (g, d, b), c in sorted(balance.items())],
}
sample_path.write_text(json.dumps(saved, indent=2) + "\n")
report["selected_sample_validation"] = saved["validation"]
print(f"Validated saved sample: {len(seen)} unique tasks, {reviewed_selected} reviewed.")

# 9. Save the profile after all checks finish.
with open("elixir_profile.json", "w") as file:
    json.dump(report, file, indent=2)
    file.write("\n")

print("\nSaved elixir_profile.json")

with open("candidate_pairs.json") as file:
    saved_sample = json.load(file)

selected_repo_counts = Counter()
unreviewed_controls = []

for pair in saved_sample["pairs"]:
    for group in ["otp", "control"]:
        task = pair[group]
        selected_repo_counts[canonical_repo(task["repo"]) ] += 1

    control = pair["control"]
    if reviewed_tags.get(control["instance_id"]) not in {"otp", "control"}:
        unreviewed_controls.append(control)

print("\nSelected tasks per repository (both groups):")
for repo, count in selected_repo_counts.most_common():
    print(repo, count)

assert max(selected_repo_counts.values()) <= saved_sample["repository_cap"]

print("\nSelected controls needing review:", len(unreviewed_controls))
for task in unreviewed_controls:
    print(task["instance_id"], task["repo"])
