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
  num_sectors: z.number().int(),
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

// ----------------------------------------------------------------------------
// Sound system
// ----------------------------------------------------------------------------

export const SoundState = z.object({
  volume: z.number(),
  duration_secs: z.number(),
});
export type SoundState = z.infer<typeof SoundState>;


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
  sounds: z.record(z.string(), SoundState),
});
export type SoundSystemState = z.infer<typeof SoundSystemState>;


export const SoundSystemStateIn = z.object({
  channels: z.record(z.string(), SoundChannelStateIn).optional(),
});
export type SoundSystemStateIn = z.infer<typeof SoundSystemStateIn>;

// ----------------------------------------------------------------------------
// Sectors
// ----------------------------------------------------------------------------

export const SectorState = z.object({
  index: z.number().int(),
  name: z.string(),
  effect: z.string(),
});
export type SectorState = z.infer<typeof SectorState>;


export const SectorStateIn = z.object({
  name: z.string().optional(),
  effect: z.string().optional(),
});
export type SectorStateIn = z.infer<typeof SectorStateIn>;


// ----------------------------------------------------------------------------
// Themes
// ----------------------------------------------------------------------------

export const ThemeState = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  based_on: z.array(z.string()),
  theme_sound: z.string(),
});
export type ThemeState = z.infer<typeof ThemeState>;

// ----------------------------------------------------------------------------
// Effects
// ----------------------------------------------------------------------------

export const EffectState = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  based_on: z.array(z.string()),
  effect_sound: z.string(),
});

export type EffectState = z.infer<typeof EffectState>;

// ----------------------------------------------------------------------------
// Wheel
// ----------------------------------------------------------------------------

export const WheelState = z.object({
  task_name: z.string().optional(),
  theme: z.string(),
  themes: z.array(ThemeState),
  sectors: z.array(SectorState),
  effects: z.array(EffectState),
  encoder: EncoderState,
  leds: LedsState,
  soundsystem: SoundSystemState,
});
export type WheelState = z.infer<typeof WheelState>;


export const WheelStateIn = z.object({
  theme: z.string().optional(),
  sectors: z.record(z.number().int(), SectorStateIn).optional(),
  leds: LedsStateIn.optional(),
  soundsystem: SoundSystemStateIn.optional(),
});
export type WheelStateIn = z.infer<typeof WheelStateIn>;


export const WheelStateUpdate = z.object({
  task_name: z.string().optional(),
  theme: z.string().optional(),
  sectors: z.array(SectorState).optional(),
  encoder: EncoderState.optional(),
  leds: LedsState.optional(),
  soundsystem: SoundSystemState.optional(),
});
export type WheelStateUpdate = z.infer<typeof WheelStateUpdate>;

// ----------------------------------------------------------------------------
// Websocket
// ----------------------------------------------------------------------------

export const WsStatePacket = z.object({
  cmd: z.string(),
  ts: z.number(),
  state: WheelState,
});
export type WsStatePacket = z.infer<typeof WsStatePacket>;


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