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
    </>
  );
};

registerRoot(RemotionRoot);
