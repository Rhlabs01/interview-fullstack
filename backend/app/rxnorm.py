"""RxNorm integration.

Three paths are provided:

1. ``local_lookup`` — resolve a name against the seeded ``medications`` catalog
   (exact / case-insensitive on the normalized name, brand names, or synonym).
2. ``live_lookup`` — call the public RxNav REST API for anything not cached.
3. ``scrape_concept`` — build a full catalog entry (properties, single-ingredient
   brand names, pharmacologic class) from RxNav, used by the catalog scraper.

All return normalized, structured attributes (rxcui, name, term type, brand
names, drug class). The catalog is **ingredient** concepts only (``tty=IN``).
Strength and dose form live on more specific RxNorm term types (SCD / SBD);
those are not stored locally. See EXERCISE.md if you take that stretch.

Note for candidates: this exposes *exact* normalized lookups only. Fuzzy
matching (misspellings, shorthand, alternative names) is part of the exercise —
see EXERCISE.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Medication


@dataclass
class MedicationInfo:
    rxcui: str
    name: str
    tty: str
    synonym: str | None = None
    brand_names: list[str] = field(default_factory=list)
    drug_class: str | None = None
    source: str = "catalog"  # "catalog" | "rxnav"

    def to_dict(self) -> dict:
        return {
            "rxcui": self.rxcui,
            "name": self.name,
            "tty": self.tty,
            "synonym": self.synonym,
            "brand_names": self.brand_names,
            "drug_class": self.drug_class,
            "source": self.source,
        }


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def medication_to_info(medication: Medication, source: str = "catalog") -> MedicationInfo:
    return MedicationInfo(
        rxcui=medication.rxcui,
        name=medication.name,
        tty=medication.tty,
        synonym=medication.synonym,
        brand_names=_split_csv(medication.brand_names),
        drug_class=medication.drug_class,
        source=source,
    )


def local_lookup(db: Session, name: str) -> MedicationInfo | None:
    """Case-insensitive exact match against the seeded catalog.

    Matches the normalized name, the synonym, or any brand name. Does not do
    fuzzy/approximate matching.
    """
    query = (name or "").strip()
    if not query:
        return None

    lowered = query.lower()

    # Match on normalized name or synonym.
    row = (
        db.query(Medication)
        .filter(
            (func.lower(Medication.name) == lowered)
            | (func.lower(Medication.synonym) == lowered)
        )
        .first()
    )
    if row is not None:
        return medication_to_info(row)

    # Match on a brand name (stored comma-separated).
    for medication in db.query(Medication).all():
        brands = [brand.lower() for brand in _split_csv(medication.brand_names)]
        if lowered in brands:
            return medication_to_info(medication)

    return None


def live_lookup(name: str) -> MedicationInfo | None:
    """Look a medication up on the public RxNav REST API.

    Best-effort: returns ``None`` on any network/parse error so callers can
    degrade gracefully (and so tests never depend on the network).
    """
    query = (name or "").strip()
    if not query:
        return None

    try:
        import httpx
    except ImportError:  # pragma: no cover - httpx is a declared dependency
        return None

    base = get_settings().rxnav_base_url.rstrip("/")

    try:
        with httpx.Client(timeout=5.0) as client:
            rxcui_resp = client.get(f"{base}/rxcui.json", params={"name": query})
            rxcui_resp.raise_for_status()
            rxcui_ids = (
                rxcui_resp.json().get("idGroup", {}).get("rxnormId", []) or []
            )
            if not rxcui_ids:
                return None
            rxcui = rxcui_ids[0]

            props_resp = client.get(f"{base}/rxcui/{rxcui}/properties.json")
            props_resp.raise_for_status()
            props = props_resp.json().get("properties", {}) or {}

            brand_names = _live_brand_names(client, base, rxcui)

        return MedicationInfo(
            rxcui=str(rxcui),
            name=props.get("name") or query,
            tty=props.get("tty") or "",
            synonym=props.get("synonym") or None,
            brand_names=brand_names,
            drug_class=None,
            source="rxnav",
        )
    except Exception:
        return None


def _live_brand_names(client, base: str, rxcui: str) -> list[str]:
    try:
        resp = client.get(
            f"{base}/rxcui/{rxcui}/related.json", params={"tty": "BN"}
        )
        resp.raise_for_status()
        groups = resp.json().get("relatedGroup", {}).get("conceptGroup", []) or []
        brands: list[str] = []
        for group in groups:
            for concept in group.get("conceptProperties", []) or []:
                brand = concept.get("name")
                if brand:
                    brands.append(brand)
        return brands
    except Exception:
        return []


def lookup(db: Session, name: str) -> MedicationInfo | None:
    """Resolve a normalized medication name: catalog first, then live RxNav."""
    return local_lookup(db, name) or live_lookup(name)


# ---------------------------------------------------------------------------
# Catalog scraping
#
# The reference catalog can be (re)built from the live RxNav API instead of the
# hand-written seed list. For each ingredient name we pull:
#   * the RxCUI and its normalized properties (name, term type, synonym),
#   * brand names, filtered down to *single-ingredient* brands (so metformin
#     yields "Glucophage", not the dozen combination products it appears in),
#   * an Established Pharmacologic Class from DailyMed, falling back to ATC.
# ---------------------------------------------------------------------------

# Brand-name verification costs one request per candidate, so bound the fan-out.
# RxNav asks for <= 20 requests/second, and a scrape runs ``_SCRAPE_WORKERS``
# concepts at once, each with its own brand pool — keep the product under that.
MAX_BRAND_CANDIDATES = 60
MAX_BRAND_NAMES = 12
_BRAND_WORKERS = 4
_SCRAPE_WORKERS = 4


def _get_json(client, url: str, params: dict | None = None) -> dict:
    resp = client.get(url, params=params)
    resp.raise_for_status()
    return resp.json()


def _concepts(payload: dict) -> list[dict]:
    groups = payload.get("relatedGroup", {}).get("conceptGroup", []) or []
    return [
        concept
        for group in groups
        for concept in (group.get("conceptProperties") or [])
    ]


def _single_ingredient_brands(client, base: str, rxcui: str) -> list[str]:
    """Brand names whose only active ingredient is ``rxcui``.

    RxNav's ``related?tty=BN`` returns every brand that *contains* the
    ingredient, including combination products. Each candidate is checked back
    against its own ingredient list and kept only if that list is exactly this
    one concept.
    """
    from concurrent.futures import ThreadPoolExecutor

    try:
        candidates = _concepts(
            _get_json(client, f"{base}/rxcui/{rxcui}/related.json", {"tty": "BN"})
        )[:MAX_BRAND_CANDIDATES]
    except Exception:
        return []

    if not candidates:
        return []

    def ingredients_of(brand: dict) -> set[str]:
        try:
            payload = _get_json(
                client, f"{base}/rxcui/{brand['rxcui']}/related.json", {"tty": "IN"}
            )
            return {concept["rxcui"] for concept in _concepts(payload)}
        except Exception:
            return set()

    with ThreadPoolExecutor(max_workers=_BRAND_WORKERS) as pool:
        ingredient_sets = list(pool.map(ingredients_of, candidates))

    brands = [
        candidate["name"]
        for candidate, ingredients in zip(candidates, ingredient_sets)
        if ingredients == {rxcui} and candidate.get("name")
    ]
    return brands[:MAX_BRAND_NAMES]


def _drug_class(client, base: str, rxcui: str) -> str | None:
    """Best-available pharmacologic class: DailyMed EPC, else ATC."""
    for source, class_types in (("DAILYMED", {"EPC"}), ("ATC", {"ATC1-4"})):
        try:
            payload = _get_json(
                client,
                f"{base}/rxclass/class/byRxcui.json",
                {"rxcui": rxcui, "relaSource": source},
            )
        except Exception:
            continue
        entries = (
            payload.get("rxclassDrugInfoList", {}).get("rxclassDrugInfo", []) or []
        )
        for entry in entries:
            item = entry.get("rxclassMinConceptItem", {}) or {}
            # Only keep classes asserted against this exact concept — the same
            # response also carries classes for combination products.
            if entry.get("minConcept", {}).get("rxcui") != rxcui:
                continue
            if item.get("classType") in class_types and item.get("className"):
                return item["className"]
    return None


def scrape_concept(name: str) -> MedicationInfo | None:
    """Build a full catalog entry for ``name`` from the live RxNav API.

    Returns ``None`` if the name does not resolve or the network is unavailable,
    so a partial scrape degrades to "this one failed" rather than a 500.
    """
    query = (name or "").strip()
    if not query:
        return None

    try:
        import httpx
    except ImportError:  # pragma: no cover - httpx is a declared dependency
        return None

    base = get_settings().rxnav_base_url.rstrip("/")

    try:
        with httpx.Client(timeout=10.0) as client:
            ids = (
                _get_json(client, f"{base}/rxcui.json", {"name": query})
                .get("idGroup", {})
                .get("rxnormId", [])
                or []
            )
            if not ids:
                return None
            rxcui = str(ids[0])

            props = (
                _get_json(client, f"{base}/rxcui/{rxcui}/properties.json").get(
                    "properties", {}
                )
                or {}
            )
            brand_names = _single_ingredient_brands(client, base, rxcui)
            drug_class = _drug_class(client, base, rxcui)
    except Exception:
        return None

    return MedicationInfo(
        rxcui=rxcui,
        name=props.get("name") or query,
        tty=props.get("tty") or "",
        synonym=props.get("synonym") or None,
        brand_names=brand_names,
        drug_class=drug_class,
        source="rxnav",
    )


def scrape_concepts(names: list[str]) -> list[MedicationInfo | None]:
    """Scrape several names at once, preserving input order.

    Network only — no database access — so the caller can fan out here and then
    write the results from a single thread (a SQLAlchemy ``Session`` is not
    thread-safe).
    """
    from concurrent.futures import ThreadPoolExecutor

    if not names:
        return []
    with ThreadPoolExecutor(max_workers=_SCRAPE_WORKERS) as pool:
        return list(pool.map(scrape_concept, names))


def upsert_medication(db: Session, info: MedicationInfo) -> bool:
    """Insert or refresh a catalog row. Returns True if the row was created."""
    row = db.get(Medication, info.rxcui)
    created = row is None
    if row is None:
        row = Medication(rxcui=info.rxcui)
        db.add(row)

    row.name = info.name
    row.tty = info.tty or row.tty or "IN"
    row.synonym = info.synonym
    row.brand_names = ",".join(info.brand_names) or None
    row.drug_class = info.drug_class
    return created
