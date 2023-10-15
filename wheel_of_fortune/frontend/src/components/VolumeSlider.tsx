import { IconVolume2 } from '@tabler/icons-react';
import { Slider, rem } from '@mantine/core';
import { useCallback, useState } from 'react';
import { throttle } from 'lodash';

export interface VolumeSliderProps {
  channelName: string;
  volume: number;
  setVolume: (volume: number) => void;
  setVolumeThrottled: (volume: number) => void;
}

export default function VolumeSlider({ channelName, volume, setVolume, setVolumeThrottled }: VolumeSliderProps) {
  const [latestValue, setLatestValue] = useState<number>(0);
  const [active, setActive] = useState<boolean>(false);
  const throttledCb = useCallback(throttle(setVolumeThrottled, 200), []);

  function setValue(value: number, active: boolean) {
    setLatestValue(value);
    setActive(active);
    setVolume(value / 100);
    throttledCb(value / 100);
  }

  return (
    <Slider
      size={5}
      mt="lg"
      mb="lg"
      label={(value) => `${channelName} ${value}%`}
      thumbChildren={<IconVolume2 size="1.5rem" />}
      value={active ? latestValue : Math.round(100 * volume)}
      onChange={(value) => setValue(value, true)}
      onChangeEnd={(value) => setValue(value, false)}
      thumbSize={25}
      styles={{
        thumb: {
          borderWidth: rem(1),
        },
      }}
    />
  );
}
