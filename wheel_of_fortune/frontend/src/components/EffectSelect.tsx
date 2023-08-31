import { EffectInfo } from "../schemas";
import { forwardRef } from 'react';
import { Group, Avatar, Text, Select, ColorSwatch } from '@mantine/core';

interface ItemProps extends React.ComponentPropsWithoutRef<'div'> {
  image: string;
  label: string;
  description: string;
  color: string;
}

const SelectItem = forwardRef<HTMLDivElement, ItemProps>(
  ({ image, label, description, color, ...others }: ItemProps, ref) => (
    <div ref={ref} {...others}>
      <Group position="apart" noWrap>
        <Group noWrap>
          <Avatar
            src={image}
          />
          <div>
            <Text size="sm">{label}</Text>
            <Text size="xs" opacity={0.65}>
              {description}
            </Text>
          </div>
        </Group>
        <ColorSwatch
            color={color}
            opacity={0.7}
            radius="sm"
          />
      </Group>
    </div>
  )
);
SelectItem.displayName = 'SelectItem';

export interface EffectSelectProps {
  activeEffectId: string;
  availableEffects: Record<string, EffectInfo>;
  setEffectId: (effectId: string) => void;
}


export default function EffectSelect({
  activeEffectId,
  availableEffects,
  setEffectId,
} : EffectSelectProps ) {

  const data = Object.keys(availableEffects).map((effectId) => {
    const effect = availableEffects[effectId]
    return {
      image: effect.image_url,
      value: effectId,
      label: effect.name,
      description: effect.description,
      color: effect.color,
    }
  });

  return (
    <Select
      label="Effect:"
      itemComponent={SelectItem}
      value={ activeEffectId }
      data={data}
      searchable
      filter={(value, item) =>
        item?.label?.toLowerCase().includes(value.toLowerCase().trim()) ||
        item.description.toLowerCase().includes(value.toLowerCase().trim())
      }
      onChange={(effectId) => {
        if (effectId !== null)
          setEffectId(effectId);
      }}
    />
  )
}