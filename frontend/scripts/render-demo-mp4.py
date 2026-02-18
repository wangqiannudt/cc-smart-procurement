#!/usr/bin/env python3
import json
from pathlib import Path

import cv2


def encode_mp4(frame_paths, output_path, fps=4.0):
    first = cv2.imread(str(frame_paths[0]))
    if first is None:
        raise RuntimeError(f"failed to read first frame: {frame_paths[0]}")

    height, width, _ = first.shape
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    if not writer.isOpened():
        raise RuntimeError(f"failed to open video writer: {output_path}")

    try:
        for frame in frame_paths:
            image = cv2.imread(str(frame))
            if image is None:
                continue
            if image.shape[0] != height or image.shape[1] != width:
                image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
            writer.write(image)
    finally:
        writer.release()


def build_index_markdown(generated_at: str, scenarios):
    lines = [
        "# Demo Video Index",
        "",
        f"- Generated at: {generated_at}",
        "",
        "## Videos",
        "",
    ]

    for item in scenarios:
        lines.extend(
            [
                f"### {item['title']}",
                f"- Path ID: `{item['id']}`",
                f"- Description: {item['description']}",
                f"- MP4: `{item['mp4_path']}`",
                f"- Preview: `{item['preview_path']}`",
                "",
            ]
        )

    return "\n".join(lines)


def main():
    repo_root = Path(__file__).resolve().parents[2]
    demos_dir = repo_root / "docs" / "worklogs" / "demos"
    latest_meta = sorted(demos_dir.glob("*-all-demo-paths/meta.json"))
    if not latest_meta:
        raise RuntimeError("meta.json not found, run capture-demo-frames.mjs first")

    meta_path = latest_meta[-1]
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    demo_root = Path(meta["demo_root"])
    frames_root = Path(meta["frames_root"])
    mp4_root = demo_root / "mp4"
    preview_root = demo_root / "preview"
    mp4_root.mkdir(parents=True, exist_ok=True)
    preview_root.mkdir(parents=True, exist_ok=True)

    updated = []
    for scenario in meta["scenarios"]:
        scenario_dir = frames_root / scenario["id"]
        frame_paths = sorted(scenario_dir.glob("frame-*.png"))
        if not frame_paths:
            continue

        mp4_path = mp4_root / f"{scenario['id']}.mp4"
        preview_path = preview_root / f"{scenario['id']}.png"
        encode_mp4(frame_paths, mp4_path, fps=4.0)

        first = cv2.imread(str(frame_paths[0]))
        if first is not None:
            cv2.imwrite(str(preview_path), first)

        updated.append(
            {
                **scenario,
                "mp4_path": str(mp4_path),
                "preview_path": str(preview_path),
            }
        )
        print(f"rendered:{scenario['id']}:{mp4_path}")

    meta["scenarios"] = updated
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    index_path = demo_root / "README.md"
    index_path.write_text(
        build_index_markdown(meta.get("generated_at", ""), updated),
        encoding="utf-8",
    )
    print(f"index:{index_path}")


if __name__ == "__main__":
    main()
