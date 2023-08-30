import { createStyles } from "@mantine/core";

const useStyles = createStyles((theme) => ({
  flipper: {
    fill: theme.colors.dark[5],
    strokeWidth: 2,
    stroke: theme.colors.gray[5],
  },
}));


export interface SvgFlipperProps {
  x: number;
  y: number;
}

export default function SvgFlipper({
  x,
  y,
} : SvgFlipperProps) {
  
  const { classes } = useStyles();

  return (
    <path
      d="M 0 78.39 L -27.7 11.48 A 30 30 0 1 1 27.7 11.48 Z"
      className={classes.flipper}
      transform={`translate(${x}, ${y})`}
    />
  );
 
}
