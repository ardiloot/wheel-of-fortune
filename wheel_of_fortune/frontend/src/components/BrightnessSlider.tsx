
import { IconSun } from "@tabler/icons-react";
import { Slider, rem } from "@mantine/core";


export interface BrightnessSliderProps{
  brightness: number;
  setBrightness: (brightness: number) => void;
  setBrightnessEnd: (brightness: number) => void;
}


export default function BrightnessSlider({
  brightness,
  setBrightness,
  setBrightnessEnd,
} : BrightnessSliderProps) {
  const brightnessPercent = Math.round(100 * brightness);

  return (
    <Slider
    size={5}
    mt="lg"
    mb="lg"
    thumbChildren={<IconSun size="1.5rem" />}
    value={ brightnessPercent }
    onChange={(value) => setBrightness(value / 100)}
    onChangeEnd={(value) => setBrightnessEnd(value / 100)}
    thumbSize={25}
    styles={{
      thumb: {
        borderWidth: rem(1),
      },
    }}
  />
  )
}