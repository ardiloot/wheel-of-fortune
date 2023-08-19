import { Button, Group, Modal, NativeSelect, TextInput } from "@mantine/core"
import { useState } from "react";


export default function SectorEditModal({ sectors, sectorIndex, effects, onClose, onSave } : 
    {
      sectors: Array<any>,
      sectorIndex: number | null,
      effects: Array<any>,
      onClose: () => void,
      onSave: (index: number, name: string, effect: string) => void 
    })
{

  const sector = sectorIndex !== null ? sectors[sectorIndex] : null;
  const [name, setName] = useState(sectorIndex !== null ? sector.name : '');
  const [effect, setEffect] = useState(sectorIndex !== null ? sector.effect : '');

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
        label="Efect:"
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