import { z } from 'zod';

// ----------------------------------------------------------------------------
// Encoder
// ----------------------------------------------------------------------------

export const EncoderState = z.object({
  sector: z.number().int(),
  rpm: z.number(),
  total_revs: z.number(),
  total_sectors: z.number().int(),
  missed_sector_count: z.number().int(),
  standstill: z.boolean(),
});
export type EncoderState = z.infer<typeof EncoderState>;

// ----------------------------------------------------------------------------
// LEDs
// ----------------------------------------------------------------------------

export const LedSegmentState = z.object({
  enabled: z.boolean(),
  brightness: z.number(),
  palette: z.string(),
  primary_color: z.string(),
  secondary_color: z.string(),
  effect: z.string(),
  effect_speed: z.number(),
  effect_intensity: z.number(),
});
export type LedSegmentState = z.infer<typeof LedSegmentState>;


export const LedsState = z.object({
  power_on: z.boolean(),
  brightness: z.number(),
  segments: z.record(z.string(), LedSegmentState)
});
export type LedsState = z.infer<typeof LedsState>;


export const LedsStateIn = z.object({
  brightness: z.number().optional(),
});
export type LedsStateIn = z.infer<typeof LedsStateIn>;


export const LedsInfo = z.object({
  version: z.string(),
});
export type LedsInfo = z.infer<typeof LedsInfo>;

// ----------------------------------------------------------------------------
// Sound system
// ----------------------------------------------------------------------------

export const SoundInfo = z.object({
  duration_secs: z.number(),
});
export type SoundInfo = z.infer<typeof SoundInfo>;


export const SoundChannelState = z.object({
  volume: z.number(),
  sound_name: z.string().nullable().optional(),
});
export type SoundChannelState = z.infer<typeof SoundChannelState>;


export const SoundChannelStateIn = z.object({
  volume: z.number().optional(),
  sound_name: z.string().optional(),
});
export type SoundChannelStateIn = z.infer<typeof SoundChannelStateIn>;


export const SoundSystemState = z.object({
  channels: z.record(z.string(), SoundChannelState),
});
export type SoundSystemState = z.infer<typeof SoundSystemState>;


export const SoundSystemStateIn = z.object({
  channels: z.record(z.string(), SoundChannelStateIn).optional(),
});
export type SoundSystemStateIn = z.infer<typeof SoundSystemStateIn>;


export const SoundSystemInfo = z.object({
  sounds: z.record(z.string(), SoundInfo),
});
export type SoundSystemInfo = z.infer<typeof SoundSystemInfo>;

// ----------------------------------------------------------------------------
// Sectors
// ----------------------------------------------------------------------------

export const SectorState = z.object({
  index: z.number().int(),
  name: z.string(),
  effect_id: z.string(),
});
export type SectorState = z.infer<typeof SectorState>;


export const SectorStateIn = z.object({
  name: z.string().optional(),
  effect_id: z.string().optional(),
});
export type SectorStateIn = z.infer<typeof SectorStateIn>;

// ----------------------------------------------------------------------------
// Themes
// ----------------------------------------------------------------------------

export const ThemeInfo = z.object({
  name: z.string(),
  description: z.string(),
  based_on: z.array(z.string()),
  theme_sound: z.string(),
  // startup_led_preset: z.record(z.string(), LedSegmentStateIn),
  // idle_led_preset: z.record(z.string(), LedSegmentStateIn),
  // spinning_led_preset: z.record(z.string(), LedSegmentStateIn),
  // poweroff_led_preset: z.record(z.string(), LedSegmentStateIn),
});
export type ThemeInfo = z.infer<typeof ThemeInfo>;

// ----------------------------------------------------------------------------
// Effects
// ----------------------------------------------------------------------------

export const EffectInfo = z.object({
  name: z.string(),
  description: z.string(),
  based_on: z.array(z.string()),
  effect_sound: z.string(),
  // leds_preset: z.record(z.string(), LedSegmentStateIn),
});

export type EffectInfo = z.infer<typeof EffectInfo>;

// ----------------------------------------------------------------------------
// Wheel
// ----------------------------------------------------------------------------

export const WheelState = z.object({
  active_task: z.string().optional(),
  theme_id: z.string(),
  sectors: z.array(SectorState),
  encoder: EncoderState,
  leds: LedsState,
  soundsystem: SoundSystemState,
});
export type WheelState = z.infer<typeof WheelState>;


export const WheelStateIn = z.object({
  theme_id: z.string().optional(),
  sectors: z.record(z.number().int(), SectorStateIn).optional(),
  leds: LedsStateIn.optional(),
  soundsystem: SoundSystemStateIn.optional(),
});
export type WheelStateIn = z.infer<typeof WheelStateIn>;


export const WheelStateUpdate = z.object({
  active_task: z.string().optional(),
  theme_id: z.string().optional(),
  sectors: z.array(SectorState).optional(),
  encoder: EncoderState.optional(),
  leds: LedsState.optional(),
  soundsystem: SoundSystemState.optional(),
});
export type WheelStateUpdate = z.infer<typeof WheelStateUpdate>;


export const WheelInfo = z.object({
  version: z.string(),
  themes: z.record(z.string(), ThemeInfo),
  effects: z.record(z.string(), EffectInfo),
  leds: LedsInfo,
  soundsystem: SoundSystemInfo,
});
export type WheelInfo = z.infer<typeof WheelInfo>;

// ----------------------------------------------------------------------------
// Websocket
// ----------------------------------------------------------------------------

export const WsInitPacket = z.object({
  cmd: z.string(),
  ts: z.number(),
  state: WheelState,
  info: WheelInfo,
});
export type WsInitPacket = z.infer<typeof WsInitPacket>;


export const WsUpdatePacket = z.object({
  cmd: z.string(),
  ts: z.number(),
  update: WheelStateUpdate,
});
export type WsUpdatePacket = z.infer<typeof WsUpdatePacket>;


export const WsSetStatePacket = z.object({
  cmd: z.string(),
  ts: z.number(),
  state: WheelStateIn,
});
export type WsSetStatePacket = z.infer<typeof WsSetStatePacket>;