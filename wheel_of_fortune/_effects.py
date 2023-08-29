import yaml
import logging
import mergedeep
from .schemas import EffectInfo


_LOGGER = logging.getLogger(__name__)

__all__ = [
    "Effect",
    "load_effects",
]


class Effect:

    def __init__(self, _id,
        name="Example effect",
        description="Example effect description",
        based_on=[],
        effect_sound="example_effect",
        leds_preset={}
    ):
        self._id: str = _id
        self.name: str = name
        self.description: str = description
        self.based_on: list[str] = based_on
        self.effect_sound: str = effect_sound
        self.leds_preset = leds_preset
    
    @staticmethod
    def from_dict(effect_id, params):
        params.pop("visible", None)
        # TODO: params validation
        return Effect(effect_id, **params)

    def get_info(self) -> EffectInfo:
        return EffectInfo(
            id=self._id,
            name=self.name,
            description=self.description,
            based_on=self.based_on,
            effect_sound=self.effect_sound,
        )


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
        res[effect_id] = Effect.from_dict(effect_id, params)
    return res
