import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Button,
  CellList,
  CellSimple,
  Spinner,
  Typography,
} from '@maxhub/max-ui';
import { Link, useParams } from 'react-router-dom';
import {
  acceptTicket,
  assignTicket,
  completeTicket,
  getTicket,
} from '../../shared/api/tickets';
import { listSpecialists } from '../../shared/api/specialists';
import type { Specialist, Ticket } from '../../shared/api/types';
import { StatusBadge, UrgencyBadge } from '../../shared/StatusBadge';
import { statusLabel } from '../../shared/labels';

function matchesParentSkills(spec: Specialist, parentCategoryId: string): boolean {
  if (!spec.skillTags.length) return true;
  const tags = spec.skillTags.map((t) => t.toLowerCase());
  const parent = parentCategoryId.toLowerCase();
  if (tags.some((t) => parent.includes(t) || t.includes(parent))) return true;
  if (parent.includes('voda') && tags.some((t) => t.includes('вод') || t.includes('протеч'))) return true;
  if (parent.includes('elektro') && tags.some((t) => t.includes('электр') || t.includes('щит'))) return true;
  if (
    parent.includes('podezd') &&
    tags.some((t) => t.includes('двер') || t.includes('домоф') || t.includes('подъезд'))
  ) {
    return true;
  }
  return false;
}

export function TicketCard() {
  const { id } = useParams();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [specialists, setSpecialists] = useState<Specialist[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [selectedSpecialist, setSelectedSpecialist] = useState<string | null>(null);

  const reload = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const [t, specs] = await Promise.all([
        getTicket(id),
        listSpecialists({ activeOnly: true }),
      ]);
      setTicket(t);
      setSpecialists(specs);
      setSelectedSpecialist(t.assigneeSpecialistId ?? specs[0]?.id ?? null);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Ошибка');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const filteredSpecialists = useMemo(() => {
    if (!ticket) return specialists;
    const matched = specialists.filter((s) =>
      matchesParentSkills(s, ticket.parentCategoryId),
    );
    return matched.length ? matched : specialists;
  }, [specialists, ticket]);

  useEffect(() => {
    if (!ticket || ticket.assigneeSpecialistId) return;
    if (
      filteredSpecialists.length &&
      !filteredSpecialists.some((s) => s.id === selectedSpecialist)
    ) {
      setSelectedSpecialist(filteredSpecialists[0].id);
    }
  }, [filteredSpecialists, selectedSpecialist, ticket]);

  const run = async (fn: () => Promise<Ticket>) => {
    setBusy(true);
    setError(null);
    try {
      setTicket(await fn());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Ошибка операции');
    } finally {
      setBusy(false);
    }
  };

  if (loading || !ticket) {
    return (
      <div className="page center">
        {error ? <Typography.Body>{error}</Typography.Body> : <Spinner size={32} />}
      </div>
    );
  }

  return (
    <div className="page page-stack">
      <Button variant="ghost" asChild>
        <Link to="/dispatcher">← Лента</Link>
      </Button>
      <Typography.Headline>Карточка заявки</Typography.Headline>
      {error && <Typography.Body>{error}</Typography.Body>}

      <div className="status-row">
        <StatusBadge status={ticket.status} />
        <UrgencyBadge level={ticket.urgencyLevel} />
      </div>
      <Typography.Body>
        Текущий статус: <strong>{statusLabel(ticket.status)}</strong>
      </Typography.Body>

      <CellList mode="island">
        <CellSimple title="Адрес" subtitle={ticket.addressSnapshot} />
        <CellSimple title="Суть" subtitle={ticket.summaryText} />
        <CellSimple
          title="Статус"
          subtitle={statusLabel(ticket.status)}
          after={<StatusBadge status={ticket.status} />}
        />
        <CellSimple
          title="Приоритет"
          after={<UrgencyBadge level={ticket.urgencyLevel} />}
        />
        <CellSimple title="Рекомендация" subtitle={ticket.recommendationTextSnapshot} />
        {ticket.assigneeSpecialistName && (
          <CellSimple title="Мастер" subtitle={ticket.assigneeSpecialistName} />
        )}
        {ticket.cancelReason && (
          <CellSimple title="Причина отмены" subtitle={ticket.cancelReason} />
        )}
        <CellSimple title="Создана" subtitle={new Date(ticket.createdAt).toLocaleString('ru-RU')} />
      </CellList>

      <Typography.Title>Ответы</Typography.Title>
      <CellList mode="island">
        {ticket.answersSnapshot.map((a) => (
          <CellSimple key={a.questionId} title={a.questionLabel} subtitle={a.optionLabel} />
        ))}
      </CellList>

      {ticket.photoUrl && (
        <>
          <Typography.Title>Фото</Typography.Title>
          <img className="photo-preview" src={ticket.photoUrl} alt="Фото заявки" />
        </>
      )}

      {ticket.status === 'NEW' && (
        <Button
          variant="primary"
          stretched
          loading={busy}
          onClick={() => void run(() => acceptTicket(ticket.id))}
        >
          Принять
        </Button>
      )}

      {(ticket.status === 'ACCEPTED' || ticket.status === 'IN_PROGRESS') && (
        <>
          <Typography.Title>Назначить специалиста</Typography.Title>
          <Typography.Body>
            Сначала показаны мастера с подходящими навыками
          </Typography.Body>
          <CellList mode="island">
            {filteredSpecialists.map((s) => (
              <CellSimple
                key={s.id}
                title={s.fullName}
                subtitle={s.skillTags.join(', ') || '—'}
                onClick={() => setSelectedSpecialist(s.id)}
                after={selectedSpecialist === s.id ? '✓' : undefined}
              />
            ))}
          </CellList>
          <Button
            variant="primary"
            stretched
            loading={busy}
            disabled={!selectedSpecialist}
            onClick={() => {
              if (!selectedSpecialist) return;
              void run(() => assignTicket(ticket.id, selectedSpecialist));
            }}
          >
            Назначить
          </Button>
        </>
      )}

      {ticket.status === 'IN_PROGRESS' && (
        <Button
          variant="primary"
          stretched
          loading={busy}
          onClick={() => void run(() => completeTicket(ticket.id))}
        >
          Завершить
        </Button>
      )}

      {ticket.status === 'DONE' && (
        <Typography.Body>Заявка закрыта — работа выполнена.</Typography.Body>
      )}
      {ticket.status === 'CANCELLED_BY_RESIDENT' && (
        <Typography.Body>Заявка отменена жителем.</Typography.Body>
      )}
    </div>
  );
}
