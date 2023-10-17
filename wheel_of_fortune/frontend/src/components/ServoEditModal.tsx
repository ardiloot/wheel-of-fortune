import { Button, Modal, Stack, Select, Alert } from '@mantine/core';
import { ServoStateIn, ServosInfo } from '../schemas';
import { useState } from 'react';
import { IconAlertTriangle, IconInfoCircle } from '@tabler/icons-react';

enum MotorCommand {
  GotoZero = 'goto_zero',
  GotoFull = 'goto_full',
  Unmount = 'unmount',
  Mount = 'mount',
}

export interface ServoEditModalProps {
  name: string | null;
  servosInfo: ServosInfo;
  updateServo: (name: string, state: ServoStateIn) => void;
  onClose: () => void;
}

export default function ServoEditModal({ name, servosInfo, updateServo, onClose }: ServoEditModalProps) {
  const [curCommand, setCurCommand] = useState<MotorCommand>(MotorCommand.GotoZero);
  const [inProgress, setInProgress] = useState<boolean>(false);
  const motorName = name ? name : '';
  const motorInfo = name !== null ? servosInfo.motors[name] : null;

  function sleep(ms: number = 0) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async function executeCommand() {
    setInProgress(true);
    if (curCommand == MotorCommand.GotoZero) {
      updateServo(motorName, { pos: 0.0, detached: false });
      await sleep(5000);
    } else if (curCommand == MotorCommand.GotoFull) {
      updateServo(motorName, { pos: 1.0, detached: false });
      await sleep(5000);
    } else if (curCommand == MotorCommand.Unmount) {
      updateServo(motorName, { pos: motorInfo?.mount_pos, detached: false });
      await sleep(5000);
      updateServo(motorName, { detached: true });
    } else if (curCommand == MotorCommand.Mount) {
      updateServo(motorName, { pos: motorInfo?.mount_pos, detached: false });
      await sleep(10000);
      updateServo(motorName, { pos: 0.0, detached: false });
    }
    setInProgress(false);
  }

  function getInfoMessage(): string {
    if (curCommand == MotorCommand.GotoZero) {
      return 'Logo will move to zero position (hidden position)';
    } else if (curCommand == MotorCommand.GotoFull) {
      return 'Will move to 100% position (display position)';
    } else if (curCommand == MotorCommand.Unmount) {
      return 'Commands logo to move out and then releases the logo. NB: logo might fall down';
    } else if (curCommand == MotorCommand.Mount) {
      return 'Motor will move to mount position, stay for 10 seconds and then move back to zero.';
    }
    return 'No information is available';
  }

  const showWarning = curCommand == MotorCommand.Mount || curCommand == MotorCommand.Unmount;
  return (
    <Modal
      opened={name !== null}
      onClose={onClose}
      title={'Side logo (' + motorName + '):'}
      styles={{ content: { overflow: 'visible !important' } }}
    >
      <Stack>
        <Select
          label="Command:"
          value={curCommand}
          data={[
            { value: MotorCommand.GotoZero, label: 'Move to hidden position' },
            { value: MotorCommand.GotoFull, label: 'Move to display position' },
            { value: MotorCommand.Unmount, label: 'Remove logo' },
            { value: MotorCommand.Mount, label: 'Attach logo' },
          ]}
          onChange={(command: string) => {
            if (command !== null) {
              setCurCommand(command as MotorCommand);
            }
          }}
        />
        <Alert
          variant="light"
          color={showWarning ? 'orange' : 'blue'}
          title="Info"
          icon={showWarning ? <IconAlertTriangle /> : <IconInfoCircle />}
        >
          {getInfoMessage()}
        </Alert>
        <Button loading={inProgress} onClick={executeCommand}>
          Execute
        </Button>
      </Stack>
    </Modal>
  );
}
