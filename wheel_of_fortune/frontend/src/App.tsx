import { useEffect, useRef, useState } from 'react';
import { ColorScheme, ColorSchemeProvider, Container, LoadingOverlay, MantineProvider, Title } from '@mantine/core';
import { Notifications, notifications } from '@mantine/notifications';
import Wheel from './components/Wheel';
import VolumeSlider from './components/VolumeSlider';
import BrightnessSlider from './components/BrightnessSlider';
import ThemeSelect from './components/ThemeSelect';
import ReconnectingWebSocket from 'reconnecting-websocket';
import { ColorSchemeToggle } from './components/ColorSchemeToggle';
import { useLocalStorage } from '@mantine/hooks';
import { IconCheck, IconX } from '@tabler/icons-react';
import { WsStatePacket, ThemeState, WsUpdatePacket, WsSetStatePacket, SectorState, EffectState, EncoderState, LedsState, SoundSystemState, WheelStateIn } from './schemas';
import { throttle } from 'lodash';


const WS_URL = (
  import.meta.env.VITE_WS_URL ?? 
  (window.location.protocol === 'http:' ? 'ws://' : 'wss://') + window.location.host + '/api/v1/ws'
);

export default function App() {
  const [colorScheme, setColorScheme] = useLocalStorage<ColorScheme>({
    key: 'mantine-color-scheme',
    defaultValue: 'light',
    getInitialValueInEffect: true,
  });

  const toggleColorScheme = (value?: ColorScheme) =>
    setColorScheme(value || (colorScheme === 'dark' ? 'light' : 'dark'));

  // States

  const [connectionStatus, setConnectionStatus] = useState<number>(-1);
  const [activeTheme, setActiveTheme] = useState<string>('');
  const [availableThemes, setAvailableThemes] = useState<Array<ThemeState>>([]);
  const [sectors, setSectors] = useState<Array<SectorState>>([]);
  const [effects, setEffects] = useState<Array<EffectState>>([]);
  const [encoderState, setEncoderState] = useState<EncoderState>({
    sector: 0,
    rpm: 0.0,
    total_revs: 0,
    total_sectors: 0,
    missed_sector_count: 0,
    num_sectors: 0,
    standstill: true,
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
      }
    },
    sounds: {},
  })

  // Websocket

  const ws = useRef<ReconnectingWebSocket | null>(null)
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
        icon: <IconCheck size="1.1rem" />
      });
      
    }
    wsConn.onclose = () => {
      console.log('ws closed');
      setConnectionStatus(wsConn.readyState);
      notifications.show({
        title: 'Websocket closed',
        message: '',
        color: 'red',
        icon: <IconX size="1.1rem" />
      });
    }
    wsConn.onerror = (event) => {
      console.log('ws error', event);
      setConnectionStatus(wsConn.readyState);
    }
    wsConn.onmessage = e => {
      const message = JSON.parse(e.data);
      console.log('ws message', message);

      if (message.cmd === 'state') {
        const packet = WsStatePacket.parse(message);
        const state = packet.state;
        console.log('state', state);
        setActiveTheme(state.theme);
        setAvailableThemes(state.themes);
        setSectors(state.sectors);
        setEffects(state.effects);
        setEncoderState(state.encoder);
        setLedsState(state.leds);
        setSoundsystemState(state.soundsystem);
      } else if (message.cmd === 'update') {
        const packet = WsUpdatePacket.parse(message);
        const update = packet.update;
        console.log('update', update);
        if (update.theme !== undefined)
          setActiveTheme(update.theme);
        if (update.sectors !== undefined)
          setSectors(update.sectors);
        if (update.encoder !== undefined)
          setEncoderState(update.encoder);
        if (update.leds !== undefined)
          setLedsState(update.leds);
        if (update.soundsystem !== undefined)
          setSoundsystemState(update.soundsystem);
      }
    };

    return () => {
      wsConn.close();
    };
  }, []);

  // Set state
  function wsSetState(state: WheelStateIn) {
    if (ws.current === null) {
      console.warn('Websocet down, cannot set state', state);
      return;
    }
    const newState: WsSetStatePacket = {
      cmd: 'set_state',
      ts: Date.now() / 1000.0,
      state: state,
    };
    ws.current.send(JSON.stringify(newState));
  };

  const throttledSetBrightness = useRef(
    throttle((brightness : number) => {
      wsSetState({
        leds: {
          brightness: brightness,
        },
      });
    }, 250)
  ).current;

  const throttledSetVolume = useRef(
    throttle((volume : number) => {
      wsSetState({
        soundsystem: {
          channels: {
            main: {
              volume: volume,
            },
          },
        }
      })
    }, 250)
  ).current;

  return (
    <ColorSchemeProvider colorScheme={colorScheme} toggleColorScheme={toggleColorScheme}>
      <MantineProvider
        withGlobalStyles
        withNormalizeCSS
        theme={{ colorScheme }}
      >
        <Notifications />
        <Container size={600}>
          <LoadingOverlay
            visible={connectionStatus !== ReconnectingWebSocket.OPEN}
            overlayBlur={2}
            loaderProps={{ size: 'xl', variant: 'bars' }}
            transitionDuration={1000}
          />
          <Title order={1} align="center">Wheel of Fortune</Title>
          <ColorSchemeToggle />

          <ThemeSelect
            activeTheme={activeTheme}
            availableThemes={availableThemes}
            setActiveTheme={async (theme: string) => {
              console.log('set theme:', theme)
              setActiveTheme(theme);
              wsSetState({theme: theme});
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
                  }
                }
              });
              throttledSetVolume(volume);
            }}
          />

          <BrightnessSlider
            brightness={ledsState.brightness}
            setBrightness={(brightness) => {
              setLedsState({
                ...ledsState,
                brightness: brightness,
              });
              throttledSetBrightness(brightness);
            }}
          />

          <Wheel
            sectors={sectors}
            effects={effects}
            encoderState={encoderState}
            updateSector={async (index, name, effect) => {
              wsSetState({
                sectors: {
                  [index]: {
                    name: name,
                    effect: effect,
                  },
                },
              });
            }}
          />

        </Container>
      </MantineProvider>
    </ColorSchemeProvider>
  )
}