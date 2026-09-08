import { registerRoot, Composition } from 'remotion';
import React from 'react';
import { CardboardRavi } from './CardboardRavi';
import { RaviStory } from './RaviStory';

const fps = 30;
// Real scene plan from VO durations + 0.4s pad (scene_plan.json, 2026-09-08)
const PLAN = [
  { frames: 350 }, { frames: 315 }, { frames: 264 },
  { frames: 358 }, { frames: 514 }, { frames: 239 }, { frames: 479 },
];
const SCENES = [
  'ravi_desk_calm', 'market_crash_monitor', 'phone_portfolio_drop',
  'panic_vs_world', 'rule_cards', 'time_recovery', 'phone_recovery_cta',
];
let acc = 0;
const story = PLAN.map((p, i) => {
  const start = acc;
  acc += p.frames;
  return { start, frames: p.frames, scene: SCENES[i] };
});
const TOTAL = acc;

const RaviStoryWrapper: React.FC = () => {
  (globalThis as any).__STORY__ = story;
  (globalThis as any).__DURATION__ = TOTAL;
  return <RaviStory />;
};

const RaviRootUnused = () => {
  return (
    <>
      <Composition
        id="CardboardRavi"
        component={CardboardRavi}
        durationInFrames={120}
        fps={30}
        width={704}
        height={1280}
      />
      <Composition
        id="RaviStory"
        component={RaviStoryWrapper}
        durationInFrames={TOTAL}
        fps={fps}
        width={704}
        height={1280}
      />
    </>
  );
};

const PLAN2 = [
  { frames: 286 }, { frames: 273 }, { frames: 310 },
  { frames: 468 }, { frames: 349 }, { frames: 370 },
];
const SCENES2 = [
  'ravi_desk_calm', 'market_crash_monitor', 'panic_vs_world',
  'rule_cards', 'time_recovery', 'phone_recovery_cta',
];
let acc2 = 0;
const story2 = PLAN2.map((p, i) => {
  const start = acc2;
  acc2 += p.frames;
  return { start, frames: p.frames, scene: SCENES2[i] };
});
const TOTAL2 = acc2;

const ArjunStoryWrapper: React.FC = () => {
  (globalThis as any).__STORY__ = story2;
  (globalThis as any).__DURATION__ = TOTAL2;
  (globalThis as any).__VARIANT__ = {
    scene: 'bedroom_night', cam: 'pan_down',
    skin: '#8D5524',
    shirt: '#0F7B6C',           // teal hoodie
    hairStyle: 'spiky',
    hairColor: '#0E0E0E',
    glasses: true,
  };
  (globalThis as any).__STORYTEXT__ = {
    b1: { kicker: "₹1,00,000 into Bitcoin", sub: "First job. Bengaluru. Age 24." },
    b2: { kicker: "-28.8% in 7 weeks", sub: "78,00,000 → 55,53,204" },
    b3: { kicker: "THE WIDER PICTURE",
      comments: ["sell before it goes to zero!!", "crypto is dead bro",
                 "take your money out NOW", "it will never recover"],
      app_counter: "App opens today: 40" },
    b4: { kicker: "3 RULES HE FOLLOWED", rules: [
        ["RULE 1 — THE 30% TEST", "Only invest what you can watch drop 30%."],
        ["RULE 2 — A 10-YEAR BET", "A ten-year bet, not a ten-day bet. Zoom out."],
        ["RULE 3 — CHECK ONCE A DAY", "Forty opens a day is panic, not investing."]] },
    b5: { kicker: "HE DID NOTHING", sub: "That was the whole move." },
    b6: { kicker: "STILL DOWN 5% FROM ENTRY",
      sub: "Panic sells at the bottom. Patience gets paid at the top.",
      cta: "FOLLOW FOR THE NEXT STORY" },
  };
  (globalThis as any).__NUMBERS__ = {
    startValue: 100000, lowValue: 71230, nowValue: 95261,
    startIndex: 7796196, lowIndex: 5553204, nowIndex: 7426772,
    asset: 'BTC', dropPct: '-28.8%', recoveryPct: '+33.7%', vsEntry: '-4.7%',
    calmIndex: 7796196, calmPct: '+2.1%',
    cards: [
      { t: 'BITCOIN', v: '▼ -28.8%' },
      { t: 'GOLD', v: '▼ -11.6%' },
      { t: 'NIFTY 50', v: '▼ -3.3%' },
    ],
        cameraZoomCrash: 1.28, cameraCxCrash: 480,
    phone: { ravi_desk_calm: 100000, market_crash_monitor: 71230,
             panic_vs_world: 71230, rule_cards: 71230 },
  };
  return <RaviStory />;
};

export const RemotionRoot = () => {
  return (
    <>
      <Composition
        id="CardboardRavi"
        component={CardboardRavi}
        durationInFrames={120}
        fps={30}
        width={704}
        height={1280}
      />
      <Composition
        id="RaviStory"
        component={RaviStoryWrapper}
        durationInFrames={TOTAL}
        fps={fps}
        width={704}
        height={1280}
      />
      <Composition
        id="ArjunStory"
        component={ArjunStoryWrapper}
        durationInFrames={TOTAL2}
        fps={fps}
        width={704}
        height={1280}
      />
    </>
  );
};

registerRoot(RemotionRoot);
