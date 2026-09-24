#!/usr/bin/env python3
"""Generate the static homepage from links.toml for GitHub Pages."""

from __future__ import annotations

import html
import re
import tomllib
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "links.toml"
OUTPUT = ROOT / "index.html"
ICONS = ROOT / "media" / "icons"


def text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'"{field}" precisa ser um texto não vazio.')
    return value.strip()


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-") or "link"


def icon_for(name: str) -> str | None:
    slug = slugify(name)
    for extension in ("png", "ico"):
        candidate = ICONS / f"{slug}.{extension}"
        if candidate.is_file():
            return f"media/icons/{candidate.name}"
    return None


def safe_url(value: str, name: str) -> str:
    parts = urlsplit(value)
    if parts.scheme not in {"http", "https", "mailto"}:
        raise ValueError(f'URL inválida para "{name}": use http, https ou mailto.')
    if parts.scheme in {"http", "https"} and not parts.netloc:
        raise ValueError(f'URL inválida para "{name}": falta o domínio.')
    return value


def load_config() -> tuple[str, str, list[dict[str, str]]]:
    with CONFIG.open("rb") as source:
        data = tomllib.load(source)

    title = text(data.get("title", "Início"), "title")
    subtitle = data.get("subtitle", "Seus lugares favoritos, todos em um só lugar.")
    if not isinstance(subtitle, str):
        raise ValueError('"subtitle" precisa ser um texto.')

    raw_links = data.get("links", [])
    if not isinstance(raw_links, list):
        raise ValueError('Use um ou mais blocos "[[links]]" em links.toml.')

    links = []
    for index, raw_link in enumerate(raw_links, start=1):
        if not isinstance(raw_link, dict):
            raise ValueError(f'O link {index} precisa estar em um bloco "[[links]]".')
        name = text(raw_link.get("name"), f"links {index}.name")
        url = safe_url(text(raw_link.get("url"), f"links {index}.url"), name)
        group = raw_link.get("group", "Links")
        description = raw_link.get("description", "")
        icon = raw_link.get("icon")
        if not isinstance(group, str) or not isinstance(description, str):
            raise ValueError(f'"group" e "description" precisam ser texto (link "{name}").')
        if icon is not None:
            if not isinstance(icon, str) or not re.fullmatch(r"[a-z0-9-]+:[a-z0-9-]+", icon.strip()):
                raise ValueError(f'Ícone inválido para "{name}": use o formato Iconify "coleção:nome".')
            icon = icon.strip()
        links.append({
            "name": name,
            "url": url,
            "group": group.strip() or "Links",
            "description": description.strip(),
            "icon": icon or "",
        })
    return title, subtitle, links


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def make_card(link: dict[str, str]) -> str:
    if link["icon"]:
        icon = (
            f'<span class="link-icon" aria-hidden="true">'
            f'<iconify-icon icon="{esc(link["icon"])}"></iconify-icon></span>'
        )
    else:
        image_path = icon_for(link["name"])
        if image_path:
            icon = f'<img class="link-icon" src="{esc(image_path)}" alt="" loading="lazy">'
        else:
            initial = esc(link["name"].strip()[0].upper())
            icon = f'<span class="link-icon link-icon-fallback" aria-hidden="true">{initial}</span>'

    description = ""
    if link["description"]:
        description = f'<span class="link-description">{esc(link["description"])}</span>'
    target = "" if link["url"].startswith("mailto:") else ' target="_blank" rel="noopener noreferrer"'
    return (
        f'<a class="link-card" href="{esc(link["url"])}"{target}>'
        f'{icon}<span class="link-copy"><span class="link-name">{esc(link["name"])}</span>'
        f'{description}</span><span class="link-arrow" aria-hidden="true">↗</span></a>'
    )


def render(title: str, subtitle: str, links: list[dict[str, str]]) -> str:
    groups: dict[str, list[dict[str, str]]] = {}
    for link in links:
        groups.setdefault(link["group"], []).append(link)

    sections = []
    for group, group_links in groups.items():
        cards = "\n".join(make_card(link) for link in group_links)
        sections.append(
            f'<section class="link-group"><h2 class="group-title">{esc(group)}</h2>'
            f'<div class="link-grid">{cards}</div></section>'
        )

    if not sections:
        sections.append('<p class="status">Adicione seus primeiros links em links.toml.</p>')

    iconify_script = ""
    if any(link["icon"] for link in links):
        iconify_script = '<script src="https://code.iconify.design/iconify-icon/3.0.0/iconify-icon.min.js" defer></script>'

    return f'''<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#f6f7f9">
    <meta name="description" content="{esc(subtitle)}">
    <title>{esc(title)}</title>
    <link rel="stylesheet" href="./style.css">
    {iconify_script}
  </head>
  <body>
    <main class="page-shell">
      <header class="site-header">
        <div class="brand-mark" aria-hidden="true">✳</div>
        <p class="eyebrow">SEU ESPAÇO NA WEB</p>
        <h1>{esc(title)}</h1>
        <p class="subtitle">{esc(subtitle)}</p>
      </header>
      <div class="link-groups">
        {''.join(sections)}
      </div>
      <footer class="site-footer">Feito para ser simples <span aria-hidden="true">·</span> configurado em <code>links.toml</code></footer>
    </main>
  </body>
</html>
'''


def main() -> None:
    title, subtitle, links = load_config()
    OUTPUT.write_text(render(title, subtitle, links), encoding="utf-8")
    print(f"Página gerada: {OUTPUT.relative_to(ROOT)} ({len(links)} links)")


if __name__ == "__main__":
    try:
        main()
    except (OSError, tomllib.TOMLDecodeError, ValueError) as error:
        raise SystemExit(f"Erro ao gerar a página: {error}") from error
