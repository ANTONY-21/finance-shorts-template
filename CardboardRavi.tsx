import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate } from 'remotion';

// Cardboard Ravi v4 — ground plane FIXED. Everything sits ON the desk, character
// stands BEHIND it (desk occludes his lower torso). Z-order: wall -> calendar ->
// character -> desk -> monitor -> phone -> cup. QCA-passed rules: no object props,
// real numbers, distinct portfolio vs index, clear expressions.

const CARD = '#C8A165';
const CARD_DARK = '#A5804A';
const CARD_DEEP = '#8F6B3C';
const INK = '#3A2A18';
const BG = '#E8D9BE';
const BLUE = '#2B3A67';

const Box: React.FC<{
  x: number; y: number; w: number; h: number; color?: string; r?: number;
  border?: string;
}> = ({ x, y, w, h, color = CARD, r = 6, border }) => (
  <div style={{
    position: 'absolute', left: x, top: y, width: w, height: h,
    background: color, borderRadius: r,
    boxShadow: 'inset 0 0 0 3px rgba(58,42,24,0.25), 0 6px 0 rgba(58,42,24,0.18)',
    border: border || 'none',
  }} />
);

export const CardboardRavi: React.FC = () => {
  const frame = useCurrentFrame();
  const q = Math.floor(frame / 3) * 3; // 10fps stop-motion holds

  const wobble = Math.sin(q / 7) * 0.8;
  const zoom = interpolate(frame, [0, 120], [1.0, 1.12], {
    extrapolateRight: 'clamp',
  });

  // live index ticker (slight drift within the crash day)
  const price = 23779 - Math.floor(q / 10) * 37;

  // reaction: lean back + tilt head + worried face after frame 40
  const tilt = interpolate(q, [40, 55], [0, -4], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const eyeY = interpolate(q, [0, 40], [0, 3], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  // GROUND PLANE (fixed): wall ends / desk surface at y=880, desk front 920+.
  const DESK_Y = 880;

  return (
    <AbsoluteFill style={{ background: BG, overflow: 'hidden' }}>
      <AbsoluteFill style={{ transform: `scale(${zoom}) rotate(${wobble * 0.15}deg)` }}>

        {/* wall calendar (on the WALL — above desk line) */}
        <Box x={480} y={80} w={140} h={170} color="#F4EEE2" r={6} />
        <div style={{
          position: 'absolute', left: 480, top: 80, width: 140, height: 170,
          padding: 12, fontFamily: 'monospace', color: INK,
        }}>
          <div style={{ fontSize: 18, fontWeight: 'bold', marginBottom: 8 }}>SEP</div>
          <div style={{ fontSize: 11, lineHeight: 1.7, opacity: 0.75 }}>
            {['M T W T F S S', '1  2  3  4  5  6  7', '8  9 10 11 12 13 14',
              '15 16 17 18 19 20 21'].map((row, i) => (
              <div key={i} style={{
                background: i === 3 ? '#FFD24A' : 'transparent',
                borderRadius: 3, width: 'fit-content',
              }}>{row}</div>
            ))}
          </div>
        </div>

        {/* ===== RAVI — standing BEHIND the desk =====
            container top=510: head 510-660, torso 660-880 (torso bottom = DESK_Y,
            desk is drawn after him and occludes the lowest 20px = grounded look) */}
        <div style={{
          position: 'absolute', left: 50, top: 510, width: 260, height: 380,
          transform: `rotate(${tilt}deg)`, transformOrigin: 'bottom center',
        }}>
          {/* head */}
          <Box x={50} y={0} w={160} h={150} color={CARD} r={10} />
          {/* cut-paper hair */}
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
          {/* eyes look toward the phone (right, downward after the drop) */}
          <div style={{ position: 'absolute', left: 88, top: 62 + eyeY }}>
            <div style={{ width: 14, height: 14, background: INK, borderRadius: '50%', display: 'inline-block', marginLeft: 4 }} />
            <div style={{ width: 14, height: 14, background: INK, borderRadius: '50%', display: 'inline-block', marginLeft: 26 }} />
          </div>
          {/* mouth: smile before the drop, inverted-arc frown after frame 40 */}
          {q >= 40 ? (
            <div style={{
              position: 'absolute', left: 100, top: 112, width: 44, height: 18,
              border: '4px solid transparent', borderTopColor: INK, borderRadius: '50%',
            }} />
          ) : (
            <div style={{
              position: 'absolute', left: 102, top: 104, width: 40, height: 12,
              borderBottom: `4px solid ${INK}`, borderRadius: '50%',
            }} />
          )}
          {/* torso: blue t-shirt, bottom edge tucks BEHIND the desk */}
          <Box x={30} y={150} w={200} h={230} color={BLUE} r={14} />
          {/* arms */}
          <Box x={-6} y={165} w={40} h={150} color={CARD} r={10} />
          <Box x={226} y={165} w={40} h={150} color={CARD} r={10} />
        </div>

        {/* ===== DESK — drawn AFTER character so it occludes his torso bottom ===== */}
        <Box x={-40} y={DESK_Y} w={784} h={40} color={CARD_DARK} r={4} />
        <Box x={-40} y={DESK_Y + 40} w={784} h={360} color={CARD_DEEP} r={0} />

        {/* monitor STANDING ON the desk: 880 - 200 = y 680, bottom sits on DESK_Y */}
        <Box x={400} y={DESK_Y - 200} w={300} h={200} color={CARD} r={8} />
        <Box x={420} y={DESK_Y - 180} w={260} h={140} color="#1A1410" r={4} />
        <div style={{
          position: 'absolute', left: 435, top: DESK_Y - 165, width: 230,
          fontFamily: 'monospace', fontSize: 22, color: '#7EC87E', lineHeight: 1.4,
        }}>
          NIFTY {price.toLocaleString('en-IN')}<br />
          <span style={{ color: '#FF6B5E', fontWeight: 'bold' }}>▼ -3.22%</span>
        </div>
        {/* monitor stand foot ON the desk surface */}
        <Box x={520} y={DESK_Y - 18} w={60} h={18} color={CARD_DEEP} r={3} />

        {/* coffee cup ON the desk: bottom = DESK_Y, real number borderRadius */}
        <Box x={300} y={DESK_Y - 60} w={70} h={60} color="#F4EEE2" r={8} />
        <Box x={318} y={DESK_Y - 74} w={34} h={16} color="#E8C27A" r={4} />

        {/* phone IN his hand: hand at arm bottom (abs ~825), phone held above desk */}
        <Box x={230} y={DESK_Y - 150} w={90} h={150} color={INK} r={10} />
        <Box x={238} y={DESK_Y - 140} w={74} h={110} color="#E8C27A" r={4} />
        <div style={{
          position: 'absolute', left: 238, top: DESK_Y - 110, width: 74,
          textAlign: 'center', fontFamily: 'monospace', fontSize: 17, color: '#1A1410',
        }}>
          ₹48,400
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
