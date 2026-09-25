import { apiRequest } from './client';
import type {
  Category,
  CategoryCreate,
  ParentCategory,
  ParentCategoryCreate,
  Question,
  QuestionCreate,
  RecommendationRule,
  RuleCreate,
} from './types';

export function listParentCategories(activeOnly = false): Promise<ParentCategory[]> {
  return apiRequest<ParentCategory[]>('/api/parent-categories', {
    query: { active_only: activeOnly },
    auth: false,
  });
}

export function createParentCategory(body: ParentCategoryCreate): Promise<ParentCategory> {
  return apiRequest<ParentCategory>('/api/parent-categories', { method: 'POST', body });
}

export function listCategories(parentId?: string, activeOnly = false): Promise<Category[]> {
  return apiRequest<Category[]>('/api/categories', {
    query: { parentId, active_only: activeOnly },
    auth: false,
  });
}

export function createCategory(body: CategoryCreate): Promise<Category> {
  return apiRequest<Category>('/api/categories', { method: 'POST', body });
}

export function createQuestion(body: QuestionCreate): Promise<Question> {
  return apiRequest<Question>('/api/questions', { method: 'POST', body });
}

export function createRule(body: RuleCreate): Promise<RecommendationRule> {
  return apiRequest<RecommendationRule>('/api/rules', { method: 'POST', body });
}
