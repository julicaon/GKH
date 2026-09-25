import { apiRequest } from './client';
import type { Building, BuildingCategories, Questionnaire } from './types';

export function listBuildings(): Promise<Building[]> {
  return apiRequest<Building[]>('/api/buildings', { auth: false });
}

export function getBuildingCategories(buildingId: string): Promise<BuildingCategories> {
  return apiRequest<BuildingCategories>(`/api/buildings/${buildingId}/categories`, {
    auth: false,
  });
}

export function getQuestionnaire(categoryId: string): Promise<Questionnaire> {
  return apiRequest<Questionnaire>(`/api/categories/${categoryId}/questionnaire`, {
    auth: false,
  });
}
