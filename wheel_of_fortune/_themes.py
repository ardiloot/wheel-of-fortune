import yaml
import logging
import mergedeep
from .schemas import ThemeState

_LOGGER = logging.getLogger(__name__)

__all__ = [
    "Theme",
    "load_themes",
]


class Theme:

    def __init__(self, _id,
        name="Example theme",
        description="Example theme description",
        based_on=[],
        theme_sound="example_theme",
        startup_led_preset={},
        idle_led_preset={},
        spinning_led_preset={},
        poweroff_led_preset={},
    ):
        self._id: str = _id
        self.name: str = name
        self.description: str = description
        self.based_on: list[str] = based_on
        self.theme_sound: str = theme_sound
        self.startup_led_preset = startup_led_preset
        self.idle_led_preset = idle_led_preset
        self.spinning_led_preset = spinning_led_preset
        self.poweroff_led_preset = poweroff_led_preset

    @staticmethod
    def from_dict(theme_id, params):
        params.pop("visible", None)
        # TODO: params validation
        return Theme(theme_id, **params)

    def get_state(self) -> ThemeState:
        return ThemeState(
            id=self._id,
            name=self.name,
            description=self.description,
            based_on=self.based_on,
            theme_sound=self.theme_sound,
        )


def load_themes(filename: str):

    _LOGGER.info("load themes: %s" % (filename))

    def merge(base, addition):
        res = mergedeep.merge({}, base, addition)
        res["based_on"] = base.get("based_on", []) + addition.get("based_on", [])
        res["visible"] = addition.get("visible", True)
        return res

    def compile(_id):
        theme = themes[_id]
        if "based_on" in theme:
            res = {}
            for base_id in theme["based_on"]:
                base_theme = compile(base_id)
                res = merge(base_theme, theme)
            return res
        else:
            return theme
    
    try:
        with open(filename, "r") as fin:
            themes = yaml.safe_load(fin)
    except Exception as e:
        raise RuntimeError("Error on loading %s file" % (filename)) from e

    res = {}
    for theme_id, theme in themes.items():
        if not theme.get("visible", True):
            continue
        params = compile(theme_id)
        res[theme_id] = Theme.from_dict(theme_id, params)
    return res
