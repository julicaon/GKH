import { useCallback, useEffect, useState } from 'react';
import {
  Button,
  CellList,
  CellSimple,
  Spinner,
  Textarea,
  Typography,
} from '@maxhub/max-ui';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { cancelTicket, getTicket, listTickets } from '../../shared/api/tickets';
import type { Ticket } from '../../shared/api/types';
import { useDevShellOverrides } from '../../dev/DevShell';
import { StatusBadge, UrgencyBadge } from '../../shared/StatusBadge';
import { statusLabel } from '../../shared/labels';

const canCancel = (status: Ticket['status']) => status !== 'CANCELLED_BY_RESIDENT';

export function MyTickets() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { userId } = useDevShellOverrides();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [detail, setDetail] = useState<Ticket | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [cancelForId, setCancelForId] = useState<string | null>(null);
  const [cancelReason, setCancelReason] = useState('');

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

  const startCancel = (ticketId: string) => {
    setCancelForId(ticketId);
    setCancelReason('');
    setError(null);
  };

  const confirmCancel = async () => {
    if (!cancelForId) return;
    const reason = cancelReason.trim();
    if (!reason) {
      setError('Укажите причину отмены');
      return;
    }
    setBusyId(cancelForId);
    try {
      await cancelTicket(cancelForId, userId, reason);
      setCancelForId(null);
      setCancelReason('');
      await reload();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Не удалось отменить');
    } finally {
      setBusyId(null);
    }
  };

  const cancelForm = cancelForId ? (
    <div className="page-stack cancel-panel">
      <Typography.Title>Почему отменяете?</Typography.Title>
      <Textarea
        rows={3}
        placeholder="Например: проблема решилась сама / ошибка в заявке"
        value={cancelReason}
        onChange={(e) => setCancelReason(e.target.value)}
      />
      <div className="row">
        <Button
          variant="secondary"
          onClick={() => {
            setCancelForId(null);
            setCancelReason('');
          }}
        >
          Назад
        </Button>
        <Button
          variant="destructive"
          loading={busyId === cancelForId}
          disabled={!cancelReason.trim()}
          onClick={() => void confirmCancel()}
        >
          Подтвердить отмену
        </Button>
      </div>
    </div>
  ) : null;

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
        <div className="status-row">
          <StatusBadge status={detail.status} />
          <UrgencyBadge level={detail.urgencyLevel} />
        </div>
        <CellList mode="island">
          <CellSimple title="Адрес" subtitle={detail.addressSnapshot} />
          <CellSimple title="Суть" subtitle={detail.summaryText} />
          <CellSimple
            title="Статус"
            subtitle={statusLabel(detail.status)}
            after={<StatusBadge status={detail.status} />}
          />
          <CellSimple title="Приоритет" after={<UrgencyBadge level={detail.urgencyLevel} />} />
          <CellSimple title="Рекомендация" subtitle={detail.recommendationTextSnapshot} />
          {detail.assigneeSpecialistName && (
            <CellSimple title="Мастер" subtitle={detail.assigneeSpecialistName} />
          )}
          {detail.cancelReason && (
            <CellSimple title="Причина отмены" subtitle={detail.cancelReason} />
          )}
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
        {cancelForm}
        {!cancelForId && canCancel(detail.status) && (
          <Button
            variant="destructive"
            stretched
            onClick={() => startCancel(detail.id)}
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
            subtitle={`${statusLabel(t.status)} · ${t.addressSnapshot}${
              t.assigneeSpecialistName ? ` · ${t.assigneeSpecialistName}` : ''
            }`}
            showChevron
            onClick={() => navigate(`/resident/tickets/${t.id}`)}
            after={
              <span className="status-row">
                {t.urgencyLevel === 'HIGH' && <UrgencyBadge level={t.urgencyLevel} />}
                <StatusBadge status={t.status} />
              </span>
            }
          />
        ))}
      </CellList>
      {cancelForm}
      {!cancelForId &&
        tickets
          .filter((t) => canCancel(t.status))
          .map((t) => (
            <Button
              key={`cancel-${t.id}`}
              variant="destructive"
              onClick={() => startCancel(t.id)}
            >
              Отменить: {t.summaryText.slice(0, 40)}
            </Button>
          ))}
    </div>
  );
}
