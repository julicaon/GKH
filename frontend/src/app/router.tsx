import type { ReactNode } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { ResidentHome } from '../features/resident/ResidentHome';
import { CreateTicketFlow } from '../features/resident/CreateTicketFlow';
import { MyTickets } from '../features/resident/MyTickets';
import { Login } from '../features/dispatcher/Login';
import { TicketFeed } from '../features/dispatcher/TicketFeed';
import { TicketCard } from '../features/dispatcher/TicketCard';
import { Settings } from '../features/dispatcher/Settings';
import { getStoredToken } from '../shared/api/client';

function RequireDispatcher({ children }: { children: ReactNode }) {
  if (!getStoredToken()) {
    return <Navigate to="/dispatcher/login" replace />;
  }
  return <>{children}</>;
}

export function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<ResidentHome />} />
      <Route path="/resident" element={<ResidentHome />} />
      <Route path="/resident/create" element={<CreateTicketFlow />} />
      <Route path="/resident/tickets" element={<MyTickets />} />
      <Route path="/resident/tickets/:id" element={<MyTickets />} />

      <Route path="/dispatcher/login" element={<Login />} />
      <Route
        path="/dispatcher"
        element={
          <RequireDispatcher>
            <TicketFeed />
          </RequireDispatcher>
        }
      />
      <Route
        path="/dispatcher/tickets/:id"
        element={
          <RequireDispatcher>
            <TicketCard />
          </RequireDispatcher>
        }
      />
      <Route
        path="/dispatcher/settings"
        element={
          <RequireDispatcher>
            <Settings />
          </RequireDispatcher>
        }
      />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
