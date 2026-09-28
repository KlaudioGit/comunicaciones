# comunicaciones

Script para generar comunicados cortos (reemplazos de personal, avisos puntuales)
con la identidad visual de **BAE Limpieza**: logo real, paleta de colores
(azul BAE, terracota, crema, carbón cálido) y tipografías de marca (Cardo + Inter
+ IBM Plex Mono), en formato **A4, A5 o A6**, listos para imprimir o mandar por
WhatsApp como PDF.

Nació del comunicado de reemplazo de Silvina Aguirre por Angela Aquino
(vacaciones desde el 2/10/2026) y quedó parametrizado para reusarlo con
cualquier otro nombre, fecha o tamaño de hoja.

## Instalación

```bash
pip install -r requirements.txt
playwright install chromium
```

(`playwright install chromium` solo hace falta una vez por máquina — descarga
el motor que arma el PDF.)

## Uso por línea de comandos

```bash
python3 generar_comunicado.py \
  --saliente "Silvina Aguirre" \
  --entrante "Angela Aquino" \
  --desde "viernes 2/10" \
  --tamano A6 \
  --salida salida/comunicado-silvina.pdf
```

Parámetros:

| Flag | Obligatorio | Descripción |
|---|---|---|
| `--saliente` | sí | Nombre y apellido de quien se ausenta |
| `--entrante` | sí | Nombre y apellido de quien reemplaza |
| `--desde` | sí | Texto libre, ej. `"viernes 2/10"` |
| `--tamano` | no (default `A6`) | `A4`, `A5` o `A6` |
| `--titulo` | no | Default: `"Reemplazo temporal de personal"` |
| `--salida` | no (default `comunicado.pdf`) | Ruta del PDF a generar |
| `--guardar-html` | no | Si se pasa una ruta, guarda también el HTML ahí |

## Uso como módulo (para integrarlo en otro flujo, ej. desde OpenClaw)

```python
from generar_comunicado import generar_comunicado

ruta = generar_comunicado(
    saliente="Silvina Aguirre",
    entrante="Angela Aquino",
    desde="viernes 2/10",
    salida="salida/comunicado-silvina.pdf",
    tamano="A6",
)
```

`generar_comunicado()` devuelve la ruta (`Path`) del PDF generado. También
acepta `parrafos` (lista de strings HTML, con `<b>` permitido) por si el
comunicado no es un reemplazo de personal sino otro tipo de aviso, y
`guardar_html` para además dejar el HTML final guardado (por ejemplo para
subirlo como Artifact o revisarlo antes de mandarlo).

## Estructura

```
comunicaciones/
├── generar_comunicado.py   # script principal (CLI + función reusable)
├── template.html           # plantilla Jinja2 con la estética de BAE
├── assets/
│   └── logo-bae.png        # isologo real de BAE Limpieza
├── requirements.txt
└── README.md
```

## Notas

- Los tamaños de página (A4/A5/A6) tienen tipografías y espaciados ajustados
  a mano para cada uno — no es solo escalar el mismo diseño.
- El logo se referencia desde `assets/logo-bae.png`, así que el script tiene
  que correrse dentro de esta carpeta (o mantener la estructura relativa).
- Pensado en principio para el aviso de reemplazo temporal de personal de
  BAE Limpieza; si más adelante hace falta una plantilla distinta (otro
  tipo de comunicado, u otra marca del grupo como RPM Vida), conviene
  duplicar `template.html` en vez de forzar el mismo layout.
