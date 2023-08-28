import { Button, Group, Modal, NativeSelect, TextInput } from "@mantine/core"
import { useState } from "react";
import { EffectState, SectorState } from "../schemas";


export default function SectorEditModal({
  sectors,
  sectorIndex,
  effects,
  onClose,
  onSave
} : {
  sectors: Array<SectorState>,
  sectorIndex: number | null,
  effects: Array<EffectState>,
  onClose: () => void,
  onSave: (index: number, name: string, effect: string) => void 
}) {

  const sector = sectorIndex !== null ? sectors[sectorIndex] : null;
  const [name, setName] = useState<string>(sector?.name ?? '');
  const [effect, setEffect] = useState<string>(sector?.effect ?? '');

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
        value={effect}
        onChange={(e) => setEffect(e.target.value)}
        data={effects.map((effect) => ({
          value: effect.id,
          label: effect.name,
        }))}
      />
      <Group position="right" mt="md">
        <Button
          onClick={() => {
            if (sectorIndex !== null)
              onSave(sectorIndex, name, effect)
          }}
        >
          Save
        </Button>
      </Group>
    </Modal>
  )
}