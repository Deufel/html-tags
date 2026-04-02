from urllib.parse import quote
from .tag import Tag, Safe, Fragment, mktag

"""Convenience constructors for common dependencies and page head."""

# ── dependency scripts ───────────────────────────────────────────────

def Datastar(v='1.0.0-RC.8'):
    """Datastar client library script tag."""
    return Tag('script', (), {
        'type': 'module',
        'src': f'https://cdn.jsdelivr.net/gh/starfederation/datastar@{v}/bundles/datastar.js'})

def ScopedCSS():
    """css-scope-inline script tag."""
    return Tag('script', (), {
        'src': 'https://cdn.jsdelivr.net/gh/gnat/css-scope-inline@main/script.js'})

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

# ── page head ────────────────────────────────────────────────────────

def Head(title='', description='', url='', image='',
         favicon='', site_name='', twitter_card='summary_large_image',
         twitter_site='', theme_color='', csp=None, datastar=False,
         scoped_css=False, extra_head=None):
    """Complete <head> contents as a Fragment.

    Returns the inner contents — wrap in html(head(Head(...)), body(...))
    """
    tags = [
        Tag('meta', (), {'charset': 'utf-8'}),
        Tag('meta', (), {'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}),
    ]
    if title:       tags.append(Tag('title', (title,), {}))
    if favicon:     tags.append(Favicon(favicon))
    if theme_color: tags.append(Tag('meta', (), {'name': 'theme-color', 'content': theme_color}))
    if title or description or url or image:
        tags.append(Social(
            title=title, description=description, url=url, image=image,
            site_name=site_name, twitter_card=twitter_card,
            twitter_site=twitter_site))
    if csp is True:  tags.append(CSP(datastar=datastar))
    elif csp:        tags.append(csp)
    if datastar:     tags.append(Datastar())
    if scoped_css:   tags.append(ScopedCSS())
    if extra_head:   tags.append(extra_head)
    return Fragment(*tags)
