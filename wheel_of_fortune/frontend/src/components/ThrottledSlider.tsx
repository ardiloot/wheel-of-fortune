import { Slider, SliderProps } from "@mantine/core";
import { useRef, useState } from "react";
import { throttle } from "lodash";


export interface ThrottledSliderProps extends SliderProps {
  initialValue: number;
  onChangeThrottled: (value: number) => void;
}


export default function ThrottledSlider({
  initialValue,
  onChangeThrottled,
  ...props
} : ThrottledSliderProps) {
  const [value, setValue] = useState<number>(initialValue);
  
  const setValueThrottled = useRef(
    throttle((value : number) => {
      onChangeThrottled(value);
    }, 250)
  ).current;

  return (
    <Slider
      value={value}
      onChange={ (value) => {
        console.log("set volume", value);
        setValue(value);
        setValueThrottled(value);
      }}
      {...props}
    />
  )
}