import { useState } from "react";
import SectorEditModal from "./SectorEditModal";
import { EncoderState, SectorState, SectorStateIn, ServosState, WheelInfo } from "../schemas";
import SvgFlipper from "./SvgFlipper";
import SvgLogo from "./SvgLogo";
import SvgLedGlow from "./SvgLedGlow";
import SvgWheel from "./SvgWheel";
import SvgServo from "./SvgServo";


export interface WheelProps {
  sectors: Array<SectorState>;
  encoderState: EncoderState;
  servosState: ServosState;
  info: WheelInfo;
  updateSector: (index: number, state: SectorStateIn) => void;
}


export default function Wheel({
  sectors,
  encoderState,
  servosState,
  info,
  updateSector,
} : WheelProps) {

  const [editSectorIndex, setEditSectorIndex] = useState<number | null>(null);
  const angularWidth = 2.0 * Math.PI / Math.max(1, sectors.length);
  const curWheelAngle = angularWidth * encoderState.sector;

  return (
    <>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="-520 -520 1040 1040"
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
          Object.keys(info.servos.motors).map((name) => {
            const servoInfo = info.servos.motors[name];
            if (!(name in servosState.motors))
              return;
            const servoState = servosState.motors[name];
            return (
              <SvgServo
                key={name}
                servoInfo={servoInfo}
                servoState={servoState}
                onClick={() => {console.log('servo', name, servoState, servoInfo)}}
              />
            );
          })
        }
          
        <SvgWheel
          radius={400}
          wheelAngle={curWheelAngle}
          sectors={sectors}
          availableEffects={info.effects}
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
        availableEffects={info.effects}
      />

    </>
  );

}


