import { IconVolume2 } from "@tabler/icons-react";
import { Slider, rem } from "@mantine/core";


export default function VolumeSlider({
  volume,
  setVolume,
} : {
  volume: number,
  setVolume: (volume: number) => void
}) {
  const volumePercent = Math.round(100 * volume);

  function handleVolumeChange(value : number) {
    if (value === volumePercent)
      return;
    setVolume(value / 100.0);
  }

  return (
    <Slider
    size={5}
    mt="lg"
    mb="lg"
    thumbChildren={<IconVolume2 size="1.5rem" />}
    value={ volumePercent }
    onChange={handleVolumeChange}
    thumbSize={25}
    styles={(_) => ({
      thumb: {
        borderWidth: rem(1),
      },
    })}
  />
  )
}