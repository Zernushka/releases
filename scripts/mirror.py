#!/usr/bin/env python3
"""Зеркало релизов Зернушки на GitHub Releases.

Источник истины — официальная раздача https://зернушка.рф/dl/:
  latest.json  — версия и список файлов (формат GitHub Releases API);
  SHA256SUMS   — контрольные суммы; без совпадения файл не публикуется;
  release.json / appcast.xml — текст «что нового».
Скрипт ничего не собирает и исходников не содержит: только перекладывает
уже опубликованные сборки после проверки SHA-256.

  python3 scripts/mirror.py            # опубликовать отсутствующие релизы
                                       # + обновить оформление старых (см. NOTES_VER)
  python3 scripts/mirror.py --dry-run  # скачать и проверить, но не публиковать
  python3 scripts/mirror.py --renotes  # только перерисовать описания существующих релизов
"""
import argparse, hashlib, json, os, re, subprocess, sys, tempfile, urllib.request
from urllib.parse import quote
import xml.etree.ElementTree as ET

BASE = os.environ.get("ZERN_DL_BASE", "https://xn--80ajfnorw4b.xn--p1ai/dl/")
REPO = os.environ.get("GITHUB_REPOSITORY", "Zernushka/releases")
UA = {"User-Agent": "zernushka-release-mirror/1.1"}

# Версия оформления. Релизы, в описании которых нет маркера с этим номером,
# перерисовываются при каждом прогоне (файлы не трогаются — только текст).
NOTES_VER = 2
MARK = f"<!-- zern-notes v{NOTES_VER} -->"

# Логотип Windows для бейджа (у shields.io нет встроенного).
WIN_LOGO = ("data:image/svg%2Bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAg"
            "MCAyNCAyNCI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTMgNC41IDExIDMuNHY4LjFIM3ptOSAtMS4yTDIxIDJ2OS41aC05ek0z"
            "IDEyLjVoOHY4LjFMMyAxOS41em05IDBoOVYyMmwtOS0xLjN6Ii8+PC9zdmc+")

# Описание файлов: ключ в имени → (платформа, кому подходит, цвет, логотип, подпись на кнопке)
KINDS = [
    ("arm64",  "Android",    "телефоны и планшеты — подходит почти всем",        "3DDC84", "android",  "APK · arm64"),
    ("armv7",  "Android TV", "телевизоры, приставки и старые 32-битные устройства", "1E88E5", "android",  "APK · armv7"),
    ("x86_64", "Android x86", "устройства на Intel и эмуляторы",                  "8E24AA", "android",  "APK · x86__64"),
    ("Setup",  "Windows",    "Windows 10 / 11, установщик",                       "0078D4", WIN_LOGO,  "Setup.exe"),
]


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
    # основной источник — release.json (коротко + подробно), запасной — appcast.xml
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


# ---------- оформление ----------

def badge(label, msg, color, logo=None):
    enc = lambda s: quote(s.replace("-", "--"), safe="")
    u = f"https://img.shields.io/badge/{enc(label)}-{enc(msg)}-{color}?style=for-the-badge"
    if logo:
        u += f"&logo={logo}&logoColor=white"
    return u


def kind_of(name):
    return next((k for k in KINDS if k[0] in name), None)


def build_notes(tag, ver, rows, new):
    """rows: [(name, size_bytes, sha256)] в порядке публикации."""
    dl = f"https://github.com/{REPO}/releases/download/{tag}/"
    order = {k[0]: i for i, k in enumerate(KINDS)}
    rows = sorted(rows, key=lambda r: order.get((kind_of(r[0]) or ("",))[0], 99))

    n = [MARK, "",
         f"<p align=\"center\"><b>Зернушка {ver}</b> — Android · Android TV · Windows</p>", ""]

    if new:
        n += ["## ✨ Что нового", "", new, ""]

    n += ["## ⬇️ Скачать", "",
          "| Для чего | Скачать | Размер |",
          "|:--|:--|--:|"]
    for name, size, h in rows:
        k = kind_of(name)
        if not k:
            n.append(f"| `{name}` | [скачать]({dl}{name}) | {size/1048576:.1f} МБ |"); continue
        _, plat, who, color, logo, btn = k
        n.append(f"| **{plat}** — {who} | [![{plat}]({badge(plat, btn, color, logo)})]({dl}{name}) | {size/1048576:.1f} МБ |")
    n += ["",
          "<details><summary>Какой APK выбрать?</summary>", "",
          "- Обычный телефон или планшет — **arm64**. Если не устанавливается — попробуйте **armv7**.",
          "- Телевизор или приставка на Android TV — **armv7** (ставится через файловый менеджер или Send Files to TV).",
          "- Эмулятор на компьютере (BlueStacks и т.п.) или устройство на Intel — **x86_64**.",
          "- Windows — `Setup.exe`. SmartScreen может предупредить о неизвестном издателе: «Подробнее» → «Выполнить в любом случае».",
          "", "</details>", "",
          "## 🔐 Подлинность", "",
          "Это зеркало официальной раздачи [зернушка.рф/dl](https://xn--80ajfnorw4b.xn--p1ai/dl/). "
          "Файлы здесь — те же самые, побайтно: перед публикацией каждый сверен с `SHA256SUMS` официальной раздачи.",
          "", "<details><summary>SHA-256</summary>", "",
          "| файл | SHA-256 |", "|:--|:--|"]
    for name, size, h in rows:
        n.append(f"| `{name}` | `{h}` |")
    n += ["", "Проверить у себя: Windows — `certutil -hashfile файл SHA256`; Linux/macOS — `sha256sum файл`.",
          "", "</details>", "",
          "## 💬 Связь", "",
          "<p>"
          f"<a href=\"https://t.me/Zernushka_bot\"><img alt=\"Бот\" src=\"{badge('Telegram', 'бот и подписка', '26A5E4', 'telegram')}\"></a> "
          f"<a href=\"https://t.me/Zernushka_support_bot\"><img alt=\"Поддержка\" src=\"{badge('Telegram', 'поддержка', '26A5E4', 'telegram')}\"></a> "
          f"<a href=\"https://xn--80ajfnorw4b.xn--p1ai/\"><img alt=\"Сайт\" src=\"{badge('зернушка.рф', 'сайт', '2E7D32')}\"></a> "
          f"<a href=\"https://zernushka.store\"><img alt=\"Витрина\" src=\"{badge('zernushka.store', 'витрина', '6D4C41')}\"></a>"
          "</p>"]
    return "\n".join(n) + "\n"


# ---------- GitHub ----------

def gh_json(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def released(tag):
    r = subprocess.run(["gh", "release", "view", tag], capture_output=True, text=True)
    return r.returncode == 0


def renotes(dry_run):
    """Перерисовать описания релизов, у которых нет маркера текущей версии оформления."""
    rels = gh_json("release", "list", "--json", "tagName,isDraft,isPrerelease", "--limit", "100")
    for rel in rels:
        tag = rel["tagName"]; ver = tag.lstrip("v")
        if rel.get("isDraft"):
            continue
        info = gh_json("release", "view", tag, "--json", "body,assets")
        body = info.get("body") or ""
        if MARK in body:
            continue
        # SHA-256 берём из старого описания (там таблица) — файлы заново не качаем
        old_sha = dict(re.findall(r"`([^`\s]+)`\s*\|[^|\n]*\|[^|\n]*\|\s*`([0-9a-f]{64})`", body))
        old_sha.update(dict(re.findall(r"`([^`\s]+)`\s*\|\s*`([0-9a-f]{64})`", body)))
        rows = []
        for a in info["assets"]:
            h = old_sha.get(a["name"])
            if not h:
                print(f"{tag}: нет SHA для {a['name']} в старом описании — пропуск релиза"); rows = None; break
            rows.append((a["name"], int(a["size"]), h))
        if not rows:
            continue
        m = (re.search(r"\*\*Что нового:\*\*\s*(.*?)(?:\n\s*\n(?:Это зеркало|<!--|##)|\Z)", body, re.S)
             or re.search(r"## ✨ Что нового\s*\n(.*?)\n\s*\n## ", body, re.S))
        new = (m.group(1).strip() if m else "") or whats_new(ver)
        notes = build_notes(tag, ver, rows, new)
        if dry_run:
            print(f"--- {tag} ---\n{notes}"); continue
        nf = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
        nf.write(notes); nf.close()
        subprocess.run(["gh", "release", "edit", tag, "--notes-file", nf.name], check=True)
        print(f"{tag}: описание обновлено (v{NOTES_VER})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--renotes", action="store_true", help="только перерисовать описания")
    a = ap.parse_args()

    if a.renotes:
        renotes(a.dry_run); return

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
        notes = build_notes(tag, ver, rows, whats_new(ver))
        nf = os.path.join(tmp, "NOTES.md")
        open(nf, "w", encoding="utf-8").write(notes)
        if a.dry_run:
            print(notes); continue
        subprocess.run(["gh", "release", "create", tag, *files, "--title", f"Зернушка {ver}",
                        "--notes-file", nf, "--latest"], check=True)
        print(f"{tag}: опубликован")

    # старые релизы — подтянуть оформление
    if not a.dry_run:
        renotes(False)


if __name__ == "__main__":
    main()
