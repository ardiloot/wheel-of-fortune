import { Button, Text, Modal, Stack, Group } from '@mantine/core';
import { ServoStateIn, ServosInfo, ServosState } from '../schemas';
import { useState } from 'react';

export interface ServoEditModalProps {
  name: string | null;
  servosState: ServosState;
  servosInfo: ServosInfo;
  updateServo: (name: string, state: ServoStateIn) => void;
  onClose: () => void;
}

export default function ServoEditModal({ name, servosState, servosInfo, updateServo, onClose }: ServoEditModalProps) {
  const [inProgress, setInProgress] = useState(false);
  const motorName = name ? name : '';
  const motorState = name !== null ? servosState.motors[name] : null;
  const motorInfo = name !== null ? servosInfo.motors[name] : null;
  console.log('edit servo', name, motorState, motorInfo);

  function sleep(ms: number = 0) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async function unmount() {
    setInProgress(true);
    updateServo(motorName, { pos: motorInfo?.mount_pos, detached: false });
    await sleep(5000);
    updateServo(motorName, { detached: true });
    setInProgress(false);
  }

  async function setPos(pos: number) {
    setInProgress(true);
    updateServo(motorName, { pos: pos, detached: false });
    await sleep(5000);
    setInProgress(false);
  }

  return (
    <Modal
      opened={name !== null}
      onClose={onClose}
      title={'Side logo (' + motorName + '):'}
      styles={{ content: { overflow: 'visible !important' } }}
    >
      <Stack>
        <Group spacing="xs">
          <Text fw={500}>Current position:</Text>
          <Text>
            {(100 * (motorState ? motorState.pos : 0)).toFixed(1)} % ({motorState?.detached ? 'detached' : 'attached'})
          </Text>
        </Group>
        <Button
          loading={inProgress}
          onClick={async () => {
            setPos(0.0);
          }}
        >
          Go to zero
        </Button>
        <Button loading={inProgress} onClick={unmount}>
          Unmount
        </Button>
        <Button loading={inProgress} onClick={unmount}>
          Prepare to mount
        </Button>
      </Stack>
    </Modal>
  );
}
