#!/usr/bin/env python3
"""
comunicaciones — genera comunicados con la estética de BAE Limpieza
(logo, colores y tipografías de marca) en HTML y PDF.

Pensado para reemplazos temporales de personal ("Fulana se toma unos
días, la reemplaza Mengana"), pero sirve para cualquier comunicado
corto de una sola pieza (tamaño A4, A5 o A6).

Uso típico:

    python3 generar_comunicado.py \
        --saliente "Silvina Aguirre" \
        --entrante "Angela Aquino" \
        --desde "viernes 2/10" \
        --tamano A6 \
        --salida comunicado-silvina.pdf

También se puede usar como módulo (por ejemplo desde OpenClaw u otro
orquestador local) importando `generar_comunicado()`.

Requisitos (una sola vez):
    pip install -r requirements.txt
    playwright install chromium
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR
LOGO_PATH = BASE_DIR / "assets" / "logo-bae.png"

# Tamaños de página soportados y su ajuste tipográfico/espaciado.
# Cada preset fue calibrado a mano para que el diseño se vea prolijo
# en ese tamaño específico (no es una simple regla de tres).
PRESETS = {
    "A4": {
        "page_size": "A4",
        "sheet_width": "210mm", "sheet_height": "297mm", "sheet_padding": "22mm 18mm",
        "gap_brand": "14px", "logo_width": "56px",
        "fs_brand_name": "20px", "fs_brand_tag": "10.5px",
        "body_block_margin": "56px",
        "fs_eyebrow": "13px", "eyebrow_margin": "14px",
        "fs_h1": "38px", "h1_margin": "28px",
        "swap_gap": "22px", "swap_padding": "30px 34px", "swap_margin": "30px",
        "fs_who": "30px", "fs_who_out": "24px", "fs_arrow": "26px", "fs_from": "12px",
        "fs_note": "16px", "note_gap": "14px",
        "footer_padding": "28px",
        "fs_footer_contact": "13.5px", "fs_footer_name": "15px", "fs_footer_stamp": "10.5px",
    },
    "A5": {
        "page_size": "A5",
        "sheet_width": "148mm", "sheet_height": "210mm", "sheet_padding": "14mm 12mm",
        "gap_brand": "14px", "logo_width": "44px",
        "fs_brand_name": "16px", "fs_brand_tag": "9px",
        "body_block_margin": "30px",
        "fs_eyebrow": "11px", "eyebrow_margin": "10px",
        "fs_h1": "26px", "h1_margin": "18px",
        "swap_gap": "14px", "swap_padding": "18px 20px", "swap_margin": "20px",
        "fs_who": "20px", "fs_who_out": "16px", "fs_arrow": "18px", "fs_from": "12px",
        "fs_note": "12.5px", "note_gap": "14px",
        "footer_padding": "16px",
        "fs_footer_contact": "10.5px", "fs_footer_name": "12px", "fs_footer_stamp": "8.5px",
    },
    "A6": {
        "page_size": "A6",
        "sheet_width": "105mm", "sheet_height": "148mm", "sheet_padding": "8mm 8mm",
        "gap_brand": "8px", "logo_width": "30px",
        "fs_brand_name": "12px", "fs_brand_tag": "6.5px",
        "body_block_margin": "14px",
        "fs_eyebrow": "8px", "eyebrow_margin": "6px",
        "fs_h1": "17px", "h1_margin": "10px",
        "swap_gap": "6px", "swap_padding": "10px 12px", "swap_margin": "12px",
        "fs_who": "13px", "fs_who_out": "10.5px", "fs_arrow": "12px", "fs_from": "7px",
        "fs_note": "8.5px", "note_gap": "8px",
        "footer_padding": "8px",
        "fs_footer_contact": "7px", "fs_footer_name": "8.5px", "fs_footer_stamp": "6px",
    },
}


def generar_comunicado(
    saliente: str,
    entrante: str,
    desde: str,
    salida: str,
    tamano: str = "A6",
    titulo: str = "Reemplazo temporal de personal",
    eyebrow: str = "Comunicado",
    parrafos: list[str] | None = None,
    guardar_html: str | None = None,
) -> Path:
    """Genera el comunicado y devuelve la ruta del PDF creado.

    - saliente / entrante: nombre y apellido de cada persona.
    - desde: texto libre, ej. "viernes 2/10" o "el lunes que viene".
    - tamano: "A4", "A5" o "A6".
    - parrafos: lista de párrafos HTML (con <b> permitido). Si no se
      pasa, se arma el texto estándar de reemplazo por vacaciones.
    - guardar_html: si se indica una ruta, además del PDF se guarda
      el HTML final ahí (útil para revisar o para subir como Artifact).
    """
    tamano = tamano.upper()
    if tamano not in PRESETS:
        raise ValueError(f"Tamaño no soportado: {tamano!r} (usar A4, A5 o A6)")

    if parrafos is None:
        parrafos = [
            f"<b>{saliente}</b> se toma unos días de vacaciones a partir del {desde}. "
            f"Durante su ausencia, el servicio quedará a cargo de <b>{entrante}</b>, "
            f"quien continuará con la misma dedicación y calidad de siempre.",
            "Ante cualquier consulta o novedad, quedamos a disposición por este medio.",
        ]

    ctx = dict(PRESETS[tamano])
    ctx.update(
        eyebrow=eyebrow,
        titulo=titulo,
        desde_texto=f"A partir del {desde}".upper(),
        persona_saliente=saliente,
        persona_entrante=entrante,
        parrafos=parrafos,
        logo_path=LOGO_PATH.resolve().as_uri(),
    )

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    html = env.get_template("template.html").render(**ctx)

    salida_path = Path(salida).resolve()
    salida_path.parent.mkdir(parents=True, exist_ok=True)

    if guardar_html:
        html_path = Path(guardar_html).resolve()
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(html, encoding="utf-8")
    else:
        html_path = salida_path.with_suffix(".tmp.html")
        html_path.write_text(html, encoding="utf-8")

    _renderizar_pdf(html_path, salida_path, ctx["page_size"])

    if not guardar_html:
        html_path.unlink(missing_ok=True)

    return salida_path


def _renderizar_pdf(html_path: Path, pdf_path: Path, page_size: str) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.resolve().as_uri())
        page.wait_for_timeout(300)
        page.pdf(
            path=str(pdf_path),
            format=page_size,
            print_background=True,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
        )
        browser.close()


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera un comunicado con la estética BAE.")
    parser.add_argument("--saliente", required=True, help="Nombre y apellido de quien se ausenta")
    parser.add_argument("--entrante", required=True, help="Nombre y apellido de quien reemplaza")
    parser.add_argument("--desde", required=True, help='Ej: "viernes 2/10"')
    parser.add_argument("--tamano", default="A6", choices=["A4", "A5", "A6", "a4", "a5", "a6"])
    parser.add_argument("--titulo", default="Reemplazo temporal de personal")
    parser.add_argument("--salida", default="comunicado.pdf", help="Ruta del PDF a generar")
    parser.add_argument("--guardar-html", default=None, help="Si se indica, guarda también el HTML en esa ruta")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    ruta = generar_comunicado(
        saliente=args.saliente,
        entrante=args.entrante,
        desde=args.desde,
        salida=args.salida,
        tamano=args.tamano,
        titulo=args.titulo,
        guardar_html=args.guardar_html,
    )
    print(f"Comunicado generado: {ruta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
