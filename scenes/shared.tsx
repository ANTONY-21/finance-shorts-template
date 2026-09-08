import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from 'remotion';

// Shared cardboard-scene primitives for Ravi's First Crash.
// GROUNDING RULE: every object bottom edge touches a surface. DESK_Y = 880.

export const CARD = '#C8A165';
export const CARD_DARK = '#A5804A';
export const CARD_DEEP = '#8F6B3C';
export const INK = '#3A2A18';
export const BG = '#E8D9BE';
export const BLUE = '#2B3A67';
export const GREEN = '#7EC87E';
export const RED = '#FF6B5E';
export const GOLD = '#FFD24A';
export const CREAM = '#F4EEE2';

export const DESK_Y = 880;
export const W = 704;
export const H = 1280;

export const stopQ = (frame: number, hold = 3) => Math.floor(frame / hold) * hold;
export const wobble = (q: number) => Math.sin(q / 7) * 0.8;

export const Box: React.FC<{
  x: number; y: number; w: number; h: number; color?: string; r?: number;
  style?: React.CSSProperties;
}> = ({ x, y, w, h, color = CARD, r = 6, style }) => (
  <div style={{
    position: 'absolute', left: x, top: y, width: w, height: h,
    background: color, borderRadius: r,
    boxShadow: 'inset 0 0 0 3px rgba(58,42,24,0.25), 0 6px 0 rgba(58,42,24,0.18)',
    ...style,
  }} />
);

export const Camera: React.FC<{
  frame: number; zoom: number; cx?: number; cy?: number; children: React.ReactNode;
}> = ({ frame, zoom, cx = W / 2, cy = H / 2, children }) => (
  <AbsoluteFill style={{ background: BG, overflow: 'hidden' }}>
    <AbsoluteFill style={{
      transform: `scale(${zoom})`,
      transformOrigin: `${cx}px ${cy}px`,
      rotate: `${wobble(stopQ(frame)) * 0.15}deg`,
    }}>
      {children}
    </AbsoluteFill>
  </AbsoluteFill>
);

// Ravi — parameterised for expression and gaze. Head top at y=510 abs.
export const Ravi: React.FC<{
  mood: 'happy' | 'neutral' | 'worried' | 'relieved';
  lookAt: 'phone' | 'monitor' | 'camera';
  armRaise?: number; // 0..1 thumb-up raise
}> = ({ mood, lookAt, armRaise = 0 }) => {
  const eyeDx = lookAt === 'monitor' ? -6 : lookAt === 'phone' ? 8 : 0;
  const eyeDy = lookAt === 'camera' ? -3 : 3;
  return (
    <div style={{ position: 'absolute', left: 50, top: 510, width: 260, height: 400,
      transformOrigin: 'bottom center' }}>
      <Box x={50} y={0} w={160} h={150} color={CARD} r={10} />
      <div style={{ position: 'absolute', left: 40, top: -18, width: 180, height: 50 }}>
        {[0,1,2,3,4,5,6].map(i => (
          <div key={i} style={{
            position: 'absolute', left: i * 26, top: (i % 2) * 8,
            width: 24, height: 42 + (i % 3) * 10,
            background: '#1C1710', borderRadius: '4px 4px 0 0',
            transform: `rotate(${(i - 3) * 4}deg)`,
          }} />
        ))}
      </div>
      {/* eyes */}
      <div style={{ position: 'absolute', left: 88 + eyeDx, top: 62 + eyeDy }}>
        <div style={{ width: 14, height: 14, background: INK, borderRadius: '50%', display: 'inline-block', marginLeft: 4 }} />
        <div style={{ width: 14, height: 14, background: INK, borderRadius: '50%', display: 'inline-block', marginLeft: 26 }} />
      </div>
      {/* mouth by mood */}
      {mood === 'worried' && (
        <div style={{ position: 'absolute', left: 100, top: 112, width: 44, height: 18,
          border: '4px solid transparent', borderTopColor: INK, borderRadius: '50%' }} />
      )}
      {(mood === 'happy' || mood === 'relieved') && (
        <div style={{ position: 'absolute', left: 102, top: 104, width: 40, height: 12,
          borderBottom: `4px solid ${INK}`, borderRadius: '50%' }} />
      )}
      {mood === 'neutral' && (
        <div style={{ position: 'absolute', left: 104, top: 110, width: 36, height: 4,
          background: INK, borderRadius: 2 }} />
      )}
      {/* torso + arms (torso tucks below desk line; desk occludes) */}
      <Box x={30} y={150} w={200} h={250} color={BLUE} r={14} />
      <Box x={8} y={185} w={44} h={150} color={CARD} r={10} />
      <Box x={218} y={185} w={44} h={150} color={CARD} r={10} />
      {/* raised forearm: ELBOW-BENT — short box angled up from the shoulder side,
          never a full-length rotating plank (AK catch 2026-09-08) */}
      {armRaise > 0.05 && (
        <div style={{ position: 'absolute', left: 246, top: 168 - armRaise * 12,
          width: 42, height: 112,
          transform: `rotate(${-18 - armRaise * 9}deg)`, transformOrigin: 'bottom left' }}>
          <Box x={0} y={0} w={42} h={112} color={CARD} r={10} />
          <Box x={11} y={-22} w={20} h={30} color={CARD} r={6} />
        </div>
      )}
    </div>
  );
};

// Desk — drawn AFTER character so it occludes his lower torso.
export const Desk: React.FC = () => (
  <>
    <Box x={-40} y={DESK_Y} w={784} h={40} color={CARD_DARK} r={4} />
    <Box x={-40} y={DESK_Y + 40} w={784} h={360} color={CARD_DEEP} r={0} />
  </>
);

// Monitor standing on the desk, live ticker prop.
export const Monitor: React.FC<{ nifty: number; chg: string; red?: boolean; mode?: 'nifty' | 'portfolio'; progress?: number }> =
  ({ nifty, chg, red = true, mode = 'nifty', progress = 1 }) => (
  <>
    <Box x={400} y={DESK_Y - 200} w={300} h={200} color={CARD} r={8} />
    <Box x={420} y={DESK_Y - 180} w={260} h={140} color="#1A1410" r={4} />
    {mode === 'portfolio' ? (
      <div style={{ position: 'absolute', left: 435, top: DESK_Y - 165, width: 230 }}>
        <div style={{ fontFamily: 'monospace', fontSize: 13, color: GREEN, opacity: 0.8, marginBottom: 6 }}>MY MONEY</div>
        <svg width={230} height={80} viewBox="0 0 230 80">
          <path d={(() => {
            const pts = Array.from({ length: 8 }, (_, i) => {
              const t = i / 7;
              return (10 + t * 210).toFixed(1) + ',' + (72 - Math.pow(t, 1.6) * 58).toFixed(1);
            });
            return 'M' + pts.join(' L');
          })()} fill="none" stroke="#2E8B57" strokeWidth={5} strokeLinecap="round" />
          <circle cx={220} cy={14} r={6} fill="#2E8B57" />
          <line x1={8} y1={74} x2={222} y2={74} stroke={GREEN} strokeWidth={2} opacity={0.35} />
        </svg>
        <div style={{ fontFamily: 'monospace', fontSize: 17, fontWeight: 'bold', color: GREEN, marginTop: 4 }}>₹50,000 SAVED</div>
      </div>
    ) : (
    <div style={{ position: 'absolute', left: 435, top: DESK_Y - 165, width: 230,
      fontFamily: 'monospace', fontSize: 22, color: GREEN, lineHeight: 1.4 }}>
      {(globalThis as any).__NUMBERS__?.asset || 'NIFTY'} {Math.round(nifty).toLocaleString('en-IN')}<br />
      <span style={{ color: red ? RED : GREEN, fontWeight: 'bold' }}>{chg}</span>
    </div>
    )}
    <Box x={520} y={DESK_Y - 18} w={60} h={18} color={CARD_DEEP} r={3} />
  </>
);

// Phone in his hand (right side), value prop.
export const Phone: React.FC<{ value: string; green?: boolean; sub?: string }> =
  ({ value, green = false, sub }) => (
  <>
    <Box x={230} y={DESK_Y - 150} w={90} h={150} color={INK} r={10} />
    <Box x={238} y={DESK_Y - 140} w={74} h={110} color={green ? GREEN : '#E8C27A'} r={4} />
    <div style={{ position: 'absolute', left: 234, top: DESK_Y - 115, width: 82,
      textAlign: 'center', fontFamily: 'monospace', fontSize: 16, color: '#1A1410' }}>
      {value}
      {sub && <div style={{ fontSize: 11, marginTop: 6 }}>{sub}</div>}
    </div>
  </>
);

// Wall calendar (on the WALL), highlight week option.
// Coffee cup ON the desk.
// Stamped rule card (drops in with a little overshoot).
// Big centered kicker text (word wrap safe).
// pass, wall calendar must agree). month: 'SEP'|'NOV'|'JAN'; highlightRow 0-3.
const CAL_GRIDS: Record<string, string[]> = {
  SEP: ['M T W T F S S', '1  2  3  4  5  6  7', '8  9 10 11 12 13 14',
        '15 16 17 18 19 20 21'],
  NOV: ['M T W T F S S', '3  4  5  6  7  8  9', '10 11 12 13 14 15 16',
        '17 18 19 20 21 22 23'],
  JAN: ['M T W T F S S', '5  6  7  8  9 10 11', '12 13 14 15 16 17 18',
        '19 20 21 22 23 24 25'],
};
export const Calendar: React.FC<{ highlight?: boolean; month?: string; highlightRow?: number }> =
  ({ highlight = false, month = 'SEP', highlightRow = 3 }) => {
  const grid = CAL_GRIDS[month] || CAL_GRIDS.SEP;
  return (
    <>
      <Box x={480} y={80} w={140} h={170} color={CREAM} r={6} />
      <div style={{ position: 'absolute', left: 480, top: 80, width: 140, height: 170,
        padding: 12, fontFamily: 'monospace', color: INK }}>
        <div style={{ fontSize: 18, fontWeight: 'bold', marginBottom: 8 }}>{month}</div>
        <div style={{ fontSize: 11, lineHeight: 1.7, opacity: 0.75 }}>
          {grid.map((row, i) => (
            <div key={i} style={{
              background: highlight && i === highlightRow ? GOLD : 'transparent',
              borderRadius: 3, width: 'fit-content',
            }}>{row}</div>
          ))}
        </div>
      </div>
    </>
  );
};

// Coffee cup ON the desk.
export const Cup: React.FC = () => (
  <>
    <Box x={150} y={DESK_Y - 60} w={70} h={60} color={CREAM} r={8} />
    <Box x={168} y={DESK_Y - 74} w={34} h={16} color="#E8C27A" r={4} />
  </>
);

// Stamped rule card (drops in with a little overshoot).
export const RuleCard: React.FC<{
  appearFrame: number; frame: number; y: number; title: string; body: string; accent: string;
}> = ({ appearFrame, frame, y, title, body, accent }) => {
  if (frame < appearFrame) return null;
  const t = frame - appearFrame;
  const drop = interpolate(t, [0, 8], [-80, 0], {
    extrapolateRight: 'clamp', easing: Easing.out(Easing.back(2)),
  });
  return (
    <div style={{ position: 'absolute', left: 92, top: y + drop, width: 520,
      background: CREAM, borderRadius: 10, padding: '18px 22px',
      boxShadow: 'inset 0 0 0 3px rgba(58,42,24,0.25), 0 8px 0 rgba(58,42,24,0.2)' }}>
      <div style={{ fontFamily: 'monospace', fontSize: 26, fontWeight: 'bold', color: accent }}>
        {title}
      </div>
      <div style={{ fontFamily: 'monospace', fontSize: 17, color: INK, marginTop: 6, lineHeight: 1.45 }}>
        {body}
      </div>
    </div>
  );
};

// Big centered kicker text (word wrap safe).
export const Kicker: React.FC<{ text: string; y: number; color?: string }> =
  ({ text, y, color = CREAM }) => (
  <div style={{ position: 'absolute', left: 40, top: y, width: 624, textAlign: 'center',
    fontFamily: 'monospace', fontSize: 34, fontWeight: 'bold', color,
    textShadow: '0 3px 0 rgba(58,42,24,0.35)', lineHeight: 1.35 }}>
    {text}
  </div>
);
