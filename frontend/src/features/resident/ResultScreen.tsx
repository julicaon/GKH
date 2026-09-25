import { Button, CellList, CellSimple, Typography } from '@maxhub/max-ui';
import { Link } from 'react-router-dom';
import type { Ticket, UrgencyLevel } from '../../shared/api/types';

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
      <CellList mode="island">
        <CellSimple title="Номер" subtitle={ticket.id} />
        <CellSimple title="Адрес" subtitle={ticket.addressSnapshot} />
        <CellSimple title="Суть" subtitle={ticket.summaryText} />
        <CellSimple
          title="Приоритет"
          subtitle={ticket.urgencyLevel}
          after={
            ticket.urgencyLevel === 'HIGH' ? (
              <span className="urgency-high">HIGH</span>
            ) : undefined
          }
        />
        <CellSimple title="Статус" subtitle={ticket.status} />
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
