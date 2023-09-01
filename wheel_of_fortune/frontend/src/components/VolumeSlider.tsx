import { IconVolume2 } from '@tabler/icons-react';
import { Slider, rem } from '@mantine/core';

export interface VolumeSliderProps {
  channelName: string;
  volume: number;
  setVolume: (volume: number) => void;
  setVolumeEnd: (volume: number) => void;
}

export default function VolumeSlider({ channelName, volume, setVolume, setVolumeEnd }: VolumeSliderProps) {
  const volumePercent = Math.round(100 * volume);

  return (
    <Slider
      size={5}
      mt="lg"
      mb="lg"
      label={(value) => `${channelName} ${value}%`}
      thumbChildren={<IconVolume2 size="1.5rem" />}
      value={volumePercent}
      onChange={(value) => setVolume(value / 100)}
      onChangeEnd={(value) => setVolumeEnd(value / 100)}
      thumbSize={25}
      styles={{
        thumb: {
          borderWidth: rem(1),
        },
      }}
    />
  );
}
