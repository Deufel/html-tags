from urllib.parse import quote
from .tag import Tag, Safe, Fragment, mktag

"""Convenience constructors for common dependencies"""

# ── dependency scripts ───────────────────────────────────────────────

def Datastar(v='1.0.0-RC.8'):
    """Datastar client library script tag."""
    return Tag('script', (), {
        'type': 'module',
        'src': f'https://cdn.jsdelivr.net/gh/starfederation/datastar@{v}/bundles/datastar.js'})

def MeCSS(v='v1.0.1'):
    return Tag('script', (), {
        'src': f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/me_css.js'
    })

def Pointer(v='v1.0.1'):
    return Tag('script', (), {
        'src': f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/pointer_events.js'
    })

def ScopedCSS():
    """the original css-scope-inline script tag."""
    return Tag('script', (), {
        'src': 'https://cdn.jsdelivr.net/gh/gnat/css-scope-inline@main/script.js'})

def FontImport(url="https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap"):
    """helper for font link imports MUST be used in head (defaults to jet brains mono)"""
    return Tag('link')(rel="stylesheet", href=url)

# ── emoji favicon ────────────────────────────────────────────────────

def Favicon(emoji):
    """Emoji favicon as an SVG data URI. Favicon("🔥")"""
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
           f'<text y=".9em" font-size="90">{emoji}</text></svg>')
    uri = 'data:image/svg+xml,' + quote(svg, safe=':/@!,')
    return Tag('link', (), {'rel': 'icon', 'href': uri})

# ── content security policy ──────────────────────────────────────────

def CSP(default_src="'self'",
        script_src=None,
        style_src=None,
        img_src=None,
        connect_src=None,
        font_src=None,
        frame_ancestors="'none'",
        datastar=False,
        extra=''):
    """CSP meta tag. Set datastar=True to add jsdelivr + unsafe-eval."""
    ds_script  = " 'unsafe-eval' https://cdn.jsdelivr.net" if datastar else ''
    ds_connect = " https://cdn.jsdelivr.net" if datastar else ''
    parts = [f"default-src {default_src}"]
    parts.append(f"script-src {script_src or default_src}{ds_script}")
    parts.append(f"style-src {style_src or default_src} 'unsafe-inline'")
    parts.append(f"img-src {img_src or default_src} data:")
    parts.append(f"connect-src {connect_src or default_src}{ds_connect}")
    if font_src:       parts.append(f"font-src {font_src}")
    if frame_ancestors: parts.append(f"frame-ancestors {frame_ancestors}")
    parts.append("object-src 'none'")
    parts.append("base-uri 'self'")
    if extra: parts.append(extra)
    policy = '; '.join(parts)
    return Tag('meta', (), {'http-equiv': 'Content-Security-Policy', 'content': policy})

# ── social / open graph meta ─────────────────────────────────────────

def Social(title, description='', url='', image='', site_name='',
           twitter_card='summary_large_image', twitter_site=''):
    """Open Graph + Twitter Card meta tags for link previews."""
    tags = []
    if description: tags.append(Tag('meta', (), {'name': 'description', 'content': description}))
    tags.append(Tag('meta', (), {'property': 'og:title', 'content': title}))
    if description: tags.append(Tag('meta', (), {'property': 'og:description', 'content': description}))
    if url:         tags.append(Tag('meta', (), {'property': 'og:url', 'content': url}))
    if image:       tags.append(Tag('meta', (), {'property': 'og:image', 'content': image}))
    if site_name:   tags.append(Tag('meta', (), {'property': 'og:site_name', 'content': site_name}))
    tags.append(Tag('meta', (), {'property': 'og:type', 'content': 'website'}))
    tags.append(Tag('meta', (), {'name': 'twitter:card', 'content': twitter_card}))
    tags.append(Tag('meta', (), {'name': 'twitter:title', 'content': title}))
    if description: tags.append(Tag('meta', (), {'name': 'twitter:description', 'content': description}))
    if image:       tags.append(Tag('meta', (), {'name': 'twitter:image', 'content': image}))
    if twitter_site: tags.append(Tag('meta', (), {'name': 'twitter:site', 'content': twitter_site}))
    return Fragment(*tags)
