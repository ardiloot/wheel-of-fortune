import { useState } from "react";
import SectorEditModal from "./SectorEditModal";
import { EffectInfo, EncoderState, SectorState, SectorStateIn, ServosState } from "../schemas";
import SvgFlipper from "./SvgFlipper";
import SvgLogo from "./SvgLogo";
import SvgLedGlow from "./SvgLedGlow";
import SvgWheel from "./SvgWheel";
import SvgServo from "./SvgServo";
import { toRad } from "../utils";


export interface WheelProps {
  servosState: ServosState;
  sectors: Array<SectorState>;
  availableEffects: Record<string, EffectInfo>;
  encoderState: EncoderState;
  updateSector: (index: number, state: SectorStateIn) => void;
}


export default function Wheel({
  servosState,
  sectors,
  availableEffects,
  encoderState,
  updateSector,
} : WheelProps) {

  const [editSectorIndex, setEditSectorIndex] = useState<number | null>(null);
  const angularWidth = 2.0 * Math.PI / Math.max(1, sectors.length);
  const curWheelAngle = angularWidth * encoderState.sector;

  const servoAnglesDeg = {
    bottom: 0,
    right: -135,
    left: 135,
  };

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
          Object.keys(servoAnglesDeg).map((name) => {
            const angleDeg: number = servoAnglesDeg[name as keyof typeof servoAnglesDeg];
            if (!(name in servosState.motors))
              return;
            const servo = servosState.motors[name];
            return (
              <SvgServo
                key={name}
                angle={toRad(angleDeg)}
                pos={servo.pos}
                onClick={() => {console.log('servo', angleDeg)}}
              />
            );
          })
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


