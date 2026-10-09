"""Deja las fotos de producto con fondo blanco parejo.

Algunas fotos del proveedor vienen con fondo gris claro o transparente y en la
grilla desentonan. Para esas, se reemplaza el fondo (la zona conectada al borde y
los agujeros de la paleta) por blanco y se guarda una copia en _site/img/.
Las fotos que ya tienen fondo blanco no se tocan y se sigue usando la original.
"""
import io

import numpy as np
from PIL import Image
from scipy import ndimage

TOLERANCIA = 14      # diferencia máxima con el color de fondo
BLANCO_OK = 246      # borde con este brillo o más ya cuenta como blanco
LADO_MAX = 900       # las copias se achican a este tamaño como máximo


def _borde(a: np.ndarray) -> np.ndarray:
    return np.concatenate([a[:2].reshape(-1, a.shape[-1]), a[-2:].reshape(-1, a.shape[-1]),
                           a[:, :2].reshape(-1, a.shape[-1]), a[:, -2:].reshape(-1, a.shape[-1])])


def limpiar(datos: bytes) -> bytes | None:
    """Devuelve la foto corregida (webp) o None si no hace falta tocarla."""
    im = Image.open(io.BytesIO(datos))
    im.load()
    tenia_transparencia = False
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        alfa = np.asarray(im)[..., 3]
        if (_borde(alfa[..., None]) < 250).mean() > 0.05:
            tenia_transparencia = True
        fondo = Image.new("RGBA", im.size, (255, 255, 255, 255))
        im = Image.alpha_composite(fondo, im)
    im = im.convert("RGB")
    if max(im.size) > LADO_MAX:
        im.thumbnail((LADO_MAX, LADO_MAX), Image.LANCZOS)
    a = np.asarray(im).astype(np.int16)
    borde = _borde(a)

    if borde.min(axis=1).mean() >= BLANCO_OK and (borde.min(axis=1) >= BLANCO_OK - 10).mean() > 0.97:
        return _webp(im) if tenia_transparencia else None
    color = np.median(borde, axis=0)
    cerca_borde = (np.abs(borde - color).max(axis=1) <= TOLERANCIA).mean()
    if cerca_borde < 0.9:
        return None  # el fondo no es parejo (foto ambientada): mejor no tocarla

    parecido = np.abs(a - color).max(axis=2) <= TOLERANCIA
    etiquetas, n = ndimage.label(parecido)
    tocan_borde = set(np.unique(np.concatenate([etiquetas[0], etiquetas[-1], etiquetas[:, 0], etiquetas[:, -1]])))
    tamanos = ndimage.sum(parecido, etiquetas, index=np.arange(n + 1))
    total = parecido.size
    fondo = np.zeros(n + 1, dtype=bool)
    for k in range(1, n + 1):
        if k in tocan_borde or 20 <= tamanos[k] <= 0.03 * total:
            fondo[k] = True
    mascara = fondo[etiquetas]
    # suaviza el borde: un pixel de transición alrededor del fondo
    mascara = ndimage.binary_dilation(mascara, iterations=1) & (np.abs(a - color).max(axis=2) <= TOLERANCIA * 2)
    mascara |= fondo[etiquetas]
    salida = np.asarray(im).copy()
    salida[mascara] = 255
    return _webp(Image.fromarray(salida))


def _webp(im: Image.Image) -> bytes:
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=86, method=4)
    return buf.getvalue()
