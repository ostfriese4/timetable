from gi.repository import Gdk, Gtk

_provider = Gtk.CssProvider()
_registered = False
_classes = {}


def serverColorClass(color):
    # returns a css class with the given background color (e.g. "#f8d4f1"),
    # generating the style on first use
    global _registered
    hexcolor = color.lstrip("#").lower()
    name = "wu-" + hexcolor

    if name not in _classes:
        _classes[name] = ".%s { background: #%s; }" % (name, hexcolor)
        _provider.load_from_string("\n".join(_classes.values()))
        if not _registered:
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                _provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )
            _registered = True

    return name
