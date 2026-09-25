from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from application.use_cases.triage import (
    AddOption,
    AddQuestion,
    CreateCategory,
    CreateParentCategory,
    GetCategoryQuestionnaire,
    ListCategories,
    ListParentCategories,
    UpdateCategory,
    UpsertRecommendationRule,
)
from domain.exceptions import CategoryNotFoundError, ValidationError
from interfaces.deps import get_db, repos
from interfaces.schemas import (
    CategoryIn,
    CategoryOut,
    CategoryUpdateIn,
    OptionIn,
    ParentCategoryIn,
    ParentCategoryOut,
    QuestionIn,
    QuestionOut,
    QuestionnaireOut,
    RuleIn,
    RuleOut,
    category_out,
    parent_out,
    question_out,
    rule_out,
)

router = APIRouter(prefix="/api", tags=["triage"])


@router.get("/parent-categories", response_model=list[ParentCategoryOut])
def list_parents(
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
):
    r = repos(db)
    items = ListParentCategories(categories=r["categories"]).execute(active_only=active_only)
    return [parent_out(p) for p in items]


@router.post("/parent-categories", response_model=ParentCategoryOut)
def create_parent(body: ParentCategoryIn, db: Session = Depends(get_db)):
    r = repos(db)
    p = CreateParentCategory(categories=r["categories"]).execute(
        name=body.name,
        order=body.order,
        active=body.active,
        default_urgency_hint=body.defaultUrgencyHint,
        id=body.id,
    )
    return parent_out(p)


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(
    parentId: Optional[str] = Query(None),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
):
    r = repos(db)
    items = ListCategories(categories=r["categories"]).execute(
        parent_id=parentId, active_only=active_only
    )
    return [category_out(c) for c in items]


@router.post("/categories", response_model=CategoryOut)
def create_category(body: CategoryIn, db: Session = Depends(get_db)):
    r = repos(db)
    try:
        c = CreateCategory(categories=r["categories"]).execute(
            parent_category_id=body.parentCategoryId,
            name=body.name,
            order=body.order,
            active=body.active,
            default_recommendation_text=body.defaultRecommendationText,
            default_urgency=body.defaultUrgency,
            organization_ids=body.organizationIds,
            id=body.id,
        )
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return category_out(c)


@router.patch("/categories/{category_id}", response_model=CategoryOut)
def update_category(category_id: str, body: CategoryUpdateIn, db: Session = Depends(get_db)):
    r = repos(db)
    try:
        c = UpdateCategory(categories=r["categories"]).execute(
            category_id=category_id,
            name=body.name,
            active=body.active,
            order=body.order,
            default_recommendation_text=body.defaultRecommendationText,
            default_urgency=body.defaultUrgency,
            organization_ids=body.organizationIds,
        )
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return category_out(c)


@router.post("/questions", response_model=QuestionOut)
def add_question(body: QuestionIn, db: Session = Depends(get_db)):
    r = repos(db)
    try:
        q = AddQuestion(categories=r["categories"]).execute(
            category_id=body.categoryId,
            text=body.text,
            order=body.order,
            active=body.active,
            options=[o.model_dump() for o in body.options],
            id=body.id,
        )
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return question_out(q)


@router.post("/questions/{question_id}/options", response_model=QuestionOut)
def add_option(question_id: str, body: OptionIn, db: Session = Depends(get_db)):
    r = repos(db)
    try:
        q = AddOption(categories=r["categories"]).execute(
            question_id=question_id,
            label=body.label,
            code=body.code,
            id=body.id,
        )
    except ValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return question_out(q)


@router.post("/rules", response_model=RuleOut)
def upsert_rule(body: RuleIn, db: Session = Depends(get_db)):
    r = repos(db)
    try:
        rule = UpsertRecommendationRule(categories=r["categories"]).execute(
            category_id=body.categoryId,
            match=body.match,
            recommendation_text=body.recommendationText,
            priority=body.priority,
            active=body.active,
            sets_urgency=body.setsUrgency,
            id=body.id,
        )
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return rule_out(rule)


@router.get("/categories/{category_id}/questionnaire", response_model=QuestionnaireOut)
def questionnaire(category_id: str, db: Session = Depends(get_db)):
    r = repos(db)
    try:
        data = GetCategoryQuestionnaire(categories=r["categories"]).execute(category_id)
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return QuestionnaireOut(
        category=category_out(data["category"]),
        parent=parent_out(data["parent"]) if data["parent"] else None,
        questions=[question_out(q) for q in data["questions"]],
        rules=[rule_out(rule) for rule in data["rules"]],
    )
