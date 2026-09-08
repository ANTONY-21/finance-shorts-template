import { registerRoot, Composition } from 'remotion';
import { CardboardRavi } from './CardboardRavi';

export const RemotionRoot = () => {
  return (
    <Composition
      id="CardboardRavi"
      component={CardboardRavi}
      durationInFrames={120}
      fps={30}
      width={704}
      height={1280}
    />
  );
};

registerRoot(RemotionRoot);
