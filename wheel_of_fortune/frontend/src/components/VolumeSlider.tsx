import { IconVolume2 } from '@tabler/icons-react';
import { Slider, rem } from '@mantine/core';
import { useCallback, useState } from 'react';
import { throttle } from 'lodash';

export interface VolumeSliderProps {
  channelName: string;
  volume: number;
  setVolume: (volume: number) => void;
  setVolumeEnd: (volume: number) => void;
}

export default function VolumeSlider({ channelName, volume, setVolume, setVolumeEnd }: VolumeSliderProps) {
  const [latestValue, setLatestValue] = useState<number>(0);
  const [active, setActive] = useState<boolean>(false);
  const throttledSetVolume = useCallback(throttle(setVolumeEnd, 1000), []);

  const volumePercent = active ? latestValue : Math.round(100 * volume);
  
  return (
    <Slider
      size={5}
      mt="lg"
      mb="lg"
      label={(value) => `${channelName} ${value}%`}
      thumbChildren={<IconVolume2 size="1.5rem" />}
      value={volumePercent}
      onChange={(value) => {
        setLatestValue(value);
        setActive(true);
        setVolume(value / 100);
        throttledSetVolume(value / 100);
      }}
      onChangeEnd={(value) => {
        setLatestValue(value);
        setActive(false);
        setVolumeEnd(value / 100);
      }}
      thumbSize={25}
      styles={{
        thumb: {
          borderWidth: rem(1),
        },
      }}
    />
  );
}
