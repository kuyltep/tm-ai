from typing import List, Literal, Annotated
from pydantic import BaseModel, Field

LimitStr = Annotated[str, Field(max_length=300)]
#
QuoteStr = Annotated[str, Field(max_length=200)]


class InputArtifacts(BaseModel):
    has_audio: bool
    has_transcript: bool
    transcript_source: LimitStr

class Privacy(BaseModel):
    anonymization_applied: bool
    allowed_personal_data: LimitStr
    company_names_policy: LimitStr

class ReportMetadata(BaseModel):
    candidate_id: LimitStr
    position_profile: LimitStr
    interview_date: LimitStr
    language: LimitStr
    input_artifacts: InputArtifacts
    privacy: Privacy

class HeaderSummary(BaseModel):
    candidate_name: LimitStr
    match_percentage: int = Field(ge=0, le=100)
    verdict_status: Literal["Не рекомендован", "С рисками", "Рекомендован", "не раскрыто"]
    verdict_color: Literal["red", "yellow", "green", "не раскрыто"]

class CandidateProfileCard(BaseModel):
    experience_years: LimitStr
    companies_type: LimitStr
    salary_request: LimitStr
    work_format: LimitStr
    expectations_from_future_job: LimitStr


class DecisionBlock(BaseModel):
    final_decision: Literal["Не рекомендован", "С рисками", "Рекомендован", "не раскрыто"]
    arguments_pros: List[LimitStr] = Field(max_length=3)
    arguments_cons: List[LimitStr] = Field(max_length=3)

class RiskCard(BaseModel):
    severity: Literal["Critical", "Alert", "Low", "не раскрыто"]
    title: LimitStr
    description: LimitStr

class StrengthCard(BaseModel):
    title: LimitStr
    description: LimitStr
    quote: QuoteStr

class RiskAnalysis(BaseModel):
    risk_cards: List[RiskCard] = Field(max_length=3)
    strengths_cards: List[StrengthCard] = Field(max_length=3)


class AudioMarker(BaseModel):
    marker: Literal[
        "tempo", "pauses_hesitations", "intonation_variability", 
        "voice_tension_breathing", "dominance_interruptions", "latency_before_answer"
    ]
    value: Literal[
        "slow", "medium", "fast", "variable", 
        "rare", "normal", "frequent", 
        "low", "high", 
        "none", "occasional", 
        "short", "long", 
        "не раскрыто"
    ]
    impact: LimitStr
    evidence_quotes: List[QuoteStr]

class ToneAudio(BaseModel):
    overall_impression: LimitStr
    audio_markers: List[AudioMarker]

class Tone(BaseModel):
    tone_textual: LimitStr
    tone_audio: ToneAudio

class QuotesPolicy(BaseModel):
    quotes_source: LimitStr
    if_no_transcript: LimitStr

class Psycholinguistics(BaseModel):
    ego_slider_value: int = Field(ge=0, le=100)
    ego_label_left: LimitStr
    ego_label_right: LimitStr
    ego_description: LimitStr
    locus_of_control: LimitStr
    locus_description: LimitStr
    tone: Tone
    key_quotes: List[QuoteStr] = Field(max_length=2)
    quotes_policy: QuotesPolicy


class TopRiskList(BaseModel):
    skill: LimitStr
    gap_percent: int
    reason: LimitStr

class RadarChartData(BaseModel):
    average_gap: int
    top_risks_list: List[TopRiskList] = Field(max_length=3)
    closest_match_text: LimitStr


class ChartData(BaseModel):
    candidate: int = Field(ge=0, le=100)
    benchmark: int = Field(ge=0, le=100) 

class AudioObservation(BaseModel):
    signal: LimitStr
    value: LimitStr
    impact_on_skill: LimitStr
    supporting_quotes: List[QuoteStr] = Field(max_length=2)

class AudioObservationsSummary(BaseModel):
    summary: LimitStr
    observations: List[AudioObservation] = Field(max_length=2)

class ModalContent(BaseModel):
    benchmark_text: LimitStr
    gap_analysis: LimitStr
    why_not_higher: LimitStr
    why_not_lower: LimitStr
    chart_data: ChartData
    evidence_quotes: List[QuoteStr] = Field(min_length=1, max_length=2)
    audio_observations: AudioObservationsSummary

class SoftSkillDetailed(BaseModel):
    id: LimitStr
    name: LimitStr
    score: int = Field(ge=0, le=100)
    short_summary: LimitStr
    modal_content: ModalContent


class AiAssessment(BaseModel):
    text: LimitStr
    sentiment: Literal["positive", "neutral", "negative", "не раскрыто"]

class StarCase(BaseModel):
    title: LimitStr
    situation: LimitStr
    task: LimitStr
    action: LimitStr
    result: LimitStr
    ai_assessment: AiAssessment

class ThemeToClarify(BaseModel):
    theme: LimitStr
    why: LimitStr
    risk_if_unchecked: LimitStr
    questions: List[LimitStr]
    what_good_looks_like: LimitStr
    red_flags: LimitStr

class ManagementGuide(BaseModel):
    title: LimitStr
    themes_to_clarify: List[ThemeToClarify] = Field(max_length=4)


class InterviewAnalysisResponse(BaseModel):
    report_metadata: ReportMetadata
    header_summary: HeaderSummary
    candidate_profile_card: CandidateProfileCard
    decision_block: DecisionBlock
    risk_analysis: RiskAnalysis
    psycholinguistics: Psycholinguistics
    radar_chart_data: RadarChartData
    soft_skills_detailed: List[SoftSkillDetailed]
    star_cases: List[StarCase] = Field(max_length=2)
    management_guide: ManagementGuide