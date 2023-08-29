import { Select } from "@mantine/core";
import { ThemeInfo } from "../schemas";


export default function ThemeSelect({
  activeTheme,
  availableThemes,
  setActiveTheme
} : {
  activeTheme: string,
  availableThemes: Record<string, ThemeInfo>,
  setActiveTheme: (theme: string) => void
}) {

  return (
    <Select
      label="Theme:"
      value={ activeTheme }
      onChange={(theme: string) => {
        setActiveTheme(theme);
      }}
      data={ Object.keys(availableThemes).map((themeId: string) => {
        const theme = availableThemes[themeId]
        return {
          value: themeId,
          label: theme.name,
        }
      })}
    />
  )
}