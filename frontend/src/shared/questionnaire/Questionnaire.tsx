import { useEffect, useMemo, useState } from 'react';
import { Button, CellList, CellSimple, Radio, Spinner, Typography } from '@maxhub/max-ui';
import type { Question } from '../api/types';
import { getQuestionnaire } from '../api/buildings';

type Props = {
  categoryId: string;
  onComplete: (answers: Record<string, string>) => void;
  onBack?: () => void;
};

export function Questionnaire({ categoryId, onComplete, onBack }: Props) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setIndex(0);
    setAnswers({});
    setSelected(null);
    getQuestionnaire(categoryId)
      .then((data) => {
        if (cancelled) return;
        const sorted = [...data.questions]
          .filter((q) => q.active)
          .sort((a, b) => a.order - b.order);
        setQuestions(sorted);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Ошибка загрузки');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [categoryId]);

  const current = questions[index];
  const isLast = index >= questions.length - 1 && questions.length > 0;

  const progress = useMemo(() => {
    if (!questions.length) return '';
    return `Вопрос ${index + 1} из ${questions.length}`;
  }, [index, questions.length]);

  if (loading) {
    return (
      <div className="center">
        <Spinner size={32} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-stack">
        <Typography.Body>{error}</Typography.Body>
        {onBack && (
          <Button variant="secondary" onClick={onBack}>
            Назад
          </Button>
        )}
      </div>
    );
  }

  if (!current) {
    return (
      <div className="page-stack">
        <Typography.Body>Нет вопросов для этой категории.</Typography.Body>
        <Button variant="primary" stretched onClick={() => onComplete({})}>
          Продолжить
        </Button>
      </div>
    );
  }

  const handleNext = () => {
    if (!selected) return;
    const nextAnswers = { ...answers, [current.id]: selected };
    setAnswers(nextAnswers);
    if (isLast) {
      onComplete(nextAnswers);
      return;
    }
    const nextIndex = index + 1;
    setIndex(nextIndex);
    setSelected(nextAnswers[questions[nextIndex]?.id] ?? null);
  };

  return (
    <div className="page-stack">
      <Typography.Headline>{progress}</Typography.Headline>
      <Typography.Title>{current.text}</Typography.Title>
      <CellList mode="island">
        {current.options.map((opt) => (
          <CellSimple
            key={opt.id}
            title={opt.label}
            onClick={() => setSelected(opt.id)}
            after={
              <Radio
                name={`q-${current.id}`}
                checked={selected === opt.id}
                onChange={() => setSelected(opt.id)}
                value={opt.id}
              />
            }
          />
        ))}
      </CellList>
      <div className="row">
        {onBack && index === 0 && (
          <Button variant="secondary" onClick={onBack}>
            Назад
          </Button>
        )}
        {index > 0 && (
          <Button
            variant="secondary"
            onClick={() => {
              const prev = index - 1;
              setIndex(prev);
              setSelected(answers[questions[prev]?.id] ?? null);
            }}
          >
            Назад
          </Button>
        )}
        <Button variant="primary" stretched disabled={!selected} onClick={handleNext}>
          {isLast ? 'Готово' : 'Далее'}
        </Button>
      </div>
    </div>
  );
}
