import { throttle } from 'lodash';
import { IconVolume2 } from "@tabler/icons-react";
import { Slider, rem } from "@mantine/core";
import { useRef } from 'react';


export default function VolumeSlider({ ws, soundState, setSoundState } : {ws: any, soundState: any, setSoundState: any}) {
  const volumePercent = soundState !== null ? Math.round(100 * soundState.volume) : 0;

  const apiSetVolume = useRef(
    throttle(async (ws, volume : number) => {
      console.log('api set volume', volume);
      ws.send(JSON.stringify({
        cmd: 'set_sound',
        data: {
          volume: volume,
        }
      }))
    }, 250)
  ).current;

  function handleVolumeChange(value : number) {
    if (value === volumePercent) {
      return;
    }
    setSoundState({
      ...soundState,
      volume: value / 100.0
    })
    apiSetVolume(ws, value / 100.0);
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