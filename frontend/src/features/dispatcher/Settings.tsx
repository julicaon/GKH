import { useCallback, useEffect, useState } from 'react';
import {
  Button,
  CellInput,
  CellList,
  CellSimple,
  Input,
  Spinner,
  Textarea,
  Typography,
} from '@maxhub/max-ui';
import { Link } from 'react-router-dom';
import { getDispatcherSession } from '../../shared/api/auth';
import {
  createCategory,
  createParentCategory,
  createQuestion,
  createRule,
  listCategories,
  listParentCategories,
} from '../../shared/api/triage';
import { createSpecialist, listSpecialists } from '../../shared/api/specialists';
import type {
  Category,
  ParentCategory,
  Specialist,
  UrgencyLevel,
} from '../../shared/api/types';

export function Settings() {
  const session = getDispatcherSession();
  const [parents, setParents] = useState<ParentCategory[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [specialists, setSpecialists] = useState<Specialist[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [parentName, setParentName] = useState('');
  const [catParentId, setCatParentId] = useState('');
  const [catName, setCatName] = useState('');
  const [qCategoryId, setQCategoryId] = useState('');
  const [qText, setQText] = useState('');
  const [qOptions, setQOptions] = useState('да:yes\nнет:no');
  const [ruleCategoryId, setRuleCategoryId] = useState('');
  const [ruleMatch, setRuleMatch] = useState('{"questionId":"optionId"}');
  const [ruleText, setRuleText] = useState('');
  const [rulePriority, setRulePriority] = useState('10');
  const [ruleUrgency, setRuleUrgency] = useState<UrgencyLevel | ''>('HIGH');
  const [specName, setSpecName] = useState('');
  const [specTags, setSpecTags] = useState('');

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [p, c, s] = await Promise.all([
        listParentCategories(),
        listCategories(),
        listSpecialists(),
      ]);
      setParents(p);
      setCategories(c);
      setSpecialists(s);
      setCatParentId((prev) => prev || p[0]?.id || '');
      setQCategoryId((prev) => prev || c[0]?.id || '');
      setRuleCategoryId((prev) => prev || c[0]?.id || '');
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Ошибка загрузки');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void reload();
  }, [reload]);

  const wrap = async (label: string, fn: () => Promise<unknown>) => {
    setMessage(null);
    setError(null);
    try {
      await fn();
      setMessage(label);
      await reload();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Ошибка');
    }
  };

  if (loading && !parents.length) {
    return (
      <div className="page center">
        <Spinner size={32} />
      </div>
    );
  }

  return (
    <div className="page page-stack">
      <Button variant="ghost" asChild>
        <Link to="/dispatcher">← Лента</Link>
      </Button>
      <Typography.Headline>Настройки триажа</Typography.Headline>
      {message && <Typography.Body>{message}</Typography.Body>}
      {error && <Typography.Body>{error}</Typography.Body>}

      <Typography.Title>Родительские категории</Typography.Title>
      <CellList mode="island">
        {parents.map((p) => (
          <CellSimple key={p.id} title={p.name} subtitle={`order=${p.order}`} />
        ))}
      </CellList>
      <CellList mode="island">
        <CellInput
          before="Название"
          value={parentName}
          onChange={(e) => setParentName(e.target.value)}
          placeholder="Новая родительская"
        />
      </CellList>
      <Button
        variant="primary"
        stretched
        disabled={!parentName.trim()}
        onClick={() =>
          void wrap('Родительская создана', () =>
            createParentCategory({ name: parentName.trim(), order: parents.length }),
          ).then(() => setParentName(''))
        }
      >
        Создать родительскую
      </Button>

      <Typography.Title>Категории</Typography.Title>
      <CellList mode="island">
        {categories.map((c) => (
          <CellSimple
            key={c.id}
            title={c.name}
            subtitle={`parent=${c.parentCategoryId}`}
          />
        ))}
      </CellList>
      <Typography.Label>Родитель</Typography.Label>
      <CellList mode="island">
        {parents.map((p) => (
          <CellSimple
            key={p.id}
            title={p.name}
            onClick={() => setCatParentId(p.id)}
            after={catParentId === p.id ? '✓' : undefined}
          />
        ))}
      </CellList>
      <Input
        placeholder="Название категории"
        value={catName}
        onChange={(e) => setCatName(e.target.value)}
      />
      <Button
        variant="primary"
        stretched
        disabled={!catName.trim() || !catParentId}
        onClick={() =>
          void wrap('Категория создана', () =>
            createCategory({
              parentCategoryId: catParentId,
              name: catName.trim(),
              order: categories.filter((c) => c.parentCategoryId === catParentId).length,
            }),
          ).then(() => setCatName(''))
        }
      >
        Создать категорию
      </Button>

      <Typography.Title>Вопрос</Typography.Title>
      <Typography.Label>Категория</Typography.Label>
      <CellList mode="island">
        {categories.map((c) => (
          <CellSimple
            key={c.id}
            title={c.name}
            onClick={() => setQCategoryId(c.id)}
            after={qCategoryId === c.id ? '✓' : undefined}
          />
        ))}
      </CellList>
      <Input
        placeholder="Текст вопроса"
        value={qText}
        onChange={(e) => setQText(e.target.value)}
      />
      <Textarea
        mode="primary"
        rows={3}
        placeholder={'Варианты: label:code по строке'}
        value={qOptions}
        onChange={(e) => setQOptions(e.target.value)}
      />
      <Button
        variant="primary"
        stretched
        disabled={!qText.trim() || !qCategoryId}
        onClick={() => {
          const options = qOptions
            .split('\n')
            .map((line) => line.trim())
            .filter(Boolean)
            .map((line) => {
              const [label, code] = line.split(':');
              return { label: (label ?? '').trim(), code: (code ?? label ?? '').trim() };
            })
            .filter((o) => o.label);
          void wrap('Вопрос добавлен', () =>
            createQuestion({
              categoryId: qCategoryId,
              text: qText.trim(),
              options,
            }),
          ).then(() => setQText(''));
        }}
      >
        Добавить вопрос
      </Button>

      <Typography.Title>Правило рекомендации</Typography.Title>
      <CellList mode="island">
        {categories.map((c) => (
          <CellSimple
            key={c.id}
            title={c.name}
            onClick={() => setRuleCategoryId(c.id)}
            after={ruleCategoryId === c.id ? '✓' : undefined}
          />
        ))}
      </CellList>
      <Textarea
        mode="primary"
        rows={2}
        placeholder="match JSON"
        value={ruleMatch}
        onChange={(e) => setRuleMatch(e.target.value)}
      />
      <Textarea
        mode="primary"
        rows={2}
        placeholder="Текст рекомендации"
        value={ruleText}
        onChange={(e) => setRuleText(e.target.value)}
      />
      <Input
        placeholder="Приоритет"
        value={rulePriority}
        onChange={(e) => setRulePriority(e.target.value)}
      />
      <CellList mode="island">
        {(['HIGH', 'MEDIUM', 'LOW', ''] as const).map((u) => (
          <CellSimple
            key={u || 'none'}
            title={u || 'без urgency'}
            onClick={() => setRuleUrgency(u)}
            after={ruleUrgency === u ? '✓' : undefined}
          />
        ))}
      </CellList>
      <Button
        variant="primary"
        stretched
        disabled={!ruleText.trim() || !ruleCategoryId}
        onClick={() => {
          let match: Record<string, string> = {};
          try {
            match = JSON.parse(ruleMatch) as Record<string, string>;
          } catch {
            setError('Некорректный JSON match');
            return;
          }
          void wrap('Правило сохранено', () =>
            createRule({
              categoryId: ruleCategoryId,
              match,
              recommendationText: ruleText.trim(),
              priority: Number(rulePriority) || 0,
              setsUrgency: ruleUrgency || null,
            }),
          );
        }}
      >
        Добавить правило
      </Button>

      <Typography.Title>Специалисты</Typography.Title>
      <CellList mode="island">
        {specialists.map((s) => (
          <CellSimple
            key={s.id}
            title={s.fullName}
            subtitle={s.skillTags.join(', ') || '—'}
          />
        ))}
      </CellList>
      <Input
        placeholder="ФИО"
        value={specName}
        onChange={(e) => setSpecName(e.target.value)}
      />
      <Input
        placeholder="Теги через запятую"
        value={specTags}
        onChange={(e) => setSpecTags(e.target.value)}
      />
      <Button
        variant="primary"
        stretched
        disabled={!specName.trim()}
        onClick={() =>
          void wrap('Специалист создан', () =>
            createSpecialist({
              organizationId: session.organizationId ?? undefined,
              fullName: specName.trim(),
              skillTags: specTags
                .split(',')
                .map((t) => t.trim())
                .filter(Boolean),
            }),
          ).then(() => {
            setSpecName('');
            setSpecTags('');
          })
        }
      >
        Создать специалиста
      </Button>
    </div>
  );
}
