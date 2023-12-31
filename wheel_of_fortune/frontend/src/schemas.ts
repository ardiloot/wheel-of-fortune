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
// Servos
// ----------------------------------------------------------------------------

export const ServoState = z.object({
  pos: z.number(),
  duty: z.number(),
  detached: z.boolean(),
});
export type ServoState = z.infer<typeof ServoState>;

export const ServoStateIn = z.object({
  pos: z.number().optional(),
  detached: z.boolean().optional(),
});
export type ServoStateIn = z.infer<typeof ServoStateIn>;

export const ServoInfo = z.object({
  mount_angle: z.number(),
  zero_duty: z.number(),
  full_duty: z.number(),
  mount_duty: z.number(),
  mount_pos: z.number(),
});
export type ServoInfo = z.infer<typeof ServoInfo>;

export const ServosState = z.object({
  motors: z.record(z.string(), ServoState),
});
export type ServosState = z.infer<typeof ServosState>;

export const ServosStateIn = z.object({
  motors: z.record(z.string(), ServoStateIn).default({}),
});
export type ServosStateIn = z.infer<typeof ServosStateIn>;

export const ServosInfo = z.object({
  version: z.string(),
  motors: z.record(z.string(), ServoInfo),
});
export type ServosInfo = z.infer<typeof ServosInfo>;

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
  segments: z.record(z.string(), LedSegmentState),
});
export type LedsState = z.infer<typeof LedsState>;

export const LedsStateIn = z.object({
  brightness: z.number().optional(),
  transition_ms: z.number().optional(),
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
  image_url: z.string(),
  based_on: z.array(z.string()),
  startup_sound: z.string(),
  theme_sounds: z.array(z.string()),
  poweroff_sound: z.string(),
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
  image_url: z.string(),
  color: z.string(),
  based_on: z.array(z.string()),
  effect_sound: z.string(),
  // leds_preset: z.record(z.string(), LedSegmentStateIn),
  active_servos: z.array(z.string()),
});

export type EffectInfo = z.infer<typeof EffectInfo>;

// ----------------------------------------------------------------------------
// Wheel
// ----------------------------------------------------------------------------

export const WheelState = z.object({
  active_task: z.string().optional(),
  theme_id: z.string(),
  standby_timer: z.number(),
  sectors: z.array(SectorState),
  encoder: EncoderState,
  leds: LedsState,
  servos: ServosState,
  soundsystem: SoundSystemState,
});
export type WheelState = z.infer<typeof WheelState>;

export const WheelStateIn = z.object({
  theme_id: z.string().optional(),
  standby_timer: z.number().optional(),
  sectors: z.record(z.number().int(), SectorStateIn).optional(),
  leds: LedsStateIn.optional(),
  servos: ServosStateIn.optional(),
  soundsystem: SoundSystemStateIn.optional(),
});
export type WheelStateIn = z.infer<typeof WheelStateIn>;

export const WheelStateUpdate = z.object({
  active_task: z.string().optional(),
  theme_id: z.string().optional(),
  standby_timer: z.number().optional(),
  sectors: z.array(SectorState).optional(),
  encoder: EncoderState.optional(),
  servos: ServosState.optional(),
  leds: LedsState.optional(),
  soundsystem: SoundSystemState.optional(),
});
export type WheelStateUpdate = z.infer<typeof WheelStateUpdate>;

export const WheelInfo = z.object({
  version: z.string(),
  name: z.string(),
  display_name: z.string(),
  logo_url: z.string(),
  themes: z.record(z.string(), ThemeInfo),
  effects: z.record(z.string(), EffectInfo),
  servos: ServosInfo,
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
