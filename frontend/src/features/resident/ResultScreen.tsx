import { Button, CellList, CellSimple, Typography } from '@maxhub/max-ui';
import { Link } from 'react-router-dom';
import type { Ticket, UrgencyLevel } from '../../shared/api/types';
import { StatusBadge, UrgencyBadge } from '../../shared/StatusBadge';
import { statusLabel } from '../../shared/labels';

const SLA: Record<UrgencyLevel, string> = {
  HIGH: 'Ожидаемая реакция: в ближайшее время (аварийный приоритет)',
  MEDIUM: 'Ожидаемая реакция: в течение рабочего дня',
  LOW: 'Ожидаемая реакция: в течение 1–2 рабочих дней',
};

type Props = {
  ticket: Ticket;
};

export function ResultScreen({ ticket }: Props) {
  return (
    <div className="page-stack">
      <Typography.Headline>Заявка создана</Typography.Headline>
      <div className="status-row">
        <StatusBadge status={ticket.status} />
        <UrgencyBadge level={ticket.urgencyLevel} />
      </div>
      <CellList mode="island">
        <CellSimple title="Номер" subtitle={ticket.id} />
        <CellSimple title="Адрес" subtitle={ticket.addressSnapshot} />
        <CellSimple title="Суть" subtitle={ticket.summaryText} />
        <CellSimple
          title="Статус"
          subtitle={statusLabel(ticket.status)}
          after={<StatusBadge status={ticket.status} />}
        />
        <CellSimple title="Приоритет" after={<UrgencyBadge level={ticket.urgencyLevel} />} />
      </CellList>
      <Typography.Body>{ticket.recommendationTextSnapshot}</Typography.Body>
      <Typography.Body>{SLA[ticket.urgencyLevel]}</Typography.Body>
      <Button variant="primary" stretched asChild>
        <Link to="/resident/tickets">Мои заявки</Link>
      </Button>
      <Button variant="secondary" stretched asChild>
        <Link to="/resident">На главную</Link>
      </Button>
    </div>
  );
}
