import { IconVolume2 } from "@tabler/icons-react";
import { Slider, rem } from "@mantine/core";
import ThrottledSlider from "./ThrottledSlider";


export default function VolumeSlider({
  volume,
  setVolume,
} : {
  volume: number,
  setVolume: (volume: number) => void
}) {
  const volumePercent = Math.round(100 * volume);

  return (
    <ThrottledSlider
      size={5}
      mt="lg"
      mb="lg"
      thumbChildren={<IconVolume2 size="1.5rem" />}
      initialValue={ volumePercent }
      onChangeThrottled={(value) => {
        console.log("set volume throttled", value);
        if (value === volumePercent)
          return;
        setVolume(value / 100.0);
      }}
      thumbSize={25}
      styles={(_) => ({
        thumb: {
          borderWidth: rem(1),
        },
      })}
    />
  )
}