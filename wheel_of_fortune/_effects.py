import yaml
import logging
import mergedeep
from .schemas import EffectInfo


_LOGGER = logging.getLogger(__name__)

__all__ = [
    "Effect",
    "load_effects",
]


class Effect(EffectInfo):

    def get_info(self) -> EffectInfo:
        return self


def load_effects(filename: str):
    _LOGGER.info("load effects: %s" % (filename))

    def merge(base, addition): 
        res = mergedeep.merge({}, base, addition)
        res["based_on"] = base.get("based_on", []) + addition.get("based_on", [])
        res["visible"] = addition.get("visible", True)
        return res

    def compile(effect_id):
        effect = effects[effect_id]
        if "based_on" in effect:
            res = {}
            for base_id in effect["based_on"]:
                base_effect = compile(base_id)
                res = merge(base_effect, effect)
            return res
        else:
            return effect
    
    try:
        with open(filename, "r") as fin:
            effects = yaml.safe_load(fin)
    except Exception as e:
        raise RuntimeError("Error on loading %s file" % (filename)) from e

    res = {}
    for effect_id, effect in effects.items():
        if not effect.get("visible", True):
            continue
        params = compile(effect_id)
        res[effect_id] = Effect.model_validate(params)
    return res
