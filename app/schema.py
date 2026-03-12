from pydantic import BaseModel
from typing import List


class Assumption(BaseModel):
    text: str


class Competitor(BaseModel):
    name: str
    strength: str


class Risk(BaseModel):
    risk: str
    severity: str


class Factor(BaseModel):
    factor: str
    impact: str


class Feature(BaseModel):
    name: str


class PRDCriteria(BaseModel):
    text: str


class PRDStory(BaseModel):
    id: str
    title: str
    persona: str
    want: str
    so: str
    criteria: List[str]


class ArchitectureComponent(BaseModel):
    name: str
    description: str


class EdgeCase(BaseModel):
    id: str
    category: str
    severity: str
    description: str
    mitigation: str


class Experiment(BaseModel):
    experiment: str
    metric: str
    timeline: str


class IdeaInterpretation(BaseModel):
    summary: str
    coreValue: str
    targetUser: str
    keyAssumptions: List[str]


class MarketReality(BaseModel):
    marketSize: str
    competitors: List[Competitor]
    trends: List[str]
    risks: List[Risk]


class MoatAnalysis(BaseModel):
    differentiators: List[str]
    barriers: List[str]
    sustainability: str


class ConfidenceScore(BaseModel):
    score: int
    factors: List[Factor]


class ProductBlueprint(BaseModel):
    core_features: List[str]


class PRD(BaseModel):
    stories: List[PRDStory]


class Architecture(BaseModel):
    components: List[ArchitectureComponent]
    dataFlow: List[str]
    scaleTriggers: List[str]


class Security(BaseModel):
    considerations: List[str]
    compliance: List[str]
    governance: List[str]


class Validation(BaseModel):
    experiments: List[Experiment]
    successCriteria: List[str]


class Blueprint(BaseModel):
    idea_interpretation: IdeaInterpretation
    market_reality: MarketReality
    moat_analysis: MoatAnalysis
    confidence_score: ConfidenceScore
    product_blueprint: ProductBlueprint
    prd: PRD
    architecture: Architecture
    security: Security
    edge_cases: List[EdgeCase]
    validation: Validation
