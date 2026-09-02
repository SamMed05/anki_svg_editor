from anki.hooks import addHook


def load_addon():
    from . import editor_button  # noqa: F401


addHook("profileLoaded", load_addon)
