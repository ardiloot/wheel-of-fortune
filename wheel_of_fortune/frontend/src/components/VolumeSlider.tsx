import { IconVolume2 } from "@tabler/icons-react";
import { Slider, rem } from "@mantine/core";


export default function VolumeSlider({
  volume,
  setVolume,
  setVolumeEnd,
} : {
  volume: number,
  setVolume: (volume: number) => void,
  setVolumeEnd: (volume: number) => void,
}) {
  const volumePercent = Math.round(100 * volume);

  return (
    <Slider
      size={5}
      mt="lg"
      mb="lg"
      thumbChildren={<IconVolume2 size="1.5rem" />}
      value={ volumePercent }
      onChange={ (value) => setVolume(value / 100) }
      onChangeEnd={ (value) => setVolumeEnd(value / 100) }
      thumbSize={25}
      styles={(_) => ({
        thumb: {
          borderWidth: rem(1),
        },
      })}
    />
  )
}