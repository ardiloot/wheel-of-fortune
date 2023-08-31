import { MantineColor } from '@mantine/core';

export interface SvgLedGlowProps {
  id: string;
  radius: number;
  stops: Array<{ offset: string; color: MantineColor; opacity: number }>;
}

export default function SvgLedGlow({ id, radius, stops }: SvgLedGlowProps) {
  return (
    <>
      <defs>
        <radialGradient id={id}>
          {stops.map((s) => (
            <stop key={s.offset} offset={s.offset} stopColor={s.color} stopOpacity={s.opacity} />
          ))}
        </radialGradient>
      </defs>
      <circle cx="0" cy="0" r={radius} fill={`url('#${id}')`} stroke="none" />
    </>
  );
}
