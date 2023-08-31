import yaml
import logging
import mergedeep
from .schemas import ThemeInfo

_LOGGER = logging.getLogger(__name__)

__all__ = [
    "Theme",
    "load_themes",
]


class Theme(ThemeInfo):
    def get_info(self) -> ThemeInfo:
        return self


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
        res[theme_id] = Theme.model_validate(params)
    return res
