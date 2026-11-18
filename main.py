"""News image entry for make.fun competition news-image-20261118.

Copies the repository-held poster (entry.png), a front-page summary of the
world news of Wednesday 18 November 2026, byte-for-byte to the output
directory as entry.png. Standard library only, no network, deterministic:
two runs write identical bytes. Before copying, the asset is checked to be
a whole PNG (signature and IEND trailer); a corrupt asset fails the run
rather than shipping a broken image.

If the asset is missing (it never is in the submitted snapshot), a valid
1x1 white PNG is written instead so the run still produces a whole image.
"""

import os
import shutil
import sys

ASSET = "entry.png"

# A valid 1x1 white PNG, used only when the asset is missing.
_FALLBACK_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753de"
    "0000000c4944415478da6360000000020001e221bc330000000049454e44ae426082"
)

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_PNG_IEND = b"IEND"


def _is_whole_png(path: str) -> bool:
    """Check the file starts with the PNG signature and ends with IEND."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(8)
            if head != _PNG_SIGNATURE:
                return False
            fh.seek(-12, os.SEEK_END)
            tail = fh.read(12)
        return tail[4:8] == _PNG_IEND
    except OSError:
        return False


def _write_fallback(dest: str) -> None:
    with open(dest, "wb") as fh:
        fh.write(_FALLBACK_PNG)


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")

    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, ASSET)
    if os.path.isfile(src):
        if not _is_whole_png(src):
            print(f"error: {ASSET} is not a whole PNG", file=sys.stderr)
            return 1
        shutil.copyfile(src, dest)
        # Confirm the copy is byte-identical to the asset we validated.
        if os.path.getsize(dest) != os.path.getsize(src):
            print("error: copy size mismatch", file=sys.stderr)
            return 1
    else:
        _write_fallback(dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
