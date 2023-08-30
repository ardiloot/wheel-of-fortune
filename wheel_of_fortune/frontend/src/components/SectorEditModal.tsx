import { Button, Group, Modal, TextInput } from "@mantine/core"
import { useState } from "react";
import { EffectInfo, SectorState, SectorStateIn } from "../schemas";
import EffectSelect from "./EffectSelect";


export interface SectorEditModalProps {
  sectors: Array<SectorState>;
  sectorIndex: number | null;
  availableEffects: Record<string, EffectInfo>;
  onClose: () => void;
  onSave: (index: number, state: SectorStateIn) => void;
}


export default function SectorEditModal({
  sectors,
  sectorIndex,
  availableEffects,
  onClose,
  onSave
} : SectorEditModalProps) {

  const sector = sectorIndex !== null ? sectors[sectorIndex] : null;
  const [name, setName] = useState<string>(sector?.name ?? '');
  const [effectId, setEffectId] = useState<string>(sector?.effect_id ?? '');

  return (
    <Modal
      opened={sectorIndex !== null}
      onClose={onClose}
      title={'Sector (' + (sectorIndex !== null ? sectorIndex : '') + ') edit'}
      styles={{ content: { overflow: 'visible !important' } }}
    >
      <TextInput
        placeholder="Name of the sector"
        label="Name:"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <EffectSelect
        activeEffectId={effectId}
        availableEffects={availableEffects}
        setEffectId={setEffectId}
      />
      <Group position="right" mt="md">
        <Button
          onClick={() => {
            if (sectorIndex !== null)
              onSave(sectorIndex, {
                name: name,
                effect_id: effectId,
              })
          }}
        >
          Save
        </Button>
      </Group>
    </Modal>
  )
}