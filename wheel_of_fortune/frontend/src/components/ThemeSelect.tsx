import { ThemeInfo } from "../schemas";
import { forwardRef } from 'react';
import { Group, Avatar, Text, Select } from '@mantine/core';

interface ItemProps extends React.ComponentPropsWithoutRef<'div'> {
  image: string;
  label: string;
  description: string;
}

const SelectItem = forwardRef<HTMLDivElement, ItemProps>(
  ({ image, label, description, ...others }: ItemProps, ref) => (
    <div ref={ref} {...others}>
      <Group noWrap>
        <Avatar src={image} />
        <div>
          <Text size="sm">{label}</Text>
          <Text size="xs" opacity={0.65}>
            {description}
          </Text>
        </div>
      </Group>
    </div>
  )
);

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

  const data = Object.keys(availableThemes).map((themeId) => {
    const theme = availableThemes[themeId]
    return {
      image: theme.image_url,
      value: themeId,
      label: theme.name,
      description: theme.description,
    }
  });

  return (
    <Select
      label="Theme:"
      itemComponent={SelectItem}
      value={ activeTheme }
      data={data}
      searchable
      filter={(value, item) =>
        item?.label?.toLowerCase().includes(value.toLowerCase().trim()) ||
        item.description.toLowerCase().includes(value.toLowerCase().trim())
      }
      onChange={(themeId) => {
        if (themeId !== null)
          setActiveTheme(themeId);
      }}
    />
  )
}