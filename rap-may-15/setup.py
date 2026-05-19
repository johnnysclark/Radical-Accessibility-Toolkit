"""macOS-focused installer for the Radical Accessibility Toolkit demo."""
import argparse
import datetime
import json
import os
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Install the rap-may-15 macOS demo.")
    parser.add_argument(
        "--allow-non-mac",
        action="store_true",
        help="Override the macOS platform check.")
    args = parser.parse_args()

    if sys.platform != "darwin" and not args.allow_non_mac:
        print("ERROR: This installer targets macOS. "
              "Pass --allow-non-mac to override.")
        sys.exit(1)

    if not os.path.isdir("output") or not os.path.isdir("controller"):
        print("ERROR: Run this from the rap-may-15/ folder.")
        sys.exit(1)

    print("OK: Installing output package...")
    print("OK: Removing legacy 'tact' install (if present) before reinstalling as 'output'.")
    subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", "-y", "tact"],
        check=False)
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", "./output"],
        check=True)

    print("OK: Installing MCP server requirements...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "mcp/requirements.txt"],
        check=True)

    if not os.path.exists(".mcp.json"):
        with open(".mcp.json.example", "r") as fh:
            text = fh.read()
        base = os.path.abspath(".")
        text = text.replace(
            '"mcp/server.py"',
            '"{}/mcp/server.py"'.format(base))
        text = text.replace(
            '"controller/state.json"',
            '"{}/controller/state.json"'.format(base))
        text = text.replace(
            '"output/mcp_entry.py"',
            '"{}/output/mcp_entry.py"'.format(base))
        with open(".mcp.json", "w") as fh:
            fh.write(text)

    state_path = os.path.join("controller", "state.json")
    if not os.path.exists(state_path):
        now = datetime.datetime.utcnow().isoformat() + "Z"
        state = {
            "schema": "rap_controller_v1.0",
            "meta": {"created": now},
            "site": {
                "origin": [0, 0],
                "width": 100,
                "height": 80,
                "corners": [[0, 0], [100, 0], [100, 80], [0, 80]],
                "units": "feet",
            },
            "zones": {},
            "bays": {},
            "walls": [],
            "apertures": [],
        }
        with open(state_path, "w") as fh:
            json.dump(state, fh, indent=2)

    # Offer to load the case-study-house example
    example_src = os.path.join("examples", "case-study-house.state.json")
    example_macro = os.path.join("examples", "case-study-house.macro.json")
    macros_dir = os.path.join("controller", "macros")
    if os.path.isfile(example_src):
        print("OK: A case-study-house example is bundled in examples/.")
        answer = ""
        try:
            answer = input("Load it as the active state now? [Y/n] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            answer = "n"
        if answer in ("", "y", "yes"):
            import shutil
            shutil.copyfile(example_src, os.path.join("controller", "state.json"))
            os.makedirs(macros_dir, exist_ok=True)
            if os.path.isfile(example_macro):
                shutil.copyfile(example_macro, os.path.join(macros_dir, "case-study-house.macro.json"))
            print("OK: Loaded examples/case-study-house.state.json into controller/state.json")
            print("OK: Copied case-study-house.macro.json into controller/macros/")
        else:
            print("Skipped. To load later: cp examples/case-study-house.state.json controller/state.json")

    print("OK: Setup complete.")
    print("Next: ./scripts/start-mac.sh")


if __name__ == "__main__":
    main()
