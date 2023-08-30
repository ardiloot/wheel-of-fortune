import { createStyles } from "@mantine/core";

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
}));


export interface SvgSectorProps {
  angle: number;
  angularWidth: number;
  radius: number;
  text: string;
  textColor: string;
  onClick: () => void;
}

export default function SvgSector({
  angle,
  angularWidth,
  radius,
  text,
  textColor,
  onClick,
} : SvgSectorProps) {

  const { classes } = useStyles();


  const p0 = toXY(radius, angle - 0.5 * angularWidth);
  const p1 = toXY(radius, angle + 0.5 * angularWidth);
  const d = 'M 0 0 L ' +
    `${p0.x.toFixed(3)} ${p0.y.toFixed(3)}` +
    `A ${radius} ${radius} 0 0 1 ` +
    `${p1.x.toFixed(3)} ${p1.y.toFixed(3)} ` +
    'Z';

  const textRadius = 0.95 * radius;
  const textPos = toXY(textRadius, angle);
  const textTransform =
    `translate(${textPos.x.toFixed(3)}, ${textPos.y.toFixed(3)}) ` +
    `rotate(${toDeg(angle  + Math.PI / 2).toFixed(3)})`;

  return (
    <>
      <path
        d={d}
        className={classes.sector}
        onClick={onClick}
      />
      <text
        x={0.0}
        y={0.0}
        className={classes.text}
        fill={textColor}
        transform={textTransform}
        opacity={0.8}
      >
        {text}
      </text>
    </>
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