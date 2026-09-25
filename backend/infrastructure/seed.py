"""Seed database with Smart City MVP demo data."""
from __future__ import annotations

from sqlalchemy.orm import Session

from application.use_cases.auth import hash_password
from domain.entities import (
    Building,
    Category,
    DispatcherAccount,
    Option,
    Organization,
    ParentCategory,
    Question,
    RecommendationRule,
    Specialist,
)
from domain.enums import UrgencyLevel
from infrastructure.persistence.models import OrganizationModel
from infrastructure.persistence.repositories import (
    SqlBuildingRepository,
    SqlCategoryRepository,
    SqlOrganizationRepository,
    SqlSpecialistRepository,
)

# Stable IDs for tests / demos
ORG_SEVER = "org-sever"
ORG_YUG = "org-yug"

PARENT_VODA = "parent-voda"
PARENT_ELEKTRO = "parent-elektro"
PARENT_PODEZD = "parent-podezd"
PARENT_GAZ = "parent-gaz"

CAT_PROTECHKA = "cat-protechka"
CAT_NO_POWER = "cat-no-power"
CAT_DOOR = "cat-door"
CAT_TRASH = "cat-trash"

Q_LEAK_WHERE = "q-leak-where"
Q_SHUT_OFF = "q-shut-off"
Q_THREAT = "q-threat"

OPT_CEILING = "opt-ceiling"
OPT_WALLS = "opt-walls"
OPT_FLOOR = "opt-floor"
OPT_RISER = "opt-riser"
OPT_CAN_SHUT = "opt-can-shut"
OPT_CANNOT_SHUT = "opt-cannot-shut"
OPT_THREAT_YES = "opt-threat-yes"
OPT_THREAT_NO = "opt-threat-no"

Q_POWER_SCOPE = "q-power-scope"
Q_BREAKER = "q-breaker"
OPT_WHOLE = "opt-whole"
OPT_ROOM = "opt-room"
OPT_TRIPPED = "opt-tripped"
OPT_ON = "opt-on"
OPT_UNKNOWN = "opt-unknown"

Q_DOOR_WHAT = "q-door-what"
Q_DOOR_NIGHT = "q-door-night"
OPT_CLOSER = "opt-closer"
OPT_INTERCOM = "opt-intercom"
OPT_KEY = "opt-key"
OPT_NIGHT_YES = "opt-night-yes"
OPT_NIGHT_NO = "opt-night-no"

BLD_SEVER_1 = "bld-sever-1"
BLD_SEVER_2 = "bld-sever-2"
BLD_YUG_1 = "bld-yug-1"
BLD_YUG_NO_GAZ = "bld-yug-no-gaz"

SPEC_SEVER_PLUMBER = "spec-sever-plumber"
SPEC_SEVER_ELEC = "spec-sever-elec"
SPEC_YUG_PLUMBER = "spec-yug-plumber"
SPEC_YUG_DOOR = "spec-yug-door"

DISP_SEVER = "disp-sever"
DISP_YUG = "disp-yug"


def is_empty(session: Session) -> bool:
    return session.query(OrganizationModel).count() == 0


def seed_database(session: Session) -> None:
    if not is_empty(session):
        return

    orgs = SqlOrganizationRepository(session)
    buildings = SqlBuildingRepository(session)
    categories = SqlCategoryRepository(session)
    specialists = SqlSpecialistRepository(session)

    orgs.add(Organization(id=ORG_SEVER, name='УК "Северная"'))
    orgs.add(Organization(id=ORG_YUG, name='УК "Южная"'))

    # Parent categories
    categories.add_parent(
        ParentCategory(
            id=PARENT_VODA,
            name="ВОДА",
            order=1,
            active=True,
            default_urgency_hint=UrgencyLevel.HIGH,
        )
    )
    categories.add_parent(
        ParentCategory(
            id=PARENT_ELEKTRO,
            name="ЭЛЕКТРИКА",
            order=2,
            active=True,
            default_urgency_hint=UrgencyLevel.MEDIUM,
        )
    )
    categories.add_parent(
        ParentCategory(
            id=PARENT_PODEZD,
            name="ПОДЪЕЗД / ДВОР",
            order=3,
            active=True,
            default_urgency_hint=UrgencyLevel.LOW,
        )
    )
    categories.add_parent(
        ParentCategory(
            id=PARENT_GAZ,
            name="ГАЗ",
            order=4,
            active=True,
            default_urgency_hint=UrgencyLevel.HIGH,
        )
    )

    # Leaf: Протечка
    categories.add_category(
        Category(
            id=CAT_PROTECHKA,
            parent_category_id=PARENT_VODA,
            name="Протечка воды в квартире",
            active=True,
            order=1,
            default_recommendation_text=(
                "Оцените масштаб протечки, по возможности перекройте воду на стояке "
                "и ожидайте специалиста УК."
            ),
            default_urgency=UrgencyLevel.HIGH,
        )
    )
    categories.add_question(
        Question(
            id=Q_LEAK_WHERE,
            category_id=CAT_PROTECHKA,
            text="Где наблюдается протечка?",
            order=1,
            options=[
                Option(id=OPT_CEILING, label="Потолок", code="ceiling"),
                Option(id=OPT_WALLS, label="Стены", code="walls"),
                Option(id=OPT_FLOOR, label="Пол/под сантехникой", code="floor_plumbing"),
                Option(id=OPT_RISER, label="Стояк", code="riser"),
            ],
        )
    )
    categories.add_question(
        Question(
            id=Q_SHUT_OFF,
            category_id=CAT_PROTECHKA,
            text="Есть ли возможность перекрыть воду самостоятельно?",
            order=2,
            options=[
                Option(
                    id=OPT_CAN_SHUT,
                    label="Да, краны доступны",
                    code="can_shut_off",
                ),
                Option(
                    id=OPT_CANNOT_SHUT,
                    label="Нет, краны недоступны/сломаны",
                    code="cannot_shut_off=yes",
                ),
            ],
        )
    )
    categories.add_question(
        Question(
            id=Q_THREAT,
            category_id=CAT_PROTECHKA,
            text="Угрожает ли вода имуществу соседей прямо сейчас?",
            order=3,
            options=[
                Option(
                    id=OPT_THREAT_YES,
                    label="Да",
                    code="threat_neighbors=yes",
                ),
                Option(
                    id=OPT_THREAT_NO,
                    label="Нет",
                    code="threat_neighbors=no",
                ),
            ],
        )
    )
    categories.upsert_rule(
        RecommendationRule(
            id="rule-water-floor-shut",
            category_id=CAT_PROTECHKA,
            match={Q_LEAK_WHERE: OPT_FLOOR, Q_SHUT_OFF: OPT_CAN_SHUT},
            recommendation_text=(
                "Перекройте корневой вентиль на стояке в санузле и подставьте ёмкость. "
                "Специалист УК приедет для осмотра сантехники."
            ),
            priority=100,
            active=True,
        )
    )
    categories.upsert_rule(
        RecommendationRule(
            id="rule-water-cannot-shut",
            category_id=CAT_PROTECHKA,
            match={Q_SHUT_OFF: OPT_CANNOT_SHUT},
            recommendation_text=(
                "СРОЧНО: краны недоступны. Звоните в аварийную службу УК по телефону "
                "из приложения / на доске объявлений подъезда. Не пытайтесь ломать вентиль."
            ),
            priority=90,
            active=True,
            sets_urgency=UrgencyLevel.HIGH,
        )
    )

    # Leaf: Нет электричества
    categories.add_category(
        Category(
            id=CAT_NO_POWER,
            parent_category_id=PARENT_ELEKTRO,
            name="Нет электричества в квартире",
            active=True,
            order=1,
            default_recommendation_text=(
                "Вероятна неисправность на линии / этажном щите. "
                "Не вскрывайте щиток самостоятельно, ожидайте электрика УК."
            ),
            default_urgency=UrgencyLevel.MEDIUM,
        )
    )
    categories.add_question(
        Question(
            id=Q_POWER_SCOPE,
            category_id=CAT_NO_POWER,
            text="Где нет электричества?",
            order=1,
            options=[
                Option(id=OPT_WHOLE, label="Во всей квартире", code="whole_apt"),
                Option(id=OPT_ROOM, label="В одной комнате", code="one_room"),
            ],
        )
    )
    categories.add_question(
        Question(
            id=Q_BREAKER,
            category_id=CAT_NO_POWER,
            text="В каком положении автомат в щитке?",
            order=2,
            options=[
                Option(id=OPT_TRIPPED, label="Выбит (отключён)", code="breaker_tripped"),
                Option(id=OPT_ON, label="Включён", code="breaker_on"),
                Option(id=OPT_UNKNOWN, label="Не знаю / нет доступа", code="breaker_unknown"),
            ],
        )
    )
    categories.upsert_rule(
        RecommendationRule(
            id="rule-elec-room-tripped",
            category_id=CAT_NO_POWER,
            match={Q_POWER_SCOPE: OPT_ROOM, Q_BREAKER: OPT_TRIPPED},
            recommendation_text=(
                "Попробуйте один раз включить автомат. Если снова выбивает — отключите "
                "нагрузку в комнате и ожидайте электрика. Не включайте повторно многократно."
            ),
            priority=100,
            active=True,
        )
    )

    # Leaf: Дверь / домофон
    categories.add_category(
        Category(
            id=CAT_DOOR,
            parent_category_id=PARENT_PODEZD,
            name="Неисправность входной двери / домофона",
            active=True,
            order=1,
            default_recommendation_text=(
                "Заявка принята. Мастер по домофонам/дверям осмотрит узел в рабочее время."
            ),
            default_urgency=UrgencyLevel.LOW,
        )
    )
    categories.add_question(
        Question(
            id=Q_DOOR_WHAT,
            category_id=CAT_DOOR,
            text="Что неисправно?",
            order=1,
            options=[
                Option(id=OPT_CLOSER, label="Доводчик / дверь не закрывается", code="closer"),
                Option(id=OPT_INTERCOM, label="Домофон", code="intercom"),
                Option(id=OPT_KEY, label="Замок / ключ", code="key"),
            ],
        )
    )
    categories.add_question(
        Question(
            id=Q_DOOR_NIGHT,
            category_id=CAT_DOOR,
            text="Дверь остаётся открытой ночью?",
            order=2,
            options=[
                Option(id=OPT_NIGHT_YES, label="Да", code="door_open_night=yes"),
                Option(id=OPT_NIGHT_NO, label="Нет", code="door_open_night=no"),
            ],
        )
    )
    categories.upsert_rule(
        RecommendationRule(
            id="rule-door-open-night",
            category_id=CAT_DOOR,
            match={Q_DOOR_WHAT: OPT_CLOSER, Q_DOOR_NIGHT: OPT_NIGHT_YES},
            recommendation_text=(
                "Дверь не закрывается и открыта ночью — угроза безопасности. "
                "Сообщите консьержу/соседям и ожидайте срочный выезд."
            ),
            priority=100,
            active=True,
            sets_urgency=UrgencyLevel.HIGH,
        )
    )

    # Trash chute (for filtering demo — some buildings exclude)
    categories.add_category(
        Category(
            id=CAT_TRASH,
            parent_category_id=PARENT_PODEZD,
            name="Засор мусоропровода",
            active=True,
            order=2,
            default_recommendation_text="Не бросайте крупногабарит. Ожидайте дворника/слесаря.",
            default_urgency=UrgencyLevel.LOW,
        )
    )

    # Buildings
    # Sever-1: all parents except none — full set
    buildings.add(
        Building(
            id=BLD_SEVER_1,
            address_label="г. Северск, ул. Ленина, д. 10",
            organization_id=ORG_SEVER,
            available_parent_category_ids=None,
            available_category_ids=None,
        )
    )
    # Sever-2: without trash chute category
    buildings.add(
        Building(
            id=BLD_SEVER_2,
            address_label="г. Северск, ул. Мира, д. 5",
            organization_id=ORG_SEVER,
            available_parent_category_ids=[PARENT_VODA, PARENT_ELEKTRO, PARENT_PODEZD, PARENT_GAZ],
            available_category_ids=[CAT_PROTECHKA, CAT_NO_POWER, CAT_DOOR],
        )
    )
    # Yug-1: full
    buildings.add(
        Building(
            id=BLD_YUG_1,
            address_label="г. Южный, пр. Победы, д. 3",
            organization_id=ORG_YUG,
            available_parent_category_ids=None,
            available_category_ids=None,
        )
    )
    # Yug without Gaz parent
    buildings.add(
        Building(
            id=BLD_YUG_NO_GAZ,
            address_label="г. Южный, ул. Садовая, д. 12 (без газа)",
            organization_id=ORG_YUG,
            available_parent_category_ids=[PARENT_VODA, PARENT_ELEKTRO, PARENT_PODEZD],
            available_category_ids=None,
        )
    )

    # Specialists
    specialists.add(
        Specialist(
            id=SPEC_SEVER_PLUMBER,
            organization_id=ORG_SEVER,
            full_name="Иванов Пётр Сантехник",
            skill_tags=["вода", "протечка", "стояк"],
            active=True,
        )
    )
    specialists.add(
        Specialist(
            id=SPEC_SEVER_ELEC,
            organization_id=ORG_SEVER,
            full_name="Сидоров Алексей Электрик",
            skill_tags=["электрика", "щиток"],
            active=True,
        )
    )
    specialists.add(
        Specialist(
            id=SPEC_YUG_PLUMBER,
            organization_id=ORG_YUG,
            full_name="Козлова Мария Сантехник",
            skill_tags=["вода", "канализация"],
            active=True,
        )
    )
    specialists.add(
        Specialist(
            id=SPEC_YUG_DOOR,
            organization_id=ORG_YUG,
            full_name="Орлов Дмитрий Мастер дверей",
            skill_tags=["домофон", "дверь", "подъезд"],
            active=True,
        )
    )

    # Dispatchers
    orgs.add_dispatcher(
        DispatcherAccount(
            id=DISP_SEVER,
            username="dispatcher_sever",
            password_hash=hash_password("sever123"),
            organization_id=ORG_SEVER,
            full_name="Диспетчер Северная",
        )
    )
    orgs.add_dispatcher(
        DispatcherAccount(
            id=DISP_YUG,
            username="dispatcher_yug",
            password_hash=hash_password("yug123"),
            organization_id=ORG_YUG,
            full_name="Диспетчер Южная",
        )
    )

    session.commit()
