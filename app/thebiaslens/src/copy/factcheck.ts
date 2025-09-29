export const FACTCHECK_COPY = {
  // Header content
  title: 'Fact check',
  subtitle: 'External fact-checker verdicts on similar claims',
  detailedSubtitle:
    "This section finds recent fact checks about claims similar to this article's headline and shows the fact-checker's verdict so you can judge the article's core claim with more context.",
  topDisclaimer: 'From independent fact-checking organizations',
  detailedTopDisclaimer:
    'These are external verdicts on specific claims. Our bias meter estimates framing and is separate from truthfulness.',

  // Footer content
  footerDisclaimer: 'Results may address similar claims rather than this exact article.',
  detailedFooterDisclaimer:
    'Fact-checks may address a similar claim rather than this exact article. Always open the source for scope, date, and methodology.',

  // Empty state
  emptyStateText:
    'No fact checks were found that closely match this headline. Lack of a fact check does not mean the claim is accurate. Consider reading multiple sources.',

  // Link labels
  readFullCheckLabel: 'Read the review →',

  // Section labels
  verdictOnClaimLabel: 'Verdict on claim',
  claimCheckedLabel: 'Claim checked',
  relationToArticleLabel: 'Relation to this article',
  actionsLabel: 'Actions:',
  matchedPhrasesLabel: 'Matched phrases:',

  // Match reason labels (for relation badges) - Only 3 categories based on match percentage:
  // >75%: Highly related, 30-75%: Moderately related, <30%: Somewhat related
  matchReasons: {
    highly_related: 'Highly related',
    moderately_related: 'Moderately related',
    somewhat_related: 'Somewhat related',
    // Legacy fallback mappings
    headline_exact: 'Highly related',
    headline_plain: 'Moderately related',
    headline_domain: 'Somewhat related',
    summary_claim_exact: 'Highly related',
    summary_claim_terms: 'Highly related',
    summary_keyphrases: 'Moderately related',
    summary_entities: 'Moderately related',
    keyphrases: 'Somewhat related',
    entities: 'Moderately related',
    short_prefix: 'Somewhat related',
    headline: 'Highly related',
    headlineDomain: 'Somewhat related',
    keywords: 'Somewhat related',
  },

  // Verdict guidance
  verdictGuidance: {
    true: "This supports the article's core claim. Still review the source.",
    'mostly true': "This supports the article's core claim. Still review the source.",
    mixed: 'Parts are correct but important context may be missing. Read the full check.',
    'needs context': 'Parts are correct but important context may be missing. Read the full check.',
    misleading: 'Selective framing may lead to a wrong takeaway. Compare details with the article.',
    false: 'This contradicts the claim. Treat the article with caution.',
    'mostly false': 'This contradicts the claim. Treat the article with caution.',
    unverified: 'No solid evidence found. Be cautious until better sources appear.',
    unsupported: 'No solid evidence found. Be cautious until better sources appear.',
    opinion: 'Not a factual claim. Do not treat as evidence.',
    analysis: 'Not a factual claim. Do not treat as evidence.',
    satire: 'Not a factual claim. Do not treat as evidence.',
    parody: 'Not a factual claim. Do not treat as evidence.',
    unknown: 'No solid evidence found. Be cautious until better sources appear.',
  },
} as const;

export type MatchReason =
  | 'headline_exact'
  | 'headline_plain'
  | 'headline_domain'
  | 'summary_claim_exact'
  | 'summary_claim_terms'
  | 'summary_keyphrases'
  | 'summary_entities'
  | 'keyphrases'
  | 'entities'
  | 'short_prefix'
  // Legacy support
  | 'headline'
  | 'headlineDomain'
  | 'keywords';
