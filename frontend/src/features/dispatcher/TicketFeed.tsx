import { useCallback, useEffect, useState } from 'react';
import { Button, CellList, CellSimple, Spinner, Typography } from '@maxhub/max-ui';
import { Link, useNavigate } from 'react-router-dom';
import { logout } from '../../shared/api/auth';
import { listTickets } from '../../shared/api/tickets';
import type { Ticket } from '../../shared/api/types';
import { StatusBadge, UrgencyBadge } from '../../shared/StatusBadge';
import { statusLabel } from '../../shared/labels';

export function TicketFeed() {
  const navigate = useNavigate();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setTickets(await listTickets('org'));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Ошибка ленты');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void reload();
  }, [reload]);

  return (
    <div className="page page-stack">
      <div className="row">
        <Typography.Headline>Лента заявок</Typography.Headline>
      </div>
      <div className="row">
        <Button variant="secondary" asChild>
          <Link to="/dispatcher/settings">Настройки</Link>
        </Button>
        <Button
          variant="ghost"
          onClick={() => {
            logout();
            navigate('/dispatcher/login');
          }}
        >
          Выйти
        </Button>
        <Button variant="ghost" onClick={() => void reload()}>
          Обновить
        </Button>
      </div>

      {loading && (
        <div className="center">
          <Spinner size={32} />
        </div>
      )}
      {error && <Typography.Body>{error}</Typography.Body>}
      {!loading && !tickets.length && <Typography.Body>Нет заявок</Typography.Body>}

      <CellList mode="island">
        {tickets.map((t) => (
          <CellSimple
            key={t.id}
            title={t.summaryText}
            subtitle={`${statusLabel(t.status)} · ${t.addressSnapshot}`}
            showChevron
            onClick={() => navigate(`/dispatcher/tickets/${t.id}`)}
            after={
              <span className="status-row">
                {t.urgencyLevel === 'HIGH' && <UrgencyBadge level={t.urgencyLevel} />}
                <StatusBadge status={t.status} />
              </span>
            }
          />
        ))}
      </CellList>
    </div>
  );
}
