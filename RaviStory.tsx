import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from 'remotion';
import {
  CARD, CARD_DARK, CARD_DEEP, INK, BG, BLUE, GREEN, RED, GOLD, CREAM,
  DESK_Y, W, H, stopQ, wobble, Box, Camera, Ravi, Desk, Monitor, Phone,
  Calendar, Cup, RuleCard, Kicker,
} from './scenes/shared';

// Ravi's First Crash — 7 scenes in one composition. Beat boundaries come from
// scene_plan.json (frame offsets baked by the build script into STORY below).

export interface StoryBeat {
  start: number; frames: number; scene: string;
}

const getStory = (): StoryBeat[] => (globalThis as any).__STORY__ || [];
const getDuration = (): number => (globalThis as any).__DURATION__ || 1449;

const beatAt = (frame: number): StoryBeat => {
  const story = getStory();
  return story.find(b => frame >= b.start && frame < b.start + b.frames) || story[story.length - 1];
};

const localFrame = (frame: number, b: StoryBeat) => frame - b.start;

export const RaviStory: React.FC = () => {
const N = (globalThis as any).__NUMBERS__ || {
  startValue: 50000, lowValue: 48165, nowValue: 53286,
  startIndex: 23682, lowIndex: 23682, nowIndex: 26200,
  asset: 'NIFTY', dropPct: '-3.67%', recoveryPct: '+10.6%', vsEntry: '+6.57%',
  calmIndex: 24584, calmPct: '+0.21%',
  recoveryFrames: 80,
  cards: [
    { t: 'NIFTY 50', v: '▼ -3.67%', c: 'RED' },
    { t: 'BANK NIFTY', v: '▼ -1.25%', c: '#E8A54A' },
    { t: 'S&P 500', v: '▼ -0.06%', c: 'GREEN' },
  ],
};

  const frame = useCurrentFrame();
  const b = beatAt(frame);
  const lf = localFrame(frame, b);
  const q = stopQ(frame);

  // default camera
  let zoom = interpolate(frame, [0, getDuration()], [1.0, 1.1], { extrapolateRight: 'clamp' });
  let cx = W / 2, cy = H / 2;

  let mood: any = 'neutral', look: any = 'phone', arm = 0;

  // per-scene camera + props
  if (b.scene === 'ravi_desk_calm') {
    mood = 'happy'; look = 'camera';
  } else if (b.scene === 'market_crash_monitor') {
    // push in to monitor
    const p = interpolate(lf, [10, 45], [1.0, 1.45], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic) });
    zoom = zoom * (N.cameraZoomCrash || p); cx = N.cameraCxCrash || 550; cy = 760;
    mood = 'worried'; look = 'monitor';
  } else if (b.scene === 'phone_portfolio_drop') {
    const p = interpolate(lf, [5, 35], [1.0, 1.6], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic) });
    zoom = zoom * p; cx = 275; cy = 780;
    mood = 'worried'; look = 'phone';
  } else if (b.scene === 'panic_vs_world') {
    mood = 'worried'; look = 'monitor';
  } else if (b.scene === 'rule_cards') {
    mood = 'neutral'; look = 'camera';
  } else if (b.scene === 'time_recovery') {
    mood = lf > 60 ? 'relieved' : 'neutral'; look = 'monitor';
  } else if (b.scene === 'phone_recovery_cta') {
    mood = 'happy'; look = 'camera';
    arm = interpolate(lf, [30, 50], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  }

// story numbers — injected by composition wrapper (Ravi defaults, Arjun overrides)
  // values
  // STORY-LOGIC state machine (AK catch: beat 1 is CALM — showing the crash there
// spoils the reveal). Monitor mirrors the story beat, each state internally consistent:
//   calm: 24,584 ▲ +0.21% green (pre-crash level: 24,584 x (1-0.0367) = 23,682 exact)
//   crash scenes: 23,682 ▼ -3.67% red
//   recovery: 23,682 -> 26,200 ticking ▲ +10.6% green
const calmNifty = N.calmIndex || 24584;
const nifty = b.scene === 'ravi_desk_calm'
    ? calmNifty
    : (b.scene === 'time_recovery' || b.scene === 'phone_recovery_cta')
    ? interpolate(lf, [0, N.recoveryFrames || 80], [N.lowIndex, N.nowIndex], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })
    : N.lowIndex;
  const chg = b.scene === 'ravi_desk_calm' ? ('▲ ' + (N.calmPct || '+0.21%'))
    : (b.scene === 'time_recovery' || b.scene === 'phone_recovery_cta') ? ('▲ ' + N.recoveryPct) : ('▼ ' + N.dropPct);
  const red = b.scene !== 'ravi_desk_calm' && b.scene !== 'time_recovery' && b.scene !== 'phone_recovery_cta';

  return (
    <Camera frame={frame} zoom={zoom} cx={cx} cy={cy}>
      {/* wall + calendar */}
      {(b.scene === 'ravi_desk_calm' || b.scene === 'market_crash_monitor' || b.scene === 'phone_portfolio_drop' || b.scene === 'panic_vs_world') &&
        <Calendar highlight={b.scene === 'market_crash_monitor' || b.scene === 'phone_portfolio_drop'} month="SEP" highlightRow={3} />}
      {b.scene === 'time_recovery' && <Calendar highlight month="NOV" highlightRow={1} />}
      {b.scene === 'phone_recovery_cta' && <Calendar month="JAN" highlightRow={0} />}

      {/* scene-specific overlays */}
      {(b.scene === 'ravi_desk_calm') && <Kicker text="₹50,000 in an index fund" y={980} />}
      {(b.scene === 'panic_vs_world') && (
        <>
          <Kicker text="THE WIDER PICTURE" y={130} color={GOLD} />
          {[
            { t: N.cards[0].t, v: N.cards[0].v, c: N.cards[0].c === 'RED' ? RED : N.cards[0].c, y: 210 },
            { t: N.cards[1].t, v: N.cards[1].v, c: N.cards[1].c === 'GREEN' ? GREEN : N.cards[1].c, y: 305 },
            { t: N.cards[2].t, v: N.cards[2].v, c: N.cards[2].c === 'GREEN' ? GREEN : N.cards[2].c, y: 400 },
          ].map((r, i) => (
            <RuleCard key={i} appearFrame={b.start + 10 + i * 15} frame={frame}
              y={r.y} title={r.t + '  ' + r.v} body=""
              accent={r.c} />
          ))}
        </>
      )}
      {(b.scene === 'rule_cards') && (
        <>
          <Kicker text="3 RULES HE LEARNED" y={100} color={GOLD} />
          <RuleCard appearFrame={b.start + 8} frame={frame} y={150} accent={GREEN}
            title="RULE 1 — DIPS ARE NORMAL"
            body="The index has fallen 10%+ many times. It recovered every time." />
          <RuleCard appearFrame={b.start + 50} frame={frame} y={278} accent={GOLD}
            title="RULE 2 — 2500 COMPANIES"
            body="His money is spread across the whole index, not one stock." />
          <RuleCard appearFrame={b.start + 92} frame={frame} y={405} accent={RED}
            title="RULE 3 — NEVER PANIC-SELL"
            body="Panic-selling makes the loss real." />
        </>
      )}
      {(b.scene === 'phone_recovery_cta') && (
        <Kicker text="FOLLOW FOR THE NEXT STORY" y={1010} color={GOLD} />
      )}

      {/* character (before desk) */}
      <Ravi mood={mood} lookAt={look} armRaise={arm} />

      {/* desk occludes torso */}
      <Desk />
      <Cup />

      {/* props on desk */}
      <Monitor nifty={nifty} chg={chg} red={red}
        mode={b.scene === 'ravi_desk_calm' ? 'portfolio' : 'nifty'} />
      <Phone
        value={N.phone && N.phone[b.scene] !== undefined
          ? '₹' + (N.phone[b.scene] as number).toLocaleString('en-IN')
          : b.scene === 'ravi_desk_calm' || b.scene === 'market_crash_monitor' ? '₹' + N.startValue.toLocaleString('en-IN')
          : b.scene === 'time_recovery'
            ? '₹' + Math.round(N.lowValue * (nifty / N.lowIndex)).toLocaleString('en-IN')
          : b.scene === 'phone_recovery_cta'
            ? '₹' + N.nowValue.toLocaleString('en-IN')
          : '₹' + N.lowValue.toLocaleString('en-IN')}
        green={b.scene === 'phone_recovery_cta'}
        sub={b.scene === 'phone_portfolio_drop' ? '▼ ₹1,835' : undefined}
      />
    </Camera>
  );
};
