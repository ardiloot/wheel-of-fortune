
import { IconSun } from "@tabler/icons-react";
import { Slider, rem } from "@mantine/core";


export default function BrightnessSlider({
  brightness,
  setBrightness,
} : {
  brightness: number,
  setBrightness: (brightness: number) => void
}) {
  const brightnessPercent = Math.round(100 * brightness);
  function handleBrightnessChange(value : number) {
    if (value === brightnessPercent)
      return;
    setBrightness(value / 100.0);
  }

  return (
    <Slider
    size={5}
    mt="lg"
    mb="lg"
    thumbChildren={<IconSun size="1.5rem" />}
    value={ brightnessPercent }
    onChange={handleBrightnessChange}
    thumbSize={25}
    styles={(_) => ({
      thumb: {
        borderWidth: rem(1),
      },
    })}
  />
  )
}