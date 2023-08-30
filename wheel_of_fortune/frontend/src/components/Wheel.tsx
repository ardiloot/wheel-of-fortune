import { useState } from "react";
import SectorEditModal from "./SectorEditModal";
import { EffectInfo, EncoderState, SectorState, SectorStateIn } from "../schemas";
import SvgFlipper from "./SvgFlipper";
import SvgLogo from "./SvgLogo";
import SvgLedGlow from "./SvgLedGlow";
import SvgWheel from "./SvgWheel";
import SvgServo from "./SvgServo";
import { Switch } from "@mantine/core";
import { toRad } from "../utils";


export interface WheelProps {
  sectors: Array<SectorState>;
  availableEffects: Record<string, EffectInfo>;
  encoderState: EncoderState;
  updateSector: (index: number, state: SectorStateIn) => void;
}


export default function Wheel({
  sectors,
  availableEffects,
  encoderState,
  updateSector,
} : WheelProps) {

  const [editSectorIndex, setEditSectorIndex] = useState<number | null>(null);
  const [servoPos, setServoPos] = useState<number>(0);
  const angularWidth = 2.0 * Math.PI / Math.max(1, sectors.length);
  const curWheelAngle = angularWidth * encoderState.sector;

  return (
    <>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="-500 -500 1000 1000"
      >        
        <SvgLedGlow
          id="background"
          radius={500}
          stops={[
            {offset: "80%", color: "blue", opacity: 0.3},
            {offset: "100%", color: "blue", opacity: 0.0},
          ]}
        />

        {/* Servos */}
        {
          [0, 135, -135].map((angleDeg) => (
            <SvgServo
            angle={toRad(angleDeg)}
            pos={servoPos}
            onClick={() => {console.log('servo', angleDeg)}}
          />
          ))
        }
          
        <SvgWheel
          radius={400}
          wheelAngle={curWheelAngle}
          sectors={sectors}
          availableEffects={availableEffects}
          onSectorClick={setEditSectorIndex}
        />

        <SvgLedGlow
          id="wheel"
          radius={220}
          stops={[
            {offset: "50%", color: "orange", opacity: 0.2},
            {offset: "100%", color: "orange", opacity: 0.0},
          ]}
        />
        
        <SvgLogo
          radius={110}
        />
      
        <SvgFlipper
          x={0}
          y={-460}
        />
        
      </svg>

      <Switch
        label="Servo pos"
        onChange={(event) => setServoPos(event.currentTarget.checked ? 1.0 : 0.0)}
      />

      <SectorEditModal
        key={editSectorIndex}
        sectors={sectors}
        sectorIndex={editSectorIndex}
        onClose={() => {
          setEditSectorIndex(null);
        }}
        onSave={(index, state) => {
          setEditSectorIndex(null);
          updateSector(index, state);
        }}
        availableEffects={availableEffects}
      />

    </>
  );

}


