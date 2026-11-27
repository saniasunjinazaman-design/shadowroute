#!/usr/bin/env python3
"""Build the five-AS Project Shadow Route lab with SEED Emulator."""
import os
from pathlib import Path
import sys

PROJECT_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = Path(os.environ.get("SEED_EMULATOR_DIR", PROJECT_DIR / "seed-emulator")).expanduser()
OUTPUT_DIR = PROJECT_DIR / "shadow-output"
if not REPO_DIR.is_dir():
    raise SystemExit(f"SEED Emulator repository not found: {REPO_DIR}\nSet SEED_EMULATOR_DIR if it is elsewhere.")
sys.path.insert(0, str(REPO_DIR))
from seedemu import *  # noqa: E402,F403


def build_emulator():
    emu, base, routing, ebgp = Emulator(), Base(), Routing(), Ebgp()
    base.createInternetExchange(100)
    for asn in (2, 3, 150, 151, 152):
        autonomous_system = base.createAutonomousSystem(asn)
        autonomous_system.createNetwork("net0")
        autonomous_system.createRouter("router0").joinNetwork("net0").joinNetwork("ix100")
        if asn in (150, 151, 152):
            autonomous_system.createHost("host0").joinNetwork("net0")
    ebgp.addPrivatePeering(100, 2, 150, abRelationship=PeerRelationship.Provider)
    ebgp.addPrivatePeering(100, 3, 151, abRelationship=PeerRelationship.Provider)
    ebgp.addPrivatePeering(100, 3, 152, abRelationship=PeerRelationship.Provider)
    ebgp.addPrivatePeering(100, 2, 3, abRelationship=PeerRelationship.Peer)
    emu.addLayer(base); emu.addLayer(routing); emu.addLayer(ebgp)
    return emu


def main():
    if OUTPUT_DIR.exists():
        raise SystemExit(f"Output already exists: {OUTPUT_DIR}\nStopped to avoid overwriting it.")
    emu = build_emulator()
    emu.render()
    emu.compile(Docker(platform=Platform.AMD64), str(OUTPUT_DIR), override=False)
    print(f"Configuration generated: {OUTPUT_DIR}")
    print("Containers have NOT been built or started.")


if __name__ == "__main__":
    main()
