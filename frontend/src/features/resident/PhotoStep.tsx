import { useState } from 'react';
import { Button, Input, Typography } from '@maxhub/max-ui';

type Props = {
  initialUrl?: string;
  onNext: (photoUrl?: string) => void;
  onBack: () => void;
  submitting?: boolean;
};

export function PhotoStep({ initialUrl = '', onNext, onBack, submitting }: Props) {
  const [url, setUrl] = useState(initialUrl);

  return (
    <div className="page-stack">
      <Typography.Headline>Фото</Typography.Headline>
      <Typography.Body>Укажите ссылку на фото (необязательно)</Typography.Body>
      <Input
        placeholder="https://…"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />
      {url.trim() && (
        <img className="photo-preview" src={url.trim()} alt="Превью" onError={() => undefined} />
      )}
      <div className="row">
        <Button variant="secondary" onClick={onBack} disabled={submitting}>
          Назад
        </Button>
        <Button
          variant="primary"
          stretched
          loading={submitting}
          disabled={submitting}
          onClick={() => onNext(url.trim() || undefined)}
        >
          Отправить заявку
        </Button>
      </div>
    </div>
  );
}
