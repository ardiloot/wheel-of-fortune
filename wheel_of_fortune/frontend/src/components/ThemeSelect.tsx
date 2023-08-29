import { Select } from "@mantine/core";
import { ThemeInfo } from "../schemas";


export default function ThemeSelect({
  activeTheme,
  availableThemes,
  setActiveTheme
} : {
  activeTheme: string,
  availableThemes: Array<ThemeInfo>,
  setActiveTheme: (theme: string) => void
}) {

  return (
    <Select
      label="Theme:"
      value={ activeTheme }
      onChange={(theme: string) => {
        setActiveTheme(theme);
      }}
      data={ availableThemes.map((theme: any) => ({value: theme.id, label: theme.name})) }
    />
  )
}