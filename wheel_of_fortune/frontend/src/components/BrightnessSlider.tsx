import { useRef } from "react";
import { throttle } from 'lodash';
import { IconSun } from "@tabler/icons-react";
import { Slider, rem } from "@mantine/core";


export default function BrightnessSlider({ ws, ledsState, setLedsState } : {ws: any, ledsState: any, setLedsState: any}) {
  const brightnessPercent = ledsState !== null ? Math.round(100 * ledsState.brightness) : 0;

  const apiSetBrightness = useRef(
    throttle(async (ws, brightness : number) => {
      ws.send(JSON.stringify({
        cmd: 'set_leds',
        data: {
          brightness: brightness,
        }
      }))
    }, 250)
  ).current;

  function handleBrightnessChange(value : number) {
    if (value === brightnessPercent)
      return;
    setLedsState({
      ...ledsState,
      brightness: value / 100.0
    })
    apiSetBrightness(ws, value / 100.0);
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