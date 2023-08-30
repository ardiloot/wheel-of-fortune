import { createStyles } from "@mantine/core";
import { EffectInfo, SectorState } from "../schemas";
import SvgSector from "./SvgSector";


const EFFECT_COLORS = [
  '#4287f5',
  '#109c10',
  '#ede73b',
  '#de6800',
  '#de0400',
];


const useStyles = createStyles((theme) => ({
  separator: {
    fill: theme.colors.gray[1],
    strokeWidth: 0,
    stroke: theme.colors.dark[3],
  },
}));


export interface SvgWheelProps {
  radius: number;
  wheelAngle: number;
  sectors: Array<SectorState>;
  availableEffects: Record<string, EffectInfo>;
  onSectorClick: (index: number) => void;
}


export default function SvgWheel({
  radius,
  wheelAngle,
  sectors,
  availableEffects,
  onSectorClick,
} : SvgWheelProps) {
  
  const { classes } = useStyles();
  const angularWidth = 2.0 * Math.PI / Math.max(1, sectors.length);

  const sectorItems = sectors.map((sector) => {
    const angle = sector.index * angularWidth;
    const effectIds = Object.keys(availableEffects);
    const effectNumber = effectIds.indexOf(sector.effect_id);
    const effectColor = EFFECT_COLORS[effectNumber]; 
    return (
      <SvgSector
        key={`${sector.index}`}  
        angle={angle}
        angularWidth={angularWidth}
        radius={radius}
        text={sector.name}
        textColor={effectColor}
        onClick={() => onSectorClick(sector.index)}
      />
    );
  });

  const sectorSeparatorItems = sectors.map((sector) => {
    const r = 0.97 * radius
    const angle = (sector.index - 0.5) * angularWidth;
    const p = toXY(r, angle);
    return (
      <circle
        key={sector.index.toString()}
        cx={p.x}
        cy={p.y}
        r={7}
        className={classes.separator}
      ></circle>
    );
  });

  return (
    <g transform={`rotate(${toDeg(wheelAngle).toFixed(3)})`}>
      {sectorItems}
      {sectorSeparatorItems}
    </g>
  );
 
}


function toXY(radius: number, angle: number): {x: number, y: number} {
  // 0 deg = upwards
  // 90 deg = to right
  // ...
  return {
    x: radius * Math.sin(angle),
    y: radius * -Math.cos(angle),
  }
}


function toDeg(radians: number): number {
  return radians * (180 / Math.PI);
}