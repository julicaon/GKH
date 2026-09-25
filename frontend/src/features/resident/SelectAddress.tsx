import { useMemo, useState } from 'react';
import { CellInput, CellList, CellSimple, Spinner, Typography } from '@maxhub/max-ui';
import type { Building } from '../../shared/api/types';

type Props = {
  buildings: Building[];
  loading: boolean;
  error: string | null;
  onSelect: (building: Building) => void;
};

function normalize(s: string): string {
  return s.toLowerCase().replace(/[.,]/g, ' ').replace(/\s+/g, ' ').trim();
}

export function SelectAddress({ buildings, loading, error, onSelect }: Props) {
  const [query, setQuery] = useState('');

  const suggestions = useMemo(() => {
    const q = normalize(query);
    if (!q) return buildings.slice(0, 8);
    const tokens = q.split(' ').filter(Boolean);
    return buildings
      .map((b) => {
        const label = normalize(b.addressLabel);
        const score = tokens.reduce((acc, t) => acc + (label.includes(t) ? 1 : 0), 0);
        return { b, score, label };
      })
      .filter(({ score }) => score > 0)
      .sort((a, b) => b.score - a.score || a.label.localeCompare(b.label, 'ru'))
      .map(({ b }) => b);
  }, [buildings, query]);

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
      <Typography.Body>Начните вводить адрес — покажем дома из базы</Typography.Body>

      <CellList mode="island">
        <CellInput
          surface="island"
          autoFocus
          placeholder="Например: Ленина 10"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </CellList>

      {query.trim() && !suggestions.length && (
        <Typography.Body>Нет совпадений среди домов УК в базе</Typography.Body>
      )}

      {suggestions.length > 0 && (
        <CellList mode="island" className="address-dropdown">
          {suggestions.map((b) => (
            <CellSimple
              key={b.id}
              title={b.addressLabel}
              showChevron
              onClick={() => onSelect(b)}
            />
          ))}
        </CellList>
      )}
    </div>
  );
}
