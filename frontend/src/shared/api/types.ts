export type UrgencyLevel = 'LOW' | 'MEDIUM' | 'HIGH';

export type TicketStatus =
  | 'NEW'
  | 'ACCEPTED'
  | 'IN_PROGRESS'
  | 'DONE'
  | 'CANCELLED_BY_RESIDENT';

export interface Building {
  id: string;
  addressLabel: string;
  organizationId: string;
  availableParentCategoryIds?: string[] | null;
  availableCategoryIds?: string[] | null;
}

export interface ParentCategory {
  id: string;
  name: string;
  order: number;
  active: boolean;
  defaultUrgencyHint: UrgencyLevel;
}

export interface Category {
  id: string;
  parentCategoryId: string;
  name: string;
  active: boolean;
  order: number;
  defaultRecommendationText: string;
  defaultUrgency: UrgencyLevel;
  organizationIds?: string[] | null;
}

export interface Option {
  id: string;
  label: string;
  code: string;
}

export interface Question {
  id: string;
  categoryId: string;
  text: string;
  order: number;
  active: boolean;
  options: Option[];
}

export interface RecommendationRule {
  id: string;
  categoryId: string;
  match: Record<string, string>;
  recommendationText: string;
  priority: number;
  active: boolean;
  setsUrgency?: UrgencyLevel | null;
}

export interface CategoryTreeNode {
  parent: ParentCategory;
  categories: Category[];
}

export interface BuildingCategories {
  building: Building;
  tree: CategoryTreeNode[];
}

export interface Questionnaire {
  category: Category;
  parent?: ParentCategory | null;
  questions: Question[];
  rules: RecommendationRule[];
}

export interface AnswerSnapshot {
  questionId: string;
  questionLabel: string;
  optionId: string;
  optionLabel: string;
  optionCode: string;
}

export interface StatusHistoryEntry {
  status: TicketStatus;
  at: string;
  note?: string | null;
}

export interface Ticket {
  id: string;
  residentRef: string;
  buildingId: string;
  addressSnapshot: string;
  organizationId: string;
  parentCategoryId: string;
  categoryId: string;
  answersSnapshot: AnswerSnapshot[];
  recommendationTextSnapshot: string;
  urgencyLevel: UrgencyLevel;
  summaryText: string;
  status: TicketStatus;
  photoUrl?: string | null;
  assigneeSpecialistId?: string | null;
  takenByDispatcherId?: string | null;
  createdAt: string;
  updatedAt: string;
  statusHistory: StatusHistoryEntry[];
}

export interface SubmitTicketBody {
  buildingId: string;
  categoryId: string;
  answers: Record<string, string>;
  photoUrl?: string;
}

export interface Specialist {
  id: string;
  organizationId: string;
  fullName: string;
  skillTags: string[];
  active: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  dispatcher_id: string;
  organization_id: string;
  username: string;
  full_name: string;
}

export interface ParentCategoryCreate {
  name: string;
  order?: number;
  active?: boolean;
  defaultUrgencyHint?: UrgencyLevel;
  id?: string;
}

export interface CategoryCreate {
  parentCategoryId: string;
  name: string;
  order?: number;
  active?: boolean;
  defaultRecommendationText?: string;
  defaultUrgency?: UrgencyLevel;
  organizationIds?: string[] | null;
  id?: string;
}

export interface QuestionCreate {
  categoryId: string;
  text: string;
  order?: number;
  active?: boolean;
  options?: Array<{ label: string; code: string; id?: string }>;
  id?: string;
}

export interface RuleCreate {
  categoryId: string;
  match: Record<string, string>;
  recommendationText: string;
  priority: number;
  active?: boolean;
  setsUrgency?: UrgencyLevel | null;
  id?: string;
}

export interface SpecialistCreate {
  organizationId?: string;
  fullName: string;
  skillTags?: string[];
  active?: boolean;
  id?: string;
}
