import { Button, Group, Modal, NativeSelect, TextInput } from "@mantine/core"
import { useState } from "react";
import { EffectInfo, SectorState } from "../schemas";


export default function SectorEditModal({
  sectors,
  sectorIndex,
  availableEffects,
  onClose,
  onSave
} : {
  sectors: Array<SectorState>,
  sectorIndex: number | null,
  availableEffects: Record<string, EffectInfo>,
  onClose: () => void,
  onSave: (index: number, name: string, effect: string) => void 
}) {

  const sector = sectorIndex !== null ? sectors[sectorIndex] : null;
  const [name, setName] = useState<string>(sector?.name ?? '');
  const [effectId, setEffectId] = useState<string>(sector?.effect_id ?? '');

  return (
    <Modal
      opened={sectorIndex !== null}
      onClose={onClose}
      title={'Sector (' + (sectorIndex !== null ? sectorIndex : '') + ') edit'}
    >
      <TextInput
        placeholder="Name of the sector"
        label="Name:"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <NativeSelect
        label="Effect:"
        placeholder="Please select one"
        value={effectId}
        onChange={(e) => setEffectId(e.target.value)}
        data={Object.keys(availableEffects).map((effectId) => {
          const effect = availableEffects[effectId];
          return {
            value: effectId,
            label: effect.name,
          };
        })}
      />
      <Group position="right" mt="md">
        <Button
          onClick={() => {
            if (sectorIndex !== null)
              onSave(sectorIndex, name, effectId)
          }}
        >
          Save
        </Button>
      </Group>
    </Modal>
  )
}