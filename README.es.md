# Media Distribution

[English](README.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [Español](README.es.md)

## Publicación multilingüe de proyectos de diseño

Prepara imágenes con texto y vídeos para redes sociales y envía proyectos a publicaciones de diseño. Adapta el texto por idioma, revisa cada destino y conserva comprobantes de entrega.

Copia SKILL.md, scripts/, references/ y examples/ juntos en una carpeta media-distribution dentro del directorio de habilidades de tu agente. Requiere Python 3.12+ en Linux/macOS. La preparación y SMTP usan la biblioteca estándar. YouTube necesita los clientes opcionales de Google y credenciales OAuth autorizadas; consulta la [configuración](references/setup.md).

YouTube y los envíos SMTP incluyen adaptadores ejecutables. Instagram, Xiaohongshu, Bilibili y los formularios editoriales dependen del navegador del agente y de una sesión iniciada. Si faltan requisitos, el resultado es blocked. No se han probado cuentas reales ni verificado las interfaces actuales.

Sustituye la imagen de ejemplo por tu material. Añade títulos y textos en localizations y asigna un idioma a cada destino. Los permisos automáticos abarcan ID de contenido, cuenta y canal, y persisten entre revisiones; revócalos al terminar. Reutiliza el mismo artefacto y directorio de estado al reintentar. Si la entrega es incierta, comprueba registros externos antes de repetirla. submitted no significa aceptación editorial. No se admiten archivos de subtítulos separados ni publicaciones programadas.

```bash
python3 scripts/media_distribution.py validate examples/image-package.json
python3 scripts/media_distribution.py prepare examples/image-package.json --output prepared
# Use the artifact path returned above.
python3 scripts/media_distribution.py --state-dir .distribution-state preview prepared/package-REPLACE/artifact.json
# Only after explicit approval:
python3 scripts/media_distribution.py --state-dir .distribution-state approve prepared/package-REPLACE/artifact.json
python3 scripts/media_distribution.py --state-dir .distribution-state execute prepared/package-REPLACE/artifact.json --send
python3 scripts/media_distribution.py --state-dir .distribution-state status
```

[Skill](SKILL.md) · [Content format](references/content-format.md) · [Authorization and recovery](references/authorization.md) · [Channels](references/channels.md)

```bash
python3 -m unittest discover -s tests -v
```
