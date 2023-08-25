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


const API_URL = (
  import.meta.env.VITE_API_URL ?? 
  window.location.protocol + '//' + window.location.host + '/api/v1'
);
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

  const [connectionStatus, setConnectionStatus] = useState<number>(-1)
  const [encoderState, setEncoderState] = useState(null)
  const [ledsState, setLedsState] = useState(null)
  const [soundState, setSoundState] = useState(null)
  const [wheelState, setWheelState] = useState(null)
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
        setEncoderState(message.data.encoder);
        setLedsState(message.data.leds);
        setSoundState(message.data.sound);
        setWheelState(message.data.wheel);
      } else if (message.cmd === 'update') {
        if ('encoder' in message.data)
          setEncoderState(message.data.encoder);
        if ('sound' in message.data)
          setSoundState(message.data.sound);
        if ('wheel' in message.data)
          setWheelState(message.data.wheel);
        if ('leds' in message.data)
          setLedsState(message.data.leds);
      }
    };

    return () => {
      wsConn.close();
    };
  }, []);

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
            apiUrl={API_URL}
            wheelState={wheelState}
            setWheelState={setWheelState}
          />

          <VolumeSlider
            ws={ws.current}
            soundState={soundState}
            setSoundState={setSoundState}
          />

          <BrightnessSlider
            ws={ws.current}
            ledsState={ledsState}
            setLedsState={setLedsState}
          />

          <Wheel
            apiUrl={API_URL}
            encoderState={encoderState}
            wheelState={wheelState}
          />

        </Container>
      </MantineProvider>
    </ColorSchemeProvider>
  )
}