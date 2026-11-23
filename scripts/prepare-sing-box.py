"""Prepare the latest stable sing-box package in the current OpenWrt tree."""

import hashlib
import json
import re
import shutil
import subprocess
import tarfile
import tempfile
from email.parser import Parser
from pathlib import Path


def curl(url, *args):
    return subprocess.check_output(
        ["curl", "--fail", "--silent", "--show-error", "--location",
         "--retry", "3", *args, url]
    )


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prepare():
    arch = "aarch64_cortex-a53"
    if f'CONFIG_TARGET_ARCH_PACKAGES="{arch}"' not in Path(".config").read_text().splitlines():
        raise ValueError(f"Expected OpenWrt target architecture {arch}")

    feed = Path("feeds/packages/net/sing-box/Makefile")
    registration = "$(eval $(call BuildPackage,sing-box))"
    recipe = feed.read_text()
    if recipe.splitlines().count(registration) != 1:
        raise ValueError(f"Cannot identify the full sing-box package in {feed}")

    release = json.loads(curl("https://api.github.com/repos/SagerNet/sing-box/releases/latest"))
    tag = release["tag_name"]
    if release["draft"] or release["prerelease"] or not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
        raise ValueError(f"Expected a stable release, received {tag!r}")
    version = tag[1:]
    name = f"sing-box_{version}_openwrt_{arch}.ipk"
    asset = next((asset for asset in release["assets"] if asset["name"] == name), None)
    if not asset or not re.fullmatch(r"sha256:[0-9a-f]{64}", asset.get("digest") or ""):
        raise ValueError(f"Official release {tag} lacks {name} or its SHA-256")
    expected = asset["digest"].split(":")[1]

    archive = Path("dl") / name
    archive.parent.mkdir(exist_ok=True)
    if not archive.exists() or sha256(archive) != expected:
        with tempfile.TemporaryDirectory(dir=archive.parent) as temp:
            download = Path(temp) / name
            curl(asset["browser_download_url"], "--output", str(download))
            if sha256(download) != expected:
                raise ValueError(f"SHA-256 mismatch for {name}")
            download.replace(archive)

    with tarfile.open(archive) as ipk:
        with tarfile.open(fileobj=ipk.extractfile("control.tar.gz")) as control:
            entry = next(m for m in control if m.name.removeprefix("./") == "control")
            metadata = Parser().parsestr(control.extractfile(entry).read().decode())
    if (metadata["Package"], metadata["Version"], metadata["Architecture"]) != ("sing-box", version, arch):
        raise ValueError(f"Package metadata disagrees with {name}")
    deps = [item.strip() for item in metadata["Depends"].split(",")]
    if not all(re.fullmatch(r"[a-z0-9][a-z0-9.+-]*", item) for item in deps):
        raise ValueError(f"Review new dependency constraints before packaging: {deps}")

    package = Path("package/sing-box-stable")
    package.mkdir(exist_ok=True)
    shutil.copyfile(Path(__file__).resolve().parents[1] / package / "Makefile", package / "Makefile")
    (package / "release.mk").write_text(
        f"SING_BOX_VERSION:={version}\nSING_BOX_SHA256:={expected}\n"
        f"SING_BOX_DEPENDS:={' '.join(deps)}\n"
    )
    # The feed still provides sing-box-tiny and the ImmortalWrt service files.
    feed.write_text(recipe.replace(registration, "# Full sing-box is provided by sing-box-stable."))
    print(f"Using {name}, SHA-256 {expected}, dependencies: {', '.join(deps)}")


if __name__ == "__main__":
    prepare()
