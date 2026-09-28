from typing import List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# websiteSettings/main
# ---------------------------------------------------------------------------
class WebsiteSettings(BaseModel):
    websiteName: str = "SKULL TRADER"
    logoUrl: Optional[str] = None
    mainTelegramUrl: str = "https://t.me/+3m3_kaixDm1lOGFl"
    proofTelegramUrl: str = "https://t.me/+P-_CbZBXe6UyOGFl"
    thirdCardName: str = "SYSTEM STATUS"
    thirdCardValue: str = "--"
    # Per-session starting capital used for public P/L % (admin-configurable)
    startingBalancePerSession: float = 30.0
    # Public hero headline (font/colors fixed in CSS; text from admin/sheet)
    challengeHeroMain: str = "30 DAYS TRADING"
    challengeHeroAccent: str = "CHALLENGE"


# ---------------------------------------------------------------------------
# dashboard/main
# ---------------------------------------------------------------------------
class Dashboard(BaseModel):
    totalPnl: float = 0
    pnlPercentage: float = 0
    thirdCardValue: str = "--"


# ---------------------------------------------------------------------------
# challengeEntries/{id}
# ---------------------------------------------------------------------------
class ChallengeEntry(BaseModel):
    id: Optional[str] = None
    date: str  # ISO format, e.g. 2026-09-13
    displayDate: Optional[str] = None
    session1Result: float = 0
    session1ProofUrl: Optional[str] = None
    session2Result: float = 0
    session2ProofUrl: Optional[str] = None
    session3Result: float = 0
    session3ProofUrl: Optional[str] = None
    totalPnl: float = 0


class ChallengeEntryCreate(BaseModel):
    date: str
    # Display label for the site (e.g. "Sep 19"). Was missing here before, so
    # the sheet sync / admin panel silently lost it on every POST/PUT.
    displayDate: Optional[str] = None
    session1Result: float = 0
    session1ProofUrl: Optional[str] = None
    session2Result: float = 0
    session2ProofUrl: Optional[str] = None
    session3Result: float = 0
    session3ProofUrl: Optional[str] = None
    totalPnl: Optional[float] = None  # auto-computed if not provided


# ---------------------------------------------------------------------------
# aboutTrading/main
# ---------------------------------------------------------------------------
class InlineStat(BaseModel):
    statNumber: str
    statDesc: str


class MatrixStat(BaseModel):
    label: str
    value: str


class Pillar(BaseModel):
    number: str
    icon: Optional[str] = None
    title: str
    text: str


class AboutTrading(BaseModel):
    heroBadge: str = "INSTITUTIONAL TRADING FRAMEWORK"
    heroTitle: str = "ABOUT SKULL TRADER"
    heroSubtitle: str = "Trading with discipline. Strategy with purpose."
    coreTitle: str = "A Precision-Driven Trading Model"
    coreParagraphs: List[str] = Field(default_factory=list)
    inlineStats: List[InlineStat] = Field(default_factory=list)
    matrixStats: List[MatrixStat] = Field(default_factory=list)
    checklistItems: List[str] = Field(default_factory=list)
    pillars: List[Pillar] = Field(default_factory=list)
    philosophyQuote: str = "Consistency is built through discipline, not through luck."
    philosophyAuthor: str = "SKULL TRADER DOCTRINE"


# ---------------------------------------------------------------------------
# crypto ticker
# ---------------------------------------------------------------------------
class CryptoPrice(BaseModel):
    symbol: str
    price: str
    change: str
    isUp: bool
