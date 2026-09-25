import { MaxUI } from '@maxhub/max-ui';
import { BrowserRouter } from 'react-router-dom';
import { DevShell, useDevShellOverrides } from '../dev/DevShell';
import { AppRouter } from './router';

function AppInner() {
  const { platform, colorScheme } = useDevShellOverrides();
  return (
    <MaxUI platform={platform} colorScheme={colorScheme}>
      <DevShell>
        <AppRouter />
      </DevShell>
    </MaxUI>
  );
}

export function App() {
  return (
    <BrowserRouter>
      <AppInner />
    </BrowserRouter>
  );
}
