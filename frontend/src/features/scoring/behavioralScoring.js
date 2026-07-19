function optionScore(value) {
  if (value === "Somewhat") return 1;
  if (value === "Very much") return 2;
  const match = String(value || "").match(/\((\d+)\)/);
  if (match) return Number(match[1]);
  const leadingScore = String(value || "").match(/^(\d+)\s*-/);
  return leadingScore ? Number(leadingScore[1]) : 0;
}

function yesCount(answers, keys) {
  return keys.reduce((total, key) => total + (answers[key] === "Yes" ? 1 : 0), 0);
}

function optionSum(answers, prefix, keys) {
  return keys.reduce((total, key) => total + optionScore(answers[`${prefix}_${key}`]), 0);
}

function indexedScore(answers, key, options, base = 0) {
  const index = options.indexOf(answers[key]);
  return index >= 0 ? index + base : null;
}

function reverseIndexedScore(answers, key, options, topScore) {
  const index = options.indexOf(answers[key]);
  return index >= 0 ? topScore - index : null;
}

function sumNullable(scores) {
  return scores.some((score) => score !== null) ? scores.reduce((total, score) => total + (score || 0), 0) : null;
}

function rangeKeys(prefix, start, end) {
  return Array.from({ length: end - start + 1 }, (_, index) => `${prefix}_${String(start + index).padStart(2, "0")}`);
}

function countAtLeast(answers, keys, threshold) {
  return keys.reduce((total, key) => total + (optionScore(answers[key]) >= threshold ? 1 : 0), 0);
}

function addVanderbiltScores(next, answers, prefix, config) {
  if (!rangeKeys(prefix, 1, config.symptomEnd).some((key) => answers[key])) return;

  for (const [key, start, end] of config.domains) {
    next[`${prefix}_${key}`] = String(countAtLeast(answers, rangeKeys(prefix, start, end), 2));
  }

  const performanceKeys = Array.from({ length: config.performanceCount }, (_, index) => `${prefix}_performance_${String(index + 1).padStart(2, "0")}`);
  const performance4 = countAtLeast(answers, performanceKeys, 4);
  const performance5 = performanceKeys.reduce((total, key) => total + (optionScore(answers[key]) === 5 ? 1 : 0), 0);
  next[`${prefix}_performance_4_count`] = String(performance4 - performance5);
  next[`${prefix}_performance_5_count`] = String(performance5);
  next[`${prefix}_impairment_present`] = performance4 > 0 ? "Yes" : "No";
}

function scaredScore(answers, prefix, items) {
  return items.reduce((total, item) => total + optionScore(answers[`${prefix}_${String(item).padStart(2, "0")}`]), 0);
}

function addScaredScores(next, answers, prefix) {
  if (!rangeKeys(prefix, 1, 41).some((key) => answers[key])) return;

  const panic = scaredScore(answers, prefix, [1, 6, 9, 12, 15, 18, 19, 22, 24, 27, 30, 34, 38]);
  const generalized = scaredScore(answers, prefix, [5, 7, 14, 21, 23, 28, 33, 35, 37]);
  const separation = scaredScore(answers, prefix, [4, 8, 13, 16, 20, 25, 29, 31]);
  const social = scaredScore(answers, prefix, [3, 10, 26, 32, 39, 40, 41]);
  const school = scaredScore(answers, prefix, [2, 11, 17, 36]);
  const total = rangeKeys(prefix, 1, 41).reduce((sum, key) => sum + optionScore(answers[key]), 0);

  next[`${prefix}_total_score`] = String(total);
  next[`${prefix}_panic_somatic_score`] = String(panic);
  next[`${prefix}_generalized_anxiety_score`] = String(generalized);
  next[`${prefix}_separation_anxiety_score`] = String(separation);
  next[`${prefix}_social_anxiety_score`] = String(social);
  next[`${prefix}_school_avoidance_score`] = String(school);
  next[`${prefix}_total_cutoff_met`] = total >= 25 ? "Yes" : "No";
  next[`${prefix}_panic_somatic_cutoff_met`] = panic >= 7 ? "Yes" : "No";
  next[`${prefix}_generalized_anxiety_cutoff_met`] = generalized >= 9 ? "Yes" : "No";
  next[`${prefix}_separation_anxiety_cutoff_met`] = separation >= 5 ? "Yes" : "No";
  next[`${prefix}_social_anxiety_cutoff_met`] = social >= 8 ? "Yes" : "No";
  next[`${prefix}_school_avoidance_cutoff_met`] = school >= 3 ? "Yes" : "No";
}

function asrsPositive(key, value) {
  if (!value) return false;
  const positiveFromSometimes = new Set(["wrap_up", "organization", "remembering"]);
  const index = ["Never", "Rarely", "Sometimes", "Often", "Very often"].indexOf(value);
  if (index < 0) return false;
  return positiveFromSometimes.has(key) ? index >= 2 : index >= 3;
}

function addAsrsScores(next, answers) {
  const partA = ["wrap_up", "organization", "remembering", "avoid_delay", "fidget", "driven"];
  const partB = ["careless_mistakes", "attention_boring_work", "concentrating_on_people", "misplace_things", "distracted_by_noise", "leave_seat", "restless", "difficulty_relaxing", "talking_too_much", "finish_sentences", "waiting_turn", "interrupt_busy"];
  if (![...partA, ...partB].some((key) => answers[key])) return;

  const partAPositive = partA.reduce((total, key) => total + (asrsPositive(key, answers[key]) ? 1 : 0), 0);
  const partBPositive = partB.reduce((total, key) => total + (asrsPositive(key, answers[key]) ? 1 : 0), 0);
  next.asrs_part_a_positive_count = String(partAPositive);
  next.asrs_part_b_positive_count = String(partBPositive);
  next.asrs_screen_result = partAPositive >= 4 ? "Positive screen" : "Negative screen";
}

function aceYesCount(answers, prefix, count) {
  return Array.from({ length: count }, (_, index) => `${prefix}_${String(index + 1).padStart(2, "0")}`).reduce((total, key) => total + (answers[key] === "Yes" ? 1 : 0), 0);
}

function addAceScores(next, answers) {
  const hasAce = Object.keys(answers).some((key) => key.startsWith("ace_physical_") || key.startsWith("ace_cognitive_") || key.startsWith("ace_emotional_") || key.startsWith("ace_sleep_"));
  if (!hasAce) return;

  const physical = aceYesCount(answers, "ace_physical", 10);
  const cognitive = aceYesCount(answers, "ace_cognitive", 4);
  const emotional = aceYesCount(answers, "ace_emotional", 4);
  const sleep = aceYesCount(answers, "ace_sleep", 4);
  const redFlags = Array.isArray(answers.ace_red_flags) ? answers.ace_red_flags.length : 0;
  next.ace_physical_total = String(physical);
  next.ace_cognitive_total = String(cognitive);
  next.ace_emotional_total = String(emotional);
  next.ace_sleep_total = String(sleep);
  next.ace_total_symptom_score = String(physical + cognitive + emotional + sleep);
  next.ace_red_flag_count = String(redFlags);
}

const EPDS_LEGACY_KEYS = [
  "epds_laugh",
  "epds_enjoyment",
  "epds_blame",
  "epds_anxious",
  "epds_scared",
  "epds_coping",
  "epds_sleeping",
  "epds_sad",
  "epds_crying",
  "epds_self_harm"
];

function epdsScoreFor(index, value) {
  if (!value) return null;
  const normalized = String(value);
  const scoring = {
    1: [
      ["As much as", 0],
      ["Not quite so much", 1],
      ["Definitely not so much", 2],
      ["Not at all", 3]
    ],
    2: [
      ["As much as", 0],
      ["Rather less", 1],
      ["Definitely less", 2],
      ["Hardly at all", 3]
    ],
    3: [
      ["Yes, most of the time", 3],
      ["Yes, some of the time", 2],
      ["Not very often", 1],
      ["No, never", 0]
    ],
    4: [
      ["No, not at all", 0],
      ["Hardly ever", 1],
      ["Yes, sometimes", 2],
      ["Yes, very often", 3]
    ],
    5: [
      ["Yes, quite a lot", 3],
      ["Yes, sometimes", 2],
      ["No, not much", 1],
      ["No, not at all", 0]
    ],
    6: [
      ["Yes, most of the time", 3],
      ["Yes, sometimes", 2],
      ["No, most of the time", 1],
      ["No, I have been coping", 0]
    ],
    7: [
      ["Yes, most of the time", 3],
      ["Yes, sometimes", 2],
      ["Not very often", 1],
      ["No, not at all", 0]
    ],
    8: [
      ["Yes, most of the time", 3],
      ["Yes, quite often", 2],
      ["Not very often", 1],
      ["No, not at all", 0]
    ],
    9: [
      ["Yes, most of the time", 3],
      ["Yes, quite often", 2],
      ["Only occasionally", 1],
      ["No, never", 0]
    ],
    10: [
      ["Yes, quite often", 3],
      ["Sometimes", 2],
      ["Hardly ever", 1],
      ["Never", 0]
    ]
  };
  const match = scoring[index]?.find(([label]) => normalized.startsWith(label));
  return match ? match[1] : optionScore(value);
}

export function calculateEpdsTotal(answers) {
  const numberedKeys = Array.from({ length: 10 }, (_, index) => `epds_${index + 1}`);
  const keys = numberedKeys.some((key) => answers[key]) ? numberedKeys : EPDS_LEGACY_KEYS;
  const scores = keys.map((key, index) => epdsScoreFor(index + 1, answers[key]));
  return scores.some((score) => score !== null) ? scores.reduce((total, score) => total + (score || 0), 0) : null;
}

export function calculateBehavioralScores(answers) {
  const next = {};

  const epds = calculateEpdsTotal(answers);
  if (epds !== null) {
    next.epds_total_score = String(epds);
  }

  const phq2Scores = [
    optionScore(answers.phq2_interest),
    optionScore(answers.phq2_down_depressed)
  ];
  const phq2 = sumNullable(phq2Scores);
  if (phq2 !== null) {
    next.phq2_total_score = String(phq2);
  }

  const actScores = [
    indexedScore(answers, "activity_limit", ["All of the time", "Most of the time", "Some of the time", "A little of the time", "None of the time"], 1),
    indexedScore(answers, "shortness_breath", ["More than once a day", "Once a day", "3 to 6 times a week", "Once or twice a week", "Not at all"], 1),
    indexedScore(answers, "night_symptoms", ["4 or more nights a week", "2 or 3 nights a week", "Once a week", "Once or twice", "Not at all"], 1),
    indexedScore(answers, "rescue_inhaler", ["3 or more times per day", "1 or 2 times per day", "2 or 3 times per week", "Once a week or less", "Not at all"], 1),
    indexedScore(answers, "control_rating", ["Not controlled at all", "Poorly controlled", "Somewhat controlled", "Well controlled", "Completely controlled"], 1)
  ];
  const act = sumNullable(actScores);
  if (act !== null) {
    next.act_total_score = String(act);
    next.act_control_status = act <= 19 ? "May not be controlled" : "Likely controlled";
  }

  const cactScores = [
    indexedScore(answers, "asthma_today", ["Very bad", "Bad", "Good", "Very good"], 0),
    indexedScore(answers, "problem_when_active", ["It is a big problem", "It is a problem", "It is a little problem", "It is not a problem"], 0),
    indexedScore(answers, "cough", ["Yes, all of the time", "Yes, most of the time", "Yes, some of the time", "No, none of the time"], 0),
    indexedScore(answers, "wake_up", ["Yes, all of the time", "Yes, most of the time", "Yes, some of the time", "No, none of the time"], 0),
    reverseIndexedScore(answers, "daytime_symptoms", ["Not at all", "1-3 days", "4-10 days", "11-18 days", "19-24 days", "Every day"], 5),
    reverseIndexedScore(answers, "wheezing", ["Not at all", "1-3 days", "4-10 days", "11-18 days", "19-24 days", "Every day"], 5),
    reverseIndexedScore(answers, "night_waking", ["Not at all", "1-3 days", "4-10 days", "11-18 days", "19-24 days", "Every day"], 5)
  ];
  const cact = sumNullable(cactScores);
  if (cact !== null) {
    next.cact_total_score = String(cact);
    next.cact_control_status = cact <= 19 ? "May not be controlled" : "Likely controlled";
  }

  addVanderbiltScores(next, answers, "vanderbilt_parent", {
    symptomEnd: 48,
    performanceCount: 8,
    domains: [
      ["inattention", 1, 9],
      ["hyperactive_impulsive", 10, 18],
      ["oppositional", 19, 26],
      ["conduct", 27, 41],
      ["anxiety_depression", 42, 48]
    ]
  });
  addVanderbiltScores(next, answers, "vanderbilt_teacher", {
    symptomEnd: 35,
    performanceCount: 8,
    domains: [
      ["inattention", 1, 9],
      ["hyperactive_impulsive", 10, 18],
      ["oppositional_conduct", 19, 28],
      ["anxiety_depression", 29, 35]
    ]
  });
  addVanderbiltScores(next, answers, "vanderbilt_parent_followup", {
    symptomEnd: 26,
    performanceCount: 8,
    domains: [
      ["inattention", 1, 9],
      ["hyperactive_impulsive", 10, 18],
      ["oppositional", 19, 26]
    ]
  });
  addVanderbiltScores(next, answers, "vanderbilt_teacher_followup", {
    symptomEnd: 28,
    performanceCount: 8,
    domains: [
      ["inattention", 1, 9],
      ["hyperactive_impulsive", 10, 18],
      ["oppositional_conduct", 19, 28]
    ]
  });

  addScaredScores(next, answers, "child_scared");
  addScaredScores(next, answers, "parent_scared");
  addAsrsScores(next, answers);
  addAceScores(next, answers);

  const phqaKeys = [
    "1_depressed",
    "2_interest",
    "3_sleep",
    "4_appetite",
    "5_tired",
    "6_bad_self",
    "7_concentration",
    "8_moving",
    "9_self_harm"
  ];
  if (phqaKeys.some((key) => answers[`phqa_${key}`])) {
    next.phqa_total_score = String(optionSum(answers, "phqa", phqaKeys));
  }

  const phq9Keys = [
    "1_interest",
    "2_depressed",
    "3_sleep",
    "4_tired",
    "5_appetite",
    "6_bad_self",
    "7_concentration",
    "8_moving",
    "9_self_harm"
  ];
  if (phq9Keys.some((key) => answers[`phq9_${key}`])) {
    next.phq9_total_score = String(optionSum(answers, "phq9", phq9Keys));
  }

  const gadKeys = ["1", "2", "3", "4", "5", "6", "7"];
  if (gadKeys.some((key) => answers[`gad7_${key}`])) {
    next.gad7_total_score = String(optionSum(answers, "gad7", gadKeys));
  }

  const crafftA = ["crafft_a_alcohol", "crafft_a_marijuana", "crafft_a_other_high"];
  const crafftB = ["crafft_b_car", "crafft_b_relax", "crafft_b_alone", "crafft_b_forget", "crafft_b_family_friends", "crafft_b_trouble"];
  if ([...crafftA, ...crafftB].some((key) => answers[key])) {
    next.crafft_part_a_yes_count = String(yesCount(answers, crafftA));
    next.crafft_part_b_yes_count = String(yesCount(answers, crafftB));
  }

  const pscScore = (key) => optionScore(answers[key]);
  if (Object.keys(answers).some((key) => key.startsWith("psc17_") && /^psc17_\d+_/.test(key))) {
    const internalizing = ["psc17_2_sad", "psc17_6_hopeless", "psc17_9_down_on_self", "psc17_11_less_fun", "psc17_15_worries"];
    const attention = ["psc17_1_fidgety", "psc17_3_daydreams", "psc17_7_trouble_concentrating", "psc17_13_driven_by_motor", "psc17_17_distracted"];
    const externalizing = ["psc17_4_refuses_share", "psc17_5_does_not_understand", "psc17_8_fights", "psc17_10_blames_others", "psc17_12_does_not_listen", "psc17_14_teases", "psc17_16_takes_things"];
    const internalizingScore = internalizing.reduce((sum, key) => sum + pscScore(key), 0);
    const attentionScore = attention.reduce((sum, key) => sum + pscScore(key), 0);
    const externalizingScore = externalizing.reduce((sum, key) => sum + pscScore(key), 0);
    next.psc17_internalizing_score = String(internalizingScore);
    next.psc17_attention_score = String(attentionScore);
    next.psc17_externalizing_score = String(externalizingScore);
    next.psc17_total_score = String(internalizingScore + attentionScore + externalizingScore);
    next.psc17_internalizing_cutoff_met = internalizingScore >= 5 ? "Yes" : "No";
    next.psc17_attention_cutoff_met = attentionScore >= 7 ? "Yes" : "No";
    next.psc17_externalizing_cutoff_met = externalizingScore >= 7 ? "Yes" : "No";
    next.psc17_total_cutoff_met = internalizingScore + attentionScore + externalizingScore >= 15 ? "Yes" : "No";
  }

  const ppscKeys = Object.keys(answers).filter((key) => key.startsWith("ppsc_") && !["ppsc_child_name", "ppsc_birth_date", "ppsc_today_date", "ppsc_total_score", "ppsc_staff_notes"].includes(key));
  if (ppscKeys.some((key) => answers[key])) {
    next.ppsc_total_score = String(ppscKeys.reduce((sum, key) => sum + optionScore(answers[key]), 0));
  }

  const mchatRiskYes = new Set(["mchat_11", "mchat_18", "mchat_20", "mchat_22"]);
  const mchatKeys = Array.from({ length: 23 }, (_, index) => `mchat_${index + 1}`);
  if (mchatKeys.some((key) => answers[key])) {
    const riskScore = mchatKeys.reduce((total, key) => {
      const value = answers[key];
      if (!value) return total;
      const atRisk = mchatRiskYes.has(key) ? value === "Yes" : value === "No";
      return total + (atRisk ? 1 : 0);
    }, 0);
    next.mchat_risk_score = String(riskScore);
    next.mchat_risk_level = riskScore >= 8 ? "High risk" : riskScore >= 3 ? "Medium risk" : "Low risk";
  }

  return next;
}
