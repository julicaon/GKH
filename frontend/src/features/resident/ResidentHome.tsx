import { Button, Typography } from '@maxhub/max-ui';
import { Link } from 'react-router-dom';

export function ResidentHome() {
  return (
    <div className="page page-stack">
      <Typography.Headline>Умный город</Typography.Headline>
      <Typography.Body className="muted">Заявки в управляющую компанию</Typography.Body>
      <Button variant="primary" stretched asChild>
        <Link to="/resident/create">Создать заявку</Link>
      </Button>
      <Button variant="secondary" stretched asChild>
        <Link to="/resident/tickets">Мои заявки</Link>
      </Button>
    </div>
  );
}
