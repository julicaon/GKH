import { useState } from 'react';
import { Button, CellInput, CellList, Typography } from '@maxhub/max-ui';
import { useNavigate } from 'react-router-dom';
import { login } from '../../shared/api/auth';

export function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('dispatcher_sever');
  const [password, setPassword] = useState('sever123');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      await login(username.trim(), password);
      navigate('/dispatcher');
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Ошибка входа');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page page-stack">
      <Typography.Headline>Вход диспетчера</Typography.Headline>
      <Typography.Body className="muted">
        Seed: dispatcher_sever / sever123 · dispatcher_yug / yug123
      </Typography.Body>
      <CellList mode="island">
        <CellInput
          before="Логин"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="username"
        />
        <CellInput
          before="Пароль"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="password"
        />
      </CellList>
      {error && <Typography.Body>{error}</Typography.Body>}
      <Button variant="primary" stretched loading={loading} onClick={() => void onSubmit()}>
        Войти
      </Button>
    </div>
  );
}
