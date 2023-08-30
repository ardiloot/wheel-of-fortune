import { createStyles } from "@mantine/core";
import { useState } from "react";
import SectorEditModal from "./SectorEditModal";
import { EffectInfo, EncoderState, SectorState } from "../schemas";


const useStyles = createStyles((theme) => ({
  sector: {
    stroke: theme.colors.gray[0],
    fill: theme.colors.dark[6],
    strokeWidth: 1,
    '&:hover': {
      fill: theme.colors.dark[2],
    },
  },
  text: {
    fontSize: "35px",
    alignmentBaseline: "middle",
    pointerEvents: "none",
    fontFamily: "Verdana, sans-serif",
  },
  separator: {
    fill: theme.colors.gray[1],
    strokeWidth: 0,
    stroke: theme.colors.dark[3],
  },
  flipper: {
    fill: theme.colors.dark[5],
    strokeWidth: 2,
    stroke: theme.colors.gray[5],
  },
}));


const EFFECT_COLORS = [
  '#4287f5',
  '#109c10',
  '#ede73b',
  '#de6800',
  '#de0400',
];


function toDeg(radians: number) {
  return radians * (180 / Math.PI);
}


function toXY(radius: number, angle: number) {
  // 0 deg = upwards
  // 90 deg = to right
  // ...
  return {
    x: radius * Math.sin(angle),
    y: radius * -Math.cos(angle),
  }
}


export interface WheelProps {
  sectors: Array<SectorState>;
  availableEffects: Record<string, EffectInfo>;
  encoderState: EncoderState;
  updateSector: (index: number, name: string, effectId: string) => void;
}


export default function Wheel({
  sectors,
  availableEffects,
  encoderState,
  updateSector,
} : WheelProps) {

  const [editSectorIndex, setEditSectorIndex] = useState<number | null>(null);  
  const { classes } = useStyles();
  const activeSector = encoderState.sector;

  function handleSectorEdit(index: number, name: string, effectId: string) {
    console.log('save: ' + index + ' ' + name + ' ' + effectId);
    setEditSectorIndex(null);
    updateSector(index, name, effectId);
  }

  const wheelRadius = 400.0;
  const sectorAngularWidth = 2.0 * Math.PI / sectors.length;
  const curWheelAngle = sectorAngularWidth * activeSector;

  const sectorPathItems = sectors.map((sector) => {
    function handleSectorClick() {
      console.log('clicked:' + sector.index)
      setEditSectorIndex(sector.index);
    }

    const angle = sector.index * 2.0 * Math.PI / sectors.length - curWheelAngle;
    const p0 = toXY(wheelRadius, angle - 0.5 * sectorAngularWidth);
    const p1 = toXY(wheelRadius, angle + 0.5 * sectorAngularWidth);
    const d = 'M 0 0 L ' +
      p0.x.toFixed(3) + ' ' + p0.y.toFixed(3) + ' ' +
      'A 400 400 0 0 1 ' +
      p1.x.toFixed(3) + ' ' + p1.y.toFixed(3) + ' ' +
      'Z';

    return (
      <path
        key={"sector_" + sector.index.toString()}
        d={d}
        className={classes.sector}
        onClick={handleSectorClick}
      />
    );
  });

  const sectorNameItems = sectors.map((sector) => {
    const textRadius = 0.95 * wheelRadius
    const angle = sector.index * 2.0 * Math.PI / sectors.length - curWheelAngle;
    const p = toXY(textRadius, angle);
    const transform =
      'translate(' + p.x.toFixed(3) + ', ' + p.y.toFixed(3) + ') ' +
      'rotate(' + toDeg(angle  + Math.PI / 2).toFixed(3) + ')';
      const effectIds = Object.keys(availableEffects);
      const effectNumber = effectIds.indexOf(sector.effect_id);
      const effectColor = EFFECT_COLORS[effectNumber]; 

    return (
      <text
        key={sector.index.toString()}
        x={0.0}
        y={0.0}
        className={classes.text}
        fill={effectColor}
        transform={transform}
        opacity={0.8}
      >
        {sector.name}
      </text>
    );
  });

  const sectorSeparatorItems = sectors.map((sector) => {
    const radius = 0.97 * wheelRadius
    const angle = sector.index * 2.0 * Math.PI / sectors.length - curWheelAngle - 0.5 * sectorAngularWidth;
    const p = toXY(radius, angle);
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
    <>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="-500 -500 1000 1000"
      >
        <defs>
          <radialGradient id="background_gradient">
            <stop offset="80%" stopColor="blue" stopOpacity="0.3"/>
            <stop offset="100%" stopColor="blue" stopOpacity="0.0"/>
          </radialGradient>
          <radialGradient id="wheel_gradient">
            <stop offset="50%" stopColor="orange" stopOpacity="0.2"/>
            <stop offset="100%" stopColor="orange" stopOpacity="0.0"/>
          </radialGradient>
          <radialGradient id="logo_gradient">
            <stop offset="0%" stopColor="red" stopOpacity="0.8"/>
            <stop offset="100%" stopColor="blue" stopOpacity="0.8"/>
          </radialGradient>
          <mask id="logo">
            <circle fill="white" cx={0} cy={0} r={500}/>
            <text
              x="0"
              y="0"
              fontSize="45"
              fill="black"
              textAnchor="middle"
              alignmentBaseline="middle"
              fontWeight="bold"
            >
              -LOGO-
            </text>
          </mask>
        </defs>

        {/* Background leds */}
        <circle cx="0" cy="0" r="500" fill="url('#background_gradient')" stroke="none"/>

        {/* Sectors */}
        {sectorPathItems}
        {sectorSeparatorItems}
        {sectorNameItems}

        {/* Cover */}
        <circle cx="0" cy="0" r="220" fill="url('#wheel_gradient')" stroke="none" pointerEvents="none"/>
        <circle cx="0" cy="0" r="110" fill="black"/>
        <circle cx="0" cy="0" r="110" fill="url('#logo_gradient')"/>
        <circle cx="0" cy="0" r="110" fill="black" stroke="gray" strokeWidth={3} mask="url(#logo)"/>
        
        {/* Flipper */}
        <path
          d="M 0 78.39 L -27.7 11.48 A 30 30 0 1 1 27.7 11.48 Z"
          className={classes.flipper}
          transform="translate(0, -460)"
        />
      </svg>

      <SectorEditModal
        key={editSectorIndex}
        sectors={sectors}
        sectorIndex={editSectorIndex}
        onClose={() => setEditSectorIndex(null)}
        onSave={handleSectorEdit}
        availableEffects={availableEffects}
      />

    </>
  );

}
