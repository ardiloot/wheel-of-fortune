import { createStyles } from "@mantine/core";
import { toDeg } from "../utils";


const useStyles = createStyles((theme) => ({
  servo: {
    fill: theme.colors.dark[4],
    strokeWidth: 1,
    stroke: theme.colors.dark[3],
    '&:hover': {
      fill: theme.colors.dark[3],
    },
  },
  outline: {
    fill: "transparent",
    opacity: 0.2,
    strokeWidth: 2,
    strokeDasharray: "5,5",
    stroke: theme.colors.dark[3],
    '&:hover': {
      fill: theme.colors.dark[3],
    },
  }
}));


export interface SvgServoProps {
  angle: number;
  pos: number;
  onClick: () => void;
}


export default function SvgServo({
  angle,
  pos,
  onClick,
} : SvgServoProps) {
  
  const { classes } = useStyles();

  const logoSize = 100;
  const zeroPos = 350;
  const fullPos = 450;
  const y = zeroPos + pos * (fullPos - zeroPos);
  return (
    <g transform={`rotate(${toDeg(angle)}) translate(0, ${y})`}>
      <rect
        x={-5}
        y={-200}
        width={10}
        height={200}
        className={classes.servo}
      />
      <circle
        cx={0}
        cy={fullPos - y}
        r={logoSize / 2}
        className={classes.outline}
        onClick={onClick}
      />
      <circle
        cx={0}
        cy={0}
        r={logoSize / 2}
        className={classes.servo}
        onClick={onClick}
      />
    </g>
  );

}