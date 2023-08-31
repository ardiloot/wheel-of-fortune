import { useEffect, useRef, useState } from 'react';
import { ColorScheme, ColorSchemeProvider, Container, LoadingOverlay, MantineProvider, Title } from '@mantine/core';
import { Notifications, notifications } from '@mantine/notifications';
import { useLocalStorage } from '@mantine/hooks';
import { IconCheck, IconX } from '@tabler/icons-react';
import ReconnectingWebSocket from 'reconnecting-websocket';
import { ColorSchemeToggle } from './components/ColorSchemeToggle';
import Wheel from './components/Wheel';
import VolumeSlider from './components/VolumeSlider';
import BrightnessSlider from './components/BrightnessSlider';
import ThemeSelect from './components/ThemeSelect';
import {
  WsInitPacket,
  WsUpdatePacket,
  WsSetStatePacket,
  SectorState,
  EncoderState,
  LedsState,
  SoundSystemState,
  WheelStateIn,
  ServosState,
  WheelInfo,
} from './schemas';

const WS_URL =
  import.meta.env.VITE_WS_URL ??
  (window.location.protocol === 'http:' ? 'ws://' : 'wss://') + window.location.host + '/api/v1/ws';

export default function App() {
  // Color scheme

  const [colorScheme, setColorScheme] = useLocalStorage<ColorScheme>({
    key: 'mantine-color-scheme',
    defaultValue: 'light',
    getInitialValueInEffect: true,
  });

  const toggleColorScheme = (value?: ColorScheme) =>
    setColorScheme(value || (colorScheme === 'dark' ? 'light' : 'dark'));

  // States

  const [connectionStatus, setConnectionStatus] = useState<number>(ReconnectingWebSocket.CLOSED);
  const [activeThemeId, setActiveThemeId] = useState<string>('');
  const [sectors, setSectors] = useState<Array<SectorState>>([]);
  const [encoderState, setEncoderState] = useState<EncoderState>({
    sector: 0,
    rpm: 0.0,
    total_revs: 0,
    total_sectors: 0,
    missed_sector_count: 0,
    standstill: true,
  });
  const [servosState, setServosState] = useState<ServosState>({
    motors: {},
  });
  const [ledsState, setLedsState] = useState<LedsState>({
    power_on: true,
    brightness: 1.0,
    segments: {},
  });
  const [soundsystemState, setSoundsystemState] = useState<SoundSystemState>({
    channels: {
      main: {
        volume: 0.0,
        sound_name: '',
      },
    },
  });
  const [info, setInfo] = useState<WheelInfo>({
    version: '',
    name: '',
    display_name: '',
    themes: {},
    effects: {},
    servos: {
      version: '',
      motors: {},
    },
    leds: {
      version: '',
    },
    soundsystem: {
      sounds: {},
    },
  });

  // Websocket

  const ws = useRef<ReconnectingWebSocket | null>(null);
  useEffect(() => {
    console.log('Connect to websocket', WS_URL);
    const wsConn = new ReconnectingWebSocket(WS_URL);
    ws.current = wsConn;

    wsConn.onopen = () => {
      console.log('ws opened');
      setConnectionStatus(wsConn.readyState);
      notifications.show({
        title: 'Websocket connected',
        message: '',
        color: 'green',
        icon: <IconCheck size="1.1rem" />,
      });
    };
    wsConn.onclose = () => {
      console.log('ws closed');
      setConnectionStatus(wsConn.readyState);
      notifications.show({
        title: 'Websocket closed',
        message: '',
        color: 'red',
        icon: <IconX size="1.1rem" />,
      });
    };
    wsConn.onerror = (event) => {
      console.log('ws error', event);
      setConnectionStatus(wsConn.readyState);
    };
    wsConn.onmessage = (e) => {
      const message = JSON.parse(e.data);
      console.log('ws message', message);

      if (message.cmd === 'init') {
        const packet = WsInitPacket.parse(message);
        const state = packet.state;
        console.log('state', state);

        setActiveThemeId(state.theme_id);
        setSectors(state.sectors);
        setEncoderState(state.encoder);
        setLedsState(state.leds);
        setServosState(state.servos);
        setSoundsystemState(state.soundsystem);

        const info = packet.info;
        console.log('info', info);
        setInfo(info);
      } else if (message.cmd === 'update') {
        const packet = WsUpdatePacket.parse(message);
        const update = packet.update;
        console.log('update', update);
        if (update.theme_id !== undefined) setActiveThemeId(update.theme_id);
        if (update.sectors !== undefined) setSectors(update.sectors);
        if (update.encoder !== undefined) setEncoderState(update.encoder);
        if (update.servos !== undefined) setServosState(update.servos);
        if (update.leds !== undefined) setLedsState(update.leds);
        if (update.soundsystem !== undefined) setSoundsystemState(update.soundsystem);
      }
    };

    return () => {
      wsConn.close();
    };
  }, []);

  // Set state

  function wsSetState(state: WheelStateIn) {
    if (ws.current === null) {
      console.warn('Websocket down, cannot set state', state);
      return;
    }
    const newState: WsSetStatePacket = {
      cmd: 'set_state',
      ts: Date.now() / 1000.0,
      state: state,
    };
    ws.current.send(JSON.stringify(newState));
  }

  return (
    <ColorSchemeProvider colorScheme={colorScheme} toggleColorScheme={toggleColorScheme}>
      <MantineProvider withGlobalStyles withNormalizeCSS theme={{ colorScheme }}>
        <Notifications />
        <Container size={600}>
          <LoadingOverlay
            visible={connectionStatus !== ReconnectingWebSocket.OPEN}
            overlayBlur={2}
            loaderProps={{ size: 'xl', variant: 'bars' }}
            transitionDuration={1000}
          />
          <Title order={1} align="center">
            {info.display_name}
          </Title>
          <ColorSchemeToggle />

          <ThemeSelect
            activeThemeId={activeThemeId}
            availableThemes={info?.themes || {}}
            setActiveThemeId={(themeId) => {
              console.log('set theme:', themeId);
              setActiveThemeId(themeId);
              wsSetState({ theme_id: themeId });
            }}
          />

          <VolumeSlider
            volume={soundsystemState.channels.main.volume}
            setVolume={(volume) => {
              setSoundsystemState({
                ...soundsystemState,
                channels: {
                  ...soundsystemState.channels,
                  main: {
                    ...soundsystemState.channels.main,
                    volume: volume,
                  },
                },
              });
            }}
            setVolumeEnd={(volume) => {
              wsSetState({ soundsystem: { channels: { main: { volume: volume } } } });
            }}
          />

          <BrightnessSlider
            brightness={ledsState.brightness}
            setBrightness={(brightness) => {
              setLedsState({
                ...ledsState,
                brightness: brightness,
              });
            }}
            setBrightnessEnd={(brightness) => {
              wsSetState({ leds: { brightness: brightness } });
            }}
          />

          <Wheel
            sectors={sectors}
            encoderState={encoderState}
            servosState={servosState}
            info={info}
            updateSector={(index, state) => {
              wsSetState({ sectors: { [index]: state } });
            }}
          />
        </Container>
      </MantineProvider>
    </ColorSchemeProvider>
  );
}
