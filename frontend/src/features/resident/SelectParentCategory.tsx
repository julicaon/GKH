import { Button, CellList, CellSimple, Typography } from '@maxhub/max-ui';
import type { ParentCategory } from '../../shared/api/types';

type Props = {
  parents: ParentCategory[];
  onSelect: (parent: ParentCategory) => void;
  onBack: () => void;
};

export function SelectParentCategory({ parents, onSelect, onBack }: Props) {
  return (
    <div className="page-stack">
      <Typography.Headline>Категория</Typography.Headline>
      <Typography.Body>Что случилось?</Typography.Body>
      <CellList mode="island">
        {parents.map((p) => (
          <CellSimple key={p.id} title={p.name} showChevron onClick={() => onSelect(p)} />
        ))}
      </CellList>
      <Button variant="secondary" onClick={onBack}>
        Назад
      </Button>
    </div>
  );
}
