from gi.repository import Graphene, Gtk


def closeOnClickOutside(dialog):
    # Adw.Dialog only closes via Escape or its close button; also close
    # it when clicking the backdrop around the dialog
    click = Gtk.GestureClick()
    click.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)

    def pressed(gesture, clicks, x, y):
        child = dialog.get_child()
        if child is None:
            return
        ok, bounds = child.compute_bounds(dialog)
        if ok and not bounds.contains_point(Graphene.Point().init(x, y)):
            dialog.close()

    click.connect("pressed", pressed)
    dialog.add_controller(click)
