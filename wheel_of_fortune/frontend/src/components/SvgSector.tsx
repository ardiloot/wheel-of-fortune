import { createStyles, useMantineTheme } from "@mantine/core";
import { toDeg, toXY } from "../utils";


const useStyles = createStyles((theme) => ({
  hover: {
    '&:hover': {
      fill: theme.colors.dark[2],
    },
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
  const theme = useMantineTheme();

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
        stroke={theme.colors.gray[0]}
        fill={theme.colors.dark[6]}
        strokeWidth={1}
        className={classes.hover}
        onClick={onClick}
      />
      <text
        x={0.0}
        y={0.0}
        fill={textColor}
        transform={textTransform}
        opacity={0.8}
        fontSize="35px"
        alignmentBaseline="middle"
        pointerEvents="none"
        fontFamily="Verdana, sans-serif"
      >
        {text}
      </text>
    </>
  );
}

