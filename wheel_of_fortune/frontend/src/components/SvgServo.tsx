import { createStyles, useMantineTheme } from "@mantine/core";
import { toDeg } from "../utils";
import { ServoState } from "../schemas";


const useStyles = createStyles((theme) => ({
  hover: {
    '&:hover': {
      fill: theme.colors.dark[3],
    },
  },
}));


export interface SvgServoProps {
  angle: number;
  servoState: ServoState;
  onClick: () => void;
}


export default function SvgServo({
  angle,
  servoState,
  onClick,
} : SvgServoProps) {
  
  const { classes } = useStyles();
  const theme = useMantineTheme();

  const logoSize = 100;
  const zeroPos = 350;
  const fullPos = 450;
  const y = zeroPos + servoState.pos * (fullPos - zeroPos);
  const stroke = servoState.detached ? theme.colors.red[9] : theme.colors.dark[3];

  return (
    <g transform={`rotate(${toDeg(angle)}) translate(0, ${y})`}>
      <rect
        x={-5}
        y={-200}
        width={10}
        height={200}
        stroke={theme.colors.dark[3]}
        strokeWidth={1}
        fill={theme.colors.dark[4]}
      />
      <circle
        cx={0}
        cy={fullPos - y}
        r={logoSize / 2}
        onClick={onClick}
        stroke={stroke}
        opacity={0.2}
        strokeWidth={2}
        strokeDasharray="5,5"
        fill="transparent"
        className={classes.hover}
      />
      <circle
        cx={0}
        cy={0}
        r={logoSize / 2}
        onClick={onClick}
        stroke={stroke}
        strokeWidth={2}
        fill={theme.colors.dark[4]}
        className={classes.hover}
      />
    </g>
  );

}