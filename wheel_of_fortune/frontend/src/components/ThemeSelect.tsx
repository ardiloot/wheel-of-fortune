import { Select } from "@mantine/core";
import { ThemeInfo } from "../schemas";


export interface ThemeSelectProps {
  activeTheme: string;
  availableThemes: Record<string, ThemeInfo>;
  setActiveTheme: (themeId: string) => void;
}


export default function ThemeSelect({
  activeTheme,
  availableThemes,
  setActiveTheme
} : ThemeSelectProps ) {

  return (
    <Select
      label="Theme:"
      value={ activeTheme }
      onChange={(themeId) => {
        if (themeId !== null)
          setActiveTheme(themeId);
      }}
      data={ Object.keys(availableThemes).map((themeId) => {
        const theme = availableThemes[themeId]
        return {
          value: themeId,
          label: theme.name,
        }
      })}
    />
  )
}