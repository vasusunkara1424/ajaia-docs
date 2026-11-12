const PALETTE = ["#2563eb", "#7c3aed", "#059669", "#d97706", "#db2777", "#0891b2"];

export function Avatar({ name, size = 28 }: { name: string; size?: number }) {
  const initials = name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
  const hash = [...name].reduce((h, ch) => (h * 31 + ch.charCodeAt(0)) >>> 0, 7);
  const color = PALETTE[hash % PALETTE.length];
  return (
    <span
      className="avatar"
      title={name}
      style={{ width: size, height: size, fontSize: size * 0.4, background: color }}
    >
      {initials}
    </span>
  );
}
