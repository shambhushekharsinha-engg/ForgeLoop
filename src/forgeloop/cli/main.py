"""Linux-oriented, key-free experiment analysis and saved result workflow."""

import argparse
import io
import json
import sqlite3
import sys
from pathlib import Path

from ..experiments.store import ExperimentStore, read_input


def analyze(args):
    # Read once: analysis and stored evidence must refer to the same bytes.
    csv_bytes = read_input(args.trajectory)
    transcript_bytes = read_input(args.transcript)
    transcript = transcript_bytes.decode("utf-8")
    try:
        from ..data.trajectory import Trajectory
    except ImportError as error:
        raise ValueError(
            'Install analysis dependencies: pip install ".[analysis]"'
        ) from error
    import pandas as pd

    from ..decisions.decision import DecisionStatus, HumanDecision
    from ..decisions.proposal import AIProposal
    from ..evaluation.integrity import calculate_integrity
    from ..evaluation.orbit import calculate_orbit_progress
    from ..evaluation.speed import calculate_speed_score
    from ..experiments.experiment import Experiment
    from ..experiments.runner import ExperimentRunner

    trajectory = Trajectory.__new__(Trajectory)
    trajectory.filepath = Path(args.trajectory)
    trajectory.data = pd.read_csv(io.BytesIO(csv_bytes))
    trajectory.validate()
    orbit = calculate_orbit_progress(trajectory)
    speed = calculate_speed_score(
        trajectory, orbit, reference_duration=args.reference_duration
    )
    integrity = calculate_integrity(trajectory)
    exp = Experiment(
        id=args.id,
        build_mode=args.build_mode,
        hypothesis=args.hypothesis,
        proposal=AIProposal(
            id=args.id + "-proposal",
            strategy=args.strategy,
            expected_benefit=args.hypothesis,
        ),
        human_decision=HumanDecision(
            status=DecisionStatus(args.decision), reason=args.reason
        ),
        notes=f"User-declared {args.evidence_kind} input. Local estimate, not an official score.",
    )
    ExperimentRunner().evaluate_experiment(exp, orbit, speed, integrity, transcript)
    record = ExperimentStore(args.store).save(
        exp,
        csv_bytes,
        transcript_bytes,
        evidence_kind=args.evidence_kind,
        assumptions={
            "format": "forgeloop-normalized-v1",
            "target_degrees": 1080,
            "reference_duration_seconds": args.reference_duration,
            "angular_progress": "signed cumulative degrees",
            "token_estimate": "UTF-8 bytes / 4 rounded up",
            "penalty_per_1000_tokens": 0.1,
        },
    )
    print(json.dumps(record, indent=2, allow_nan=False))


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # Keep specialized parsers' complete help and options.
    if argv and argv[0] in ("catalog", "doctor"):
        if argv[0] == "catalog":
            from .catalog import main as command
        else:
            from .doctor import main as command
        return command(argv[1:])
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("catalog", help="Search pinned public block metadata offline")
    commands.add_parser("doctor", help="Check local runtime dependencies")
    analysis = commands.add_parser(
        "analyze", help="Evaluate normalized CSV and save original evidence"
    )
    analysis.add_argument("trajectory", type=Path)
    analysis.add_argument("--transcript", type=Path, required=True)
    analysis.add_argument("--id", required=True)
    analysis.add_argument("--hypothesis", required=True)
    analysis.add_argument("--strategy", required=True)
    analysis.add_argument(
        "--decision",
        choices=["ACCEPT", "REJECT"],
        required=True,
        help="Recorded human review; modified strategies should be supplied as the reviewed strategy",
    )
    analysis.add_argument("--reason", required=True)
    analysis.add_argument(
        "--build-mode", choices=["Copilot", "Autopilot"], required=True
    )
    analysis.add_argument(
        "--evidence-kind", choices=["measured", "synthetic"], required=True
    )
    analysis.add_argument(
        "--reference-duration",
        type=float,
        required=True,
        help="Explicit local speed baseline in seconds",
    )
    analysis.add_argument(
        "--store", type=Path, default=Path("runs/experiments.sqlite3")
    )
    listing = commands.add_parser(
        "list", help="Inspect saved experiments and verify evidence hashes"
    )
    listing.add_argument("--store", type=Path, default=Path("runs/experiments.sqlite3"))
    listing.add_argument("--evidence-kind", choices=["measured", "synthetic"])
    dashboard = commands.add_parser(
        "dashboard", help="Export saved results for one evidence category"
    )
    dashboard.add_argument(
        "--store", type=Path, default=Path("runs/experiments.sqlite3")
    )
    dashboard.add_argument(
        "--evidence-kind", choices=["measured", "synthetic"], required=True
    )
    dashboard.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "analyze":
            analyze(args)
        elif args.command == "list":
            print(
                json.dumps(
                    ExperimentStore(args.store).records(args.evidence_kind),
                    indent=2,
                    allow_nan=False,
                )
            )
        elif args.command == "dashboard":
            from .export_web import export_dashboard

            store = ExperimentStore(args.store)
            if (
                args.output.resolve() == store.path
                or args.output.resolve() in store.path.parents
            ):
                raise ValueError(
                    "Dashboard output must be separate from the evidence database"
                )
            registry = store.registry(args.evidence_kind)
            output = export_dashboard(
                registry, output_dir=args.output, plots_dir=args.output / "plots"
            )
            # The exporter escapes all registry values. Make the category explicit.
            page = output.read_text(encoding="utf-8").replace(
                "Local Experiment Dashboard",
                f"{args.evidence_kind.title()} Inputs — Local Estimates",
            )
            page = page.replace(
                "No evaluated experiments supplied.",
                f"No {args.evidence_kind} experiments supplied.",
            )
            page = page.replace(
                "<body ", '<body data-evidence-kind="' + args.evidence_kind + '" ', 1
            )
            # Visible label alongside the page heading, without modifying layout.
            page = page.replace(
                "ForgeLoop<span",
                args.evidence_kind.title() + " Inputs · ForgeLoop<span",
                1,
            )
            output.write_text(page, encoding="utf-8")
    except (OSError, ValueError, sqlite3.Error) as error:
        parser.exit(2, f"ForgeLoop error: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
