import { useMantineTheme } from '@mantine/core';
import { EffectInfo, SectorState } from '../schemas';
import SvgSector from './SvgSector';
import { toDeg, toXY } from '../utils';

export interface SvgWheelProps {
  radius: number;
  wheelAngle: number;
  sectors: Array<SectorState>;
  availableEffects: Record<string, EffectInfo>;
  onSectorClick: (index: number) => void;
}

export default function SvgWheel({ radius, wheelAngle, sectors, availableEffects, onSectorClick }: SvgWheelProps) {
  const theme = useMantineTheme();
  const angularWidth = (2.0 * Math.PI) / Math.max(1, sectors.length);

  const sectorItems = sectors.map((sector) => {
    const angle = sector.index * angularWidth;
    const effect = availableEffects[sector.effect_id];
    return (
      <SvgSector
        key={`${sector.index}`}
        angle={angle}
        angularWidth={angularWidth}
        radius={radius}
        text={sector.name}
        textColor={effect?.color || '#00FFFF'}
        onClick={() => onSectorClick(sector.index)}
      />
    );
  });

  const sectorSeparatorItems = sectors.map((sector) => {
    const r = 0.97 * radius;
    const angle = (sector.index - 0.5) * angularWidth;
    const p = toXY(r, angle);
    return (
      <circle
        key={sector.index.toString()}
        cx={p.x}
        cy={p.y}
        r={7}
        fill={theme.colors.gray[1]}
        strokeWidth={0}
        stroke={theme.colors.dark[3]}
      ></circle>
    );
  });

  return (
    <g transform={`rotate(${toDeg(-wheelAngle).toFixed(3)})`}>
      {sectorItems}
      {sectorSeparatorItems}
    </g>
  );
}
