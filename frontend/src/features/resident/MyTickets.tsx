import { useCallback, useEffect, useState } from 'react';
import { Button, CellList, CellSimple, Spinner, Typography } from '@maxhub/max-ui';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { cancelTicket, getTicket, listTickets } from '../../shared/api/tickets';
import type { Ticket } from '../../shared/api/types';
import { useDevShellOverrides } from '../../dev/DevShell';

const canCancel = (status: Ticket['status']) => status === 'NEW' || status === 'ACCEPTED';

export function MyTickets() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { userId } = useDevShellOverrides();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [detail, setDetail] = useState<Ticket | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      if (id) {
        setDetail(await getTicket(id));
      } else {
        setTickets(await listTickets('resident', { maxUserId: userId }));
        setDetail(null);
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Ошибка загрузки');
    } finally {
      setLoading(false);
    }
  }, [id, userId]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const onCancel = async (ticketId: string) => {
    setBusyId(ticketId);
    try {
      await cancelTicket(ticketId, userId);
      await reload();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Не удалось отменить');
    } finally {
      setBusyId(null);
    }
  };

  if (loading) {
    return (
      <div className="page center">
        <Spinner size={32} />
      </div>
    );
  }

  if (detail) {
    return (
      <div className="page page-stack">
        <Button variant="ghost" onClick={() => navigate('/resident/tickets')}>
          ← К списку
        </Button>
        {error && <Typography.Body>{error}</Typography.Body>}
        <Typography.Headline>Заявка</Typography.Headline>
        <CellList mode="island">
          <CellSimple title="Адрес" subtitle={detail.addressSnapshot} />
          <CellSimple title="Суть" subtitle={detail.summaryText} />
          <CellSimple title="Статус" subtitle={detail.status} />
          <CellSimple
            title="Приоритет"
            subtitle={detail.urgencyLevel}
            after={
              detail.urgencyLevel === 'HIGH' ? (
                <span className="urgency-high">HIGH</span>
              ) : undefined
            }
          />
          <CellSimple title="Рекомендация" subtitle={detail.recommendationTextSnapshot} />
        </CellList>
        {detail.answersSnapshot.map((a) => (
          <CellSimple
            key={a.questionId}
            title={a.questionLabel}
            subtitle={a.optionLabel}
          />
        ))}
        {detail.photoUrl && (
          <img className="photo-preview" src={detail.photoUrl} alt="Фото заявки" />
        )}
        {canCancel(detail.status) && (
          <Button
            variant="destructive"
            stretched
            loading={busyId === detail.id}
            onClick={() => void onCancel(detail.id)}
          >
            Отменить заявку
          </Button>
        )}
      </div>
    );
  }

  return (
    <div className="page page-stack">
      <div className="row">
        <Button variant="ghost" asChild>
          <Link to="/resident">← Главная</Link>
        </Button>
      </div>
      <Typography.Headline>Мои заявки</Typography.Headline>
      {error && <Typography.Body>{error}</Typography.Body>}
      {!tickets.length && <Typography.Body>Заявок пока нет</Typography.Body>}
      <CellList mode="island">
        {tickets.map((t) => (
          <CellSimple
            key={t.id}
            title={t.summaryText}
            subtitle={`${t.status} · ${t.addressSnapshot}`}
            showChevron
            onClick={() => navigate(`/resident/tickets/${t.id}`)}
            after={
              t.urgencyLevel === 'HIGH' ? <span className="urgency-high">HIGH</span> : undefined
            }
          />
        ))}
      </CellList>
      {tickets.map(
        (t) =>
          canCancel(t.status) && (
            <Button
              key={`cancel-${t.id}`}
              variant="destructive"
              loading={busyId === t.id}
              onClick={() => void onCancel(t.id)}
            >
              Отменить: {t.summaryText.slice(0, 40)}
            </Button>
          ),
      )}
    </div>
  );
}
