export interface SvgLogoProps {
  radius: number;
}

export default function SvgLogo({ radius }: SvgLogoProps) {
  return (
    <>
      <defs>
        <radialGradient id="logo_gradient">
          <stop offset="0%" stopColor="red" stopOpacity="0.8" />
          <stop offset="100%" stopColor="blue" stopOpacity="0.8" />
        </radialGradient>
        <mask id="logo">
          <circle fill="white" cx={0} cy={0} r={500} />
          <image x="-110" y="-110" width="220" height="220" href="logos/logo.svg" />
        </mask>
      </defs>

      <circle cx="0" cy="0" r={radius} fill="black" />
      <circle cx="0" cy="0" r={radius} fill="url('#logo_gradient')" />
      <circle cx="0" cy="0" r={radius} fill="black" stroke="gray" strokeWidth={3} mask="url(#logo)" />
    </>
  );
}
