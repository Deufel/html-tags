from .core import to_html

def patch_elements(elements, selector=None, mode=None, namespace=None, use_view_transition=None):
    "Format a datastar-patch-elements SSE event"
    if hasattr(elements, 'tag'): elements = to_html(elements)
    lines = []
    if selector: lines.append(f'data: selector {selector}')
    if mode: lines.append(f'data: mode {mode}')
    if namespace: lines.append(f'data: namespace {namespace}')
    if use_view_transition is not None: lines.append(f'data: useViewTransition {str(use_view_transition).lower()}')
    for line in elements.split('\n'): lines.append(f'data: elements {line}')
    return 'event: datastar-patch-elements\n' + '\n'.join(lines) + '\n\n'

def patch_signals(signals, only_if_missing=None):
    "Format a datastar-patch-signals SSE event"
    lines = []
    if only_if_missing is not None: lines.append(f'data: onlyIfMissing {str(only_if_missing).lower()}')
    lines.append(f'data: signals {signals}')
    return 'event: datastar-patch-signals\n' + '\n'.join(lines) + '\n\n'

def datastar_stream(events):
    "Return (headers, generator) for a datastar SSE response"
    return dict(Content_Type='text/event-stream', Cache_Control='no-cache', X_Accel_Buffering='no'), (e for e in events)
