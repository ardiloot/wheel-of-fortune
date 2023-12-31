import { ThemeInfo } from '../schemas';
import { forwardRef } from 'react';
import { Group, Avatar, Text, Select } from '@mantine/core';
import { resolveLocalUrl } from '../utils';

interface ItemProps extends React.ComponentPropsWithoutRef<'div'> {
  image: string;
  label: string;
  description: string;
}

const SelectItem = forwardRef<HTMLDivElement, ItemProps>(({ image, label, description, ...others }: ItemProps, ref) => (
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
));
SelectItem.displayName = 'SelectItem';

export interface ThemeSelectProps {
  activeThemeId: string;
  availableThemes: Record<string, ThemeInfo>;
  setActiveThemeId: (themeId: string) => void;
}

export default function ThemeSelect({ activeThemeId, availableThemes, setActiveThemeId }: ThemeSelectProps) {
  const data = Object.keys(availableThemes).map((themeId) => {
    const theme = availableThemes[themeId];
    return {
      image: resolveLocalUrl(theme.image_url),
      value: themeId,
      label: theme.name,
      description: theme.description,
    };
  });

  const activeTheme = availableThemes[activeThemeId];

  return (
    <Select
      label="Theme:"
      icon={
        <Avatar size="1.5rem" src={activeTheme !== undefined ? resolveLocalUrl(activeTheme.image_url) : undefined} />
      }
      itemComponent={SelectItem}
      value={activeThemeId}
      data={data}
      searchable
      filter={(value, item) =>
        item?.label?.toLowerCase().includes(value.toLowerCase().trim()) ||
        item.description.toLowerCase().includes(value.toLowerCase().trim())
      }
      onChange={(themeId) => {
        if (themeId !== null) setActiveThemeId(themeId);
      }}
    />
  );
}
