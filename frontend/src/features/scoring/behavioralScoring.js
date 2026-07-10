function optionScore(value) {
  if (value === "Somewhat") return 1;
  if (value === "Very much") return 2;
  const match = String(value || "").match(/\((\d+)\)/);
  return match ? Number(match[1]) : 0;
}

function yesCount(answers, keys) {
  return keys.reduce((total, key) => total + (answers[key] === "Yes" ? 1 : 0), 0);
}

function optionSum(answers, prefix, keys) {
  return keys.reduce((total, key) => total + optionScore(answers[`${prefix}_${key}`]), 0);
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
