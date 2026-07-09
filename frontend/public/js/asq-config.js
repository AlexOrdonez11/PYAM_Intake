const ASQ_2_MONTH_SCORE_CONFIG = {
  "2-months-visit": [
    {
      key: "communication",
      label: "Communication",
      fieldPrefix: "asq_comm_",
      totalFieldId: "asq_communication_total",
      summaryFieldId: "asq_summary_communication_score",
      zoneFieldId: "asq_communication_zone",
      cutoff: 22.77,
      zones: { belowMax: 20, monitorMax: 35 }
    },
    {
      key: "gross_motor",
      label: "Gross Motor",
      fieldPrefix: "asq_gross_",
      totalFieldId: "asq_gross_motor_total",
      summaryFieldId: "asq_summary_gross_motor_score",
      zoneFieldId: "asq_gross_motor_zone",
      cutoff: 41.84,
      zones: { belowMax: 40, monitorMax: 45 }
    },
    {
      key: "fine_motor",
      label: "Fine Motor",
      fieldPrefix: "asq_fine_",
      totalFieldId: "asq_fine_motor_total",
      summaryFieldId: "asq_summary_fine_motor_score",
      zoneFieldId: "asq_fine_motor_zone",
      cutoff: 30.16,
      zones: { belowMax: 30, monitorMax: 40 }
    },
    {
      key: "problem_solving",
      label: "Problem Solving",
      fieldPrefix: "asq_problem_",
      totalFieldId: "asq_problem_solving_total",
      summaryFieldId: "asq_summary_problem_solving_score",
      zoneFieldId: "asq_problem_solving_zone",
      cutoff: 24.62,
      zones: { belowMax: 20, monitorMax: 35 }
    },
    {
      key: "personal_social",
      label: "Personal-Social",
      fieldPrefix: "asq_social_",
      totalFieldId: "asq_personal_social_total",
      summaryFieldId: "asq_summary_personal_social_score",
      zoneFieldId: "asq_personal_social_zone",
      cutoff: 33.71,
      zones: { belowMax: 30, monitorMax: 40 }
    }
  ],
  "2-year-visit-maplewood": [
    {
      key: "communication",
      label: "Communication",
      fieldPrefix: "asq24_comm_",
      totalFieldId: "asq24_communication_total",
      summaryFieldId: "asq24_summary_communication_score",
      zoneFieldId: "asq24_communication_zone",
      cutoff: 25.17,
      zones: { belowMax: 25, monitorMax: 35 }
    },
    {
      key: "gross_motor",
      label: "Gross Motor",
      fieldPrefix: "asq24_gross_",
      totalFieldId: "asq24_gross_motor_total",
      summaryFieldId: "asq24_summary_gross_motor_score",
      zoneFieldId: "asq24_gross_motor_zone",
      cutoff: 38.07,
      zones: { belowMax: 35, monitorMax: 45 }
    },
    {
      key: "fine_motor",
      label: "Fine Motor",
      fieldPrefix: "asq24_fine_",
      totalFieldId: "asq24_fine_motor_total",
      summaryFieldId: "asq24_summary_fine_motor_score",
      zoneFieldId: "asq24_fine_motor_zone",
      cutoff: 35.16,
      zones: { belowMax: 35, monitorMax: 40 }
    },
    {
      key: "problem_solving",
      label: "Problem Solving",
      fieldPrefix: "asq24_problem_",
      totalFieldId: "asq24_problem_solving_total",
      summaryFieldId: "asq24_summary_problem_solving_score",
      zoneFieldId: "asq24_problem_solving_zone",
      cutoff: 29.78,
      zones: { belowMax: 25, monitorMax: 35 }
    },
    {
      key: "personal_social",
      label: "Personal-Social",
      fieldPrefix: "asq24_social_",
      totalFieldId: "asq24_personal_social_total",
      summaryFieldId: "asq24_summary_personal_social_score",
      zoneFieldId: "asq24_personal_social_zone",
      cutoff: 31.54,
      zones: { belowMax: 30, monitorMax: 40 }
    }
  ]
};

function buildAsqScoreConfig(prefix, cutoffs, zones) {
  const areas = [
    ["communication", "Communication", "communication", "communication", "communication"],
    ["gross_motor", "Gross Motor", "gross", "gross", "gross_motor"],
    ["fine_motor", "Fine Motor", "fine", "fine", "fine_motor"],
    ["problem_solving", "Problem Solving", "problem", "problem", "problem_solving"],
    ["personal_social", "Personal-Social", "social", "social", "personal_social"]
  ];

  return areas.map(([key, label, answerKey, totalKey, summaryKey]) => ({
    key,
    label,
    fieldPrefix: `${prefix}_${answerKey}_`,
    totalFieldId: `${prefix}_${totalKey}_total`,
    summaryFieldId: `${prefix}_summary_${summaryKey}_score`,
    zoneFieldId: `${prefix}_${summaryKey}_zone`,
    cutoff: cutoffs[key],
    zones: zones[key]
  }));
}

ASQ_2_MONTH_SCORE_CONFIG["2-year-visit-eagan"] = ASQ_2_MONTH_SCORE_CONFIG["2-year-visit-maplewood"];
ASQ_2_MONTH_SCORE_CONFIG["4-months-visit"] = buildAsqScoreConfig(
  "asq4",
  { communication: 34.6, gross_motor: 38.41, fine_motor: 29.62, problem_solving: 34.98, personal_social: 33.16 },
  {
    communication: { belowMax: 30, monitorMax: 40 },
    gross_motor: { belowMax: 35, monitorMax: 45 },
    fine_motor: { belowMax: 25, monitorMax: 40 },
    problem_solving: { belowMax: 30, monitorMax: 45 },
    personal_social: { belowMax: 30, monitorMax: 40 }
  }
);
ASQ_2_MONTH_SCORE_CONFIG["6-months-visit"] = buildAsqScoreConfig(
  "asq6",
  { communication: 29.65, gross_motor: 22.25, fine_motor: 25.14, problem_solving: 27.72, personal_social: 25.34 },
  {
    communication: { belowMax: 25, monitorMax: 40 },
    gross_motor: { belowMax: 20, monitorMax: 35 },
    fine_motor: { belowMax: 25, monitorMax: 40 },
    problem_solving: { belowMax: 25, monitorMax: 35 },
    personal_social: { belowMax: 25, monitorMax: 35 }
  }
);
ASQ_2_MONTH_SCORE_CONFIG["7-8-months-visit"] = buildAsqScoreConfig(
  "asq8",
  { communication: 33.06, gross_motor: 30.61, fine_motor: 40.15, problem_solving: 36.17, personal_social: 35.84 },
  {
    communication: { belowMax: 30, monitorMax: 40 },
    gross_motor: { belowMax: 30, monitorMax: 35 },
    fine_motor: { belowMax: 40, monitorMax: 45 },
    problem_solving: { belowMax: 35, monitorMax: 40 },
    personal_social: { belowMax: 35, monitorMax: 40 }
  }
);
ASQ_2_MONTH_SCORE_CONFIG["9-months-visit"] = buildAsqScoreConfig(
  "asq9",
  { communication: 13.97, gross_motor: 17.82, fine_motor: 31.32, problem_solving: 28.72, personal_social: 18.91 },
  {
    communication: { belowMax: 10, monitorMax: 30 },
    gross_motor: { belowMax: 15, monitorMax: 30 },
    fine_motor: { belowMax: 30, monitorMax: 40 },
    problem_solving: { belowMax: 25, monitorMax: 40 },
    personal_social: { belowMax: 15, monitorMax: 30 }
  }
);
ASQ_2_MONTH_SCORE_CONFIG["10-months-visit"] = buildAsqScoreConfig(
  "asq10",
  { communication: 22.87, gross_motor: 30.07, fine_motor: 37.97, problem_solving: 32.51, personal_social: 27.25 },
  {
    communication: { belowMax: 20, monitorMax: 35 },
    gross_motor: { belowMax: 30, monitorMax: 40 },
    fine_motor: { belowMax: 35, monitorMax: 45 },
    problem_solving: { belowMax: 30, monitorMax: 40 },
    personal_social: { belowMax: 25, monitorMax: 35 }
  }
);
ASQ_2_MONTH_SCORE_CONFIG["12-months-visit-eagan"] = buildAsqScoreConfig(
  "asq12",
  { communication: 15.64, gross_motor: 21.49, fine_motor: 34.5, problem_solving: 27.32, personal_social: 21.73 },
  {
    communication: { belowMax: 15, monitorMax: 30 },
    gross_motor: { belowMax: 20, monitorMax: 35 },
    fine_motor: { belowMax: 30, monitorMax: 40 },
    problem_solving: { belowMax: 25, monitorMax: 35 },
    personal_social: { belowMax: 20, monitorMax: 35 }
  }
);
ASQ_2_MONTH_SCORE_CONFIG["12-months-visit-maplewood"] = ASQ_2_MONTH_SCORE_CONFIG["12-months-visit-eagan"];
ASQ_2_MONTH_SCORE_CONFIG["14-months-visit"] = buildAsqScoreConfig(
  "asq14",
  { communication: 17.4, gross_motor: 25.8, fine_motor: 23.06, problem_solving: 22.56, personal_social: 23.18 },
  {
    communication: { belowMax: 15, monitorMax: 30 },
    gross_motor: { belowMax: 25, monitorMax: 40 },
    fine_motor: { belowMax: 20, monitorMax: 35 },
    problem_solving: { belowMax: 20, monitorMax: 35 },
    personal_social: { belowMax: 20, monitorMax: 35 }
  }
);
ASQ_2_MONTH_SCORE_CONFIG["3-year-visit"] = buildAsqScoreConfig(
  "asq36",
  { communication: 30.99, gross_motor: 36.99, fine_motor: 18.07, problem_solving: 30.29, personal_social: 35.33 },
  {
    communication: { belowMax: 30, monitorMax: 40 },
    gross_motor: { belowMax: 35, monitorMax: 45 },
    fine_motor: { belowMax: 15, monitorMax: 30 },
    problem_solving: { belowMax: 30, monitorMax: 40 },
    personal_social: { belowMax: 35, monitorMax: 45 }
  }
);
ASQ_2_MONTH_SCORE_CONFIG["4-year-visit"] = buildAsqScoreConfig(
  "asq48",
  { communication: 30.72, gross_motor: 32.78, fine_motor: 15.81, problem_solving: 31.3, personal_social: 26.6 },
  {
    communication: { belowMax: 30, monitorMax: 40 },
    gross_motor: { belowMax: 30, monitorMax: 40 },
    fine_motor: { belowMax: 15, monitorMax: 30 },
    problem_solving: { belowMax: 30, monitorMax: 40 },
    personal_social: { belowMax: 25, monitorMax: 35 }
  }
);
ASQ_2_MONTH_SCORE_CONFIG["5-year-visit"] = buildAsqScoreConfig(
  "asq60",
  { communication: 33.19, gross_motor: 31.28, fine_motor: 26.54, problem_solving: 29.99, personal_social: 39.07 },
  {
    communication: { belowMax: 30, monitorMax: 40 },
    gross_motor: { belowMax: 30, monitorMax: 40 },
    fine_motor: { belowMax: 25, monitorMax: 35 },
    problem_solving: { belowMax: 25, monitorMax: 40 },
    personal_social: { belowMax: 35, monitorMax: 45 }
  }
);

