import { useEffect, useMemo, useState } from 'react';
import { Button, Spinner, Typography } from '@maxhub/max-ui';
import { Link } from 'react-router-dom';
import { getBuildingCategories, listBuildings } from '../../shared/api/buildings';
import { createTicket } from '../../shared/api/tickets';
import type {
  Building,
  Category,
  CategoryTreeNode,
  ParentCategory,
  Ticket,
} from '../../shared/api/types';
import { useDevShellOverrides } from '../../dev/DevShell';
import { Questionnaire } from '../../shared/questionnaire/Questionnaire';
import { SelectAddress } from './SelectAddress';
import { SelectParentCategory } from './SelectParentCategory';
import { SelectCategory } from './SelectCategory';
import { PhotoStep } from './PhotoStep';
import { ResultScreen } from './ResultScreen';

type Step = 'address' | 'parent' | 'leaf' | 'questions' | 'photo' | 'result';

export function CreateTicketFlow() {
  const { userId } = useDevShellOverrides();
  const [step, setStep] = useState<Step>('address');
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [loadingBuildings, setLoadingBuildings] = useState(true);
  const [buildingsError, setBuildingsError] = useState<string | null>(null);

  const [building, setBuilding] = useState<Building | null>(null);
  const [tree, setTree] = useState<CategoryTreeNode[]>([]);
  const [loadingTree, setLoadingTree] = useState(false);

  const [parent, setParent] = useState<ParentCategory | null>(null);
  const [category, setCategory] = useState<Category | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [photoUrl, setPhotoUrl] = useState<string | undefined>();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoadingBuildings(true);
    listBuildings()
      .then((items) => {
        if (!cancelled) setBuildings(items);
      })
      .catch((e: unknown) => {
        if (!cancelled) setBuildingsError(e instanceof Error ? e.message : 'Ошибка');
      })
      .finally(() => {
        if (!cancelled) setLoadingBuildings(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const leafCategories = useMemo(() => {
    if (!parent) return [];
    const node = tree.find((n) => n.parent.id === parent.id);
    return node?.categories.filter((c) => c.active) ?? [];
  }, [parent, tree]);

  const parents = useMemo(
    () => tree.map((n) => n.parent).filter((p) => p.active),
    [tree],
  );

  const selectBuilding = async (b: Building) => {
    setBuilding(b);
    setParent(null);
    setCategory(null);
    setLoadingTree(true);
    try {
      const data = await getBuildingCategories(b.id);
      setTree(data.tree);
      setStep('parent');
    } catch (e: unknown) {
      setBuildingsError(e instanceof Error ? e.message : 'Ошибка категорий');
    } finally {
      setLoadingTree(false);
    }
  };

  const submit = async (url?: string) => {
    if (!building || !category) return;
    setPhotoUrl(url);
    setSubmitting(true);
    setSubmitError(null);
    try {
      const created = await createTicket(
        {
          buildingId: building.id,
          categoryId: category.id,
          answers,
          photoUrl: url,
        },
        userId,
      );
      setTicket(created);
      setStep('result');
    } catch (e: unknown) {
      setSubmitError(e instanceof Error ? e.message : 'Не удалось создать заявку');
    } finally {
      setSubmitting(false);
    }
  };

  if (step === 'result' && ticket) {
    return (
      <div className="page">
        <ResultScreen ticket={ticket} />
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

      {loadingTree && (
        <div className="center">
          <Spinner size={32} />
        </div>
      )}

      {!loadingTree && step === 'address' && (
        <SelectAddress
          buildings={buildings}
          loading={loadingBuildings}
          error={buildingsError}
          onSelect={selectBuilding}
        />
      )}

      {!loadingTree && step === 'parent' && (
        <SelectParentCategory
          parents={parents}
          onSelect={(p) => {
            setParent(p);
            setCategory(null);
            setStep('leaf');
          }}
          onBack={() => setStep('address')}
        />
      )}

      {!loadingTree && step === 'leaf' && parent && (
        <SelectCategory
          categories={leafCategories}
          parentName={parent.name}
          onSelect={(c) => {
            setCategory(c);
            setStep('questions');
          }}
          onBack={() => setStep('parent')}
        />
      )}

      {!loadingTree && step === 'questions' && category && (
        <Questionnaire
          categoryId={category.id}
          onComplete={(a) => {
            setAnswers(a);
            setStep('photo');
          }}
          onBack={() => setStep('leaf')}
        />
      )}

      {!loadingTree && step === 'photo' && (
        <>
          {submitError && <Typography.Body>{submitError}</Typography.Body>}
          <PhotoStep
            initialUrl={photoUrl}
            submitting={submitting}
            onBack={() => setStep('questions')}
            onNext={submit}
          />
        </>
      )}
    </div>
  );
}
