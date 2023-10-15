import { IconSun } from '@tabler/icons-react';
import { Slider, rem } from '@mantine/core';
import { useCallback, useState } from 'react';
import { throttle } from 'lodash';

export interface BrightnessSliderProps {
  brightness: number;
  setBrightness: (brightness: number) => void;
  setBrightnessThrottled: (brightness: number) => void;
}

export default function BrightnessSlider({ brightness, setBrightness, setBrightnessThrottled }: BrightnessSliderProps) {
  const [latestValue, setLatestValue] = useState<number>(0);
  const [active, setActive] = useState<boolean>(false);
  const throttledCb = useCallback(throttle(setBrightnessThrottled, 200), []);

  function setValue(value: number, active: boolean) {
    setLatestValue(value);
    setActive(active);
    setBrightness(value / 100);
    throttledCb(value / 100);
  }

  return (
    <Slider
      size={5}
      mt="lg"
      mb="lg"
      thumbChildren={<IconSun size="1.5rem" />}
      value={active ? latestValue : Math.round(100 * brightness)}
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
