import { CellList, CellSimple, Spinner, Typography } from '@maxhub/max-ui';
import type { Building } from '../../shared/api/types';

type Props = {
  buildings: Building[];
  loading: boolean;
  error: string | null;
  onSelect: (building: Building) => void;
};

export function SelectAddress({ buildings, loading, error, onSelect }: Props) {
  if (loading) {
    return (
      <div className="center">
        <Spinner size={32} />
      </div>
    );
  }

  if (error) {
    return <Typography.Body>{error}</Typography.Body>;
  }

  return (
    <div className="page-stack">
      <Typography.Headline>Адрес</Typography.Headline>
      <Typography.Body>Выберите дом</Typography.Body>
      <CellList mode="island">
        {buildings.map((b) => (
          <CellSimple
            key={b.id}
            title={b.addressLabel}
            showChevron
            onClick={() => onSelect(b)}
          />
        ))}
      </CellList>
    </div>
  );
}
