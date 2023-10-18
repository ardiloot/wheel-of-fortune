const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export function resolveLocalUrl(url: string): string {
  if (BACKEND_URL !== undefined && url.startsWith('local/')) {
    return BACKEND_URL + url;
  } else {
    return url;
  }
}

export function toXY(radius: number, angle: number): { x: number; y: number } {
  // 0 deg = upwards
  // 90 deg = to right
  // ...
  return {
    x: radius * Math.sin(angle),
    y: radius * -Math.cos(angle),
  };
}

export function toDeg(radians: number): number {
  return radians * (180 / Math.PI);
}

export function toRad(degrees: number): number {
  return (Math.PI / 180) * degrees;
}
