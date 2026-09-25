import { Button, CellList, CellSimple, Typography } from '@maxhub/max-ui';
import type { Category } from '../../shared/api/types';

type Props = {
  categories: Category[];
  parentName: string;
  onSelect: (category: Category) => void;
  onBack: () => void;
};

export function SelectCategory({ categories, parentName, onSelect, onBack }: Props) {
  return (
    <div className="page-stack">
      <Typography.Headline>{parentName}</Typography.Headline>
      <Typography.Body>Уточните тему</Typography.Body>
      <CellList mode="island">
        {categories.map((c) => (
          <CellSimple key={c.id} title={c.name} showChevron onClick={() => onSelect(c)} />
        ))}
      </CellList>
      <Button variant="secondary" onClick={onBack}>
        Назад
      </Button>
    </div>
  );
}
