# Kovu Run

Endless runner 2.5D: Kovu el galgo corre y una viejita con cardigan malva lo persigue. Saltá a los vagones para correr un tramo elevado, juntá galletas y mejoras locales.

## Requisitos

- Windows 10/11
- Python 3.11+ (solo si corrés desde código)
- `pygame` (`py -m pip install -r requirements.txt`)

## Correr desde código

```bash
py -m pip install -r requirements.txt
py main.py
```

## Build instalable (.exe)

```bash
py -m pip install pyinstaller
py tools/build.py
```

Queda en `dist/KovuRun/KovuRun.exe`. Podés copiar **toda** la carpeta `dist/KovuRun/` a otra PC y ejecutar el `.exe` (no hace falta Python).

Los saves van en `data/` al lado del ejecutable (`accounts.json`, ranking, opciones).

## Controles

| Teclado | Acción |
|--------|--------|
| ← → / A D | Carril |
| ↑ W / Espacio | Saltar (también para subir a un vagón) |
| ↓ S | Agacharse |
| Clic | Menú, tienda, cuentas, opciones |
| F11 | Pantalla completa |
| Esc | Volver / salir |

Arranca en **pantalla completa** (se puede apagar en Opciones). Hay **música en loop** y SFX (salto, galleta, crash, menú, etc.); el volumen se ajusta en Opciones.

Los WAV se regeneran con:

```bash
py -m tools.forge
```

## Licencia

Proyecto personal / demo.
