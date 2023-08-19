import { Select } from "@mantine/core";


export default function ThemeSelect({ apiUrl, wheelState, setWheelState } : {apiUrl: string, wheelState: any, setWheelState: any}) {

  const theme = wheelState?.theme ?? '';
  const themes = wheelState?.themes ?? [];

  const apiSetTheme = async (theme : string) => {
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ theme: theme })
    };
    const resp = await fetch(apiUrl + '/wheel', requestOptions);
    if (resp.status >= 400) {
      throw new Error('Server responds with error!');
    }
  };
  
  return (
    <Select
      label="Theme:"
      value={ theme }
      onChange={ async (theme) => {
        if (theme !== null) {
          setWheelState({
            ...wheelState,
            theme: theme,
          })
          await apiSetTheme(theme);
        }
      }}
      data={ themes.map((theme: any) => ({value: theme.id, label: theme.name})) }
    />
  )
}