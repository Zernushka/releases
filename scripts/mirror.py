#!/usr/bin/env python3
"""Зеркало релизов Зернушки на GitHub Releases.

Источник истины — официальная раздача https://зернушка.рф/dl/:
  latest.json  — версия и список файлов (формат GitHub Releases API);
  SHA256SUMS   — контрольные суммы; без совпадения файл не публикуется;
  appcast.xml  — текст «что нового» (если найдётся).
Скрипт ничего не собирает и исходников не содержит: только перекладывает
уже опубликованные сборки после проверки SHA-256.

  python3 scripts/mirror.py            # опубликовать отсутствующие релизы
  python3 scripts/mirror.py --dry-run  # скачать и проверить, но не публиковать
"""
import argparse, hashlib, json, os, re, subprocess, sys, tempfile, urllib.request
import xml.etree.ElementTree as ET

BASE = os.environ.get("ZERN_DL_BASE", "https://xn--80ajfnorw4b.xn--p1ai/dl/")
UA = {"User-Agent": "zernushka-release-mirror/1.0"}


def get(url, timeout=60):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def download(url, path):
    h = hashlib.sha256()
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r, open(path, "wb") as f:
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            h.update(b); f.write(b)
    return h.hexdigest()


def sums():
    out = {}
    for line in get(BASE + "SHA256SUMS").decode().splitlines():
        m = re.match(r"^([0-9a-f]{64})\s+\*?(\S+)$", line.strip())
        if m:
            out[m.group(2)] = m.group(1)
    if not out:
        raise SystemExit("SHA256SUMS пуст или не читается — стоп")
    return out


def whats_new(version):
    # 24.09.2026: основной источник — release.json (коротко + подробно), запасной — appcast.xml
    try:
        r = json.loads(get(BASE + "release.json"))
        if r.get("version") == version and r.get("notes_short"):
            return (r["notes_short"] + ("\n\n" + r["notes_full"] if r.get("notes_full") else "")).strip()
    except Exception:
        pass
    try:
        root = ET.fromstring(get(BASE + "appcast.xml"))
    except Exception:
        return ""
    for item in root.iter("item"):
        blob = ET.tostring(item, encoding="unicode")
        if version in blob:
            d = item.findtext("description") or ""
            return re.sub(r"<[^>]+>", "", d).strip()
    return ""


def released(tag):
    r = subprocess.run(["gh", "release", "view", tag], capture_output=True, text=True)
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    rels = json.loads(get(BASE + "latest.json"))
    assert isinstance(rels, list) and rels, "latest.json: ожидался непустой массив"
    sha = sums()
    for rel in rels:
        tag = rel["tag_name"]; ver = tag.lstrip("v")
        assert re.fullmatch(r"v\d+\.\d+\.\d+", tag), f"странный тег {tag!r}"
        if rel.get("prerelease"):
            print(f"{tag}: prerelease — пропуск"); continue
        if not a.dry_run and released(tag):
            print(f"{tag}: уже на GitHub"); continue
        tmp = tempfile.mkdtemp(prefix="zern-")
        files, rows = [], []
        for asset in rel["assets"]:
            name = asset["name"]; url = asset["browser_download_url"]
            assert url.startswith(BASE), f"{name}: ссылка не на официальную раздачу: {url}"
            want = sha.get(name)
            if not want:
                raise SystemExit(f"{name}: нет в SHA256SUMS — стоп, ничего не публикую")
            path = os.path.join(tmp, name)
            got = download(url, path)
            if got != want:
                raise SystemExit(f"{name}: SHA-256 не совпал ({got} != {want}) — стоп")
            size = os.path.getsize(path)
            print(f"{name}: ok {size} байт {got}")
            files.append(path); rows.append((name, size, got))
        new = whats_new(ver)
        notes = [f"Зернушка {ver}.", ""]
        if new:
            notes += ["**Что нового:** " + new, ""]
        notes += [
            "Это зеркало. Официальная раздача: https://зернушка.рф/dl/ · витрина: https://zernushka.store",
            "Файлы здесь — те же самые, побайтно: перед публикацией каждый сверен с SHA256SUMS официальной раздачи.",
            "",
            "| файл | для чего | размер | SHA-256 |",
            "|---|---|---|---|",
        ]
        what = {"arm64": "Android, большинство телефонов", "armv7": "Android 32-бит, телевизоры",
                "x86_64": "Android на Intel/эмуляторы", "Setup": "Windows 10/11"}
        for name, size, h in rows:
            k = next((k for k in what if k in name), "")
            notes.append(f"| `{name}` | {what.get(k, '')} | {size/1048576:.1f} МБ | `{h}` |")
        nf = os.path.join(tmp, "NOTES.md")
        open(nf, "w", encoding="utf-8").write("\n".join(notes) + "\n")
        if a.dry_run:
            print("\n".join(notes)); continue
        subprocess.run(["gh", "release", "create", tag, *files, "--title", f"Зернушка {ver}",
                        "--notes-file", nf, "--latest"], check=True)
        print(f"{tag}: опубликован")


if __name__ == "__main__":
    main()
