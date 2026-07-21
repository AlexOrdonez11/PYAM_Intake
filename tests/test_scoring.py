import unittest

from backend.scoring import add_calculated_scores, review_for_submission


class ScoringTests(unittest.TestCase):
    def test_asq_scores_include_totals_zones_and_review_flags(self):
        answers = {
            **{f"asq6_communication_{index}": "Yes" for index in range(1, 7)},
            **{f"asq6_gross_{index}": "Not Yet" for index in range(1, 7)},
            **{f"asq6_fine_{index}": "Sometimes" for index in range(1, 7)},
            **{f"asq6_problem_{index}": "Yes" for index in range(1, 7)},
            **{f"asq6_social_{index}": "Yes" for index in range(1, 7)},
        }

        scored = add_calculated_scores("6-months-visit", answers)

        self.assertEqual(scored["asq6_communication_total"], "60")
        self.assertEqual(scored["asq6_communication_zone"], "Above cutoff")
        self.assertEqual(scored["asq6_gross_total"], "0")
        self.assertEqual(scored["asq6_gross_motor_zone"], "Delayed")
        self.assertEqual(scored["asq6_fine_total"], "30")
        self.assertEqual(scored["asq6_fine_motor_zone"], "Close to cutoff")

        review = review_for_submission({"formId": "6-months-visit", "status": "new", "answers": scored})
        self.assertEqual(review["status"], "needs-review")
        self.assertIn("1 ASQ delayed", [flag["label"] for flag in review["flags"]])
        self.assertIn("1 ASQ monitor", [flag["label"] for flag in review["flags"]])

    def test_epds_total_and_review_flag_are_calculated(self):
        answers = {
            "epds_1": "Not at all",
            "epds_2": "Hardly at all",
            "epds_3": "Yes, most of the time",
            "epds_4": "Yes, very often",
            "epds_5": "Yes, quite a lot",
            "epds_6": "Yes, most of the time",
            "epds_7": "Yes, most of the time",
            "epds_8": "Yes, most of the time",
            "epds_9": "Yes, most of the time",
            "epds_10": "Never",
        }

        scored = add_calculated_scores("1-month-visit", answers)

        self.assertEqual(scored["epds_total_score"], "27")
        review = review_for_submission({"formId": "1-month-visit", "status": "new", "answers": scored})
        self.assertIn("EPDS elevated", [flag["label"] for flag in review["flags"]])

    def test_phq_gad_crafft_and_mchat_scores_and_flags_are_calculated(self):
        answers = {
            "phq2_interest": "Several days (1)",
            "phq2_down_depressed": "More than half the days (2)",
            "phq9_1_interest": "More than half the days (2)",
            "phq9_2_depressed": "More than half the days (2)",
            "phq9_3_sleep": "More than half the days (2)",
            "phq9_4_tired": "More than half the days (2)",
            "phq9_5_appetite": "More than half the days (2)",
            "phq9_6_bad_self": "More than half the days (2)",
            "phq9_7_concentration": "Several days (1)",
            "phq9_8_moving": "Several days (1)",
            "phq9_9_self_harm": "Several days (1)",
            **{f"gad7_{index}": "More than half the days (2)" for index in range(1, 8)},
            "crafft_a_alcohol": "Yes",
            "crafft_a_marijuana": "No",
            "crafft_a_other_high": "Yes",
            "crafft_b_car": "No",
            "crafft_b_relax": "Yes",
            "crafft_b_alone": "No",
            "crafft_b_forget": "Yes",
            "crafft_b_family_friends": "No",
            "crafft_b_trouble": "No",
            **{f"mchat_{index}": "No" for index in range(1, 9)},
        }

        scored = add_calculated_scores("behavioral-test", answers)

        self.assertEqual(scored["phq2_total_score"], "3")
        self.assertEqual(scored["phq9_total_score"], "15")
        self.assertEqual(scored["gad7_total_score"], "14")
        self.assertEqual(scored["crafft_part_a_yes_count"], "2")
        self.assertEqual(scored["crafft_part_b_yes_count"], "2")
        self.assertEqual(scored["mchat_risk_score"], "8")
        self.assertEqual(scored["mchat_risk_level"], "High risk")

        review = review_for_submission({"formId": "behavioral-test", "status": "new", "answers": scored})
        labels = [flag["label"] for flag in review["flags"]]
        self.assertIn("GAD-7 elevated", labels)
        self.assertIn("PHQ-9 elevated", labels)
        self.assertIn("PHQ-9 self-harm review", labels)
        self.assertIn("CRAFFT positive", labels)
        self.assertIn("M-CHAT high risk", labels)

    def test_act_cact_asrs_ace_and_ppsc_scores_are_calculated(self):
        answers = {
            "activity_limit": "Some of the time",
            "shortness_breath": "Once a day",
            "night_symptoms": "Once a week",
            "rescue_inhaler": "2 or 3 times per week",
            "control_rating": "Somewhat controlled",
            "asthma_today": "Good",
            "problem_when_active": "It is a little problem",
            "cough": "Yes, some of the time",
            "wake_up": "No, none of the time",
            "daytime_symptoms": "4-10 days",
            "wheezing": "1-3 days",
            "night_waking": "Not at all",
            "wrap_up": "Sometimes",
            "organization": "Often",
            "remembering": "Very often",
            "avoid_delay": "Often",
            "fidget": "Often",
            "driven": "Rarely",
            "careless_mistakes": "Often",
            "attention_boring_work": "Never",
            "ace_physical_01": "Yes",
            "ace_physical_02": "Yes",
            "ace_cognitive_01": "Yes",
            "ace_emotional_01": "No",
            "ace_sleep_01": "Yes",
            "ace_red_flags": ["Worsening headache", "Repeated vomiting"],
            "ppsc_fights": "Very much",
            "ppsc_breaks_things": "Somewhat",
            "ppsc_is_aggressive": "Very much",
            "ppsc_hard_to_take_out": "Very much",
            "ppsc_hard_to_comfort": "Very much",
        }

        scored = add_calculated_scores("mixed-scoring-test", answers)

        self.assertEqual(scored["act_total_score"], "14")
        self.assertEqual(scored["act_control_status"], "May not be controlled")
        self.assertEqual(scored["cact_total_score"], "21")
        self.assertEqual(scored["cact_control_status"], "Likely controlled")
        self.assertEqual(scored["asrs_part_a_positive_count"], "5")
        self.assertEqual(scored["asrs_part_b_positive_count"], "1")
        self.assertEqual(scored["asrs_screen_result"], "Positive screen")
        self.assertEqual(scored["ace_physical_total"], "2")
        self.assertEqual(scored["ace_cognitive_total"], "1")
        self.assertEqual(scored["ace_emotional_total"], "0")
        self.assertEqual(scored["ace_sleep_total"], "1")
        self.assertEqual(scored["ace_total_symptom_score"], "4")
        self.assertEqual(scored["ace_red_flag_count"], "2")
        self.assertEqual(scored["ppsc_total_score"], "9")

        review = review_for_submission({"formId": "mixed-scoring-test", "status": "new", "answers": scored})
        self.assertIn("PPSC elevated", [flag["label"] for flag in review["flags"]])

    def test_scared_and_vanderbilt_domain_scores_are_calculated(self):
        answers = {
            **{f"child_scared_{index:02d}": "1 - Somewhat true" for index in range(1, 42)},
            **{f"vanderbilt_parent_{index:02d}": "Often (2)" for index in range(1, 49)},
            **{f"vanderbilt_parent_performance_{index:02d}": "Problematic (4)" for index in range(1, 9)},
            "vanderbilt_parent_performance_08": "Severe problem (5)",
        }

        scored = add_calculated_scores("vanderbilt-scared-test", answers)

        self.assertEqual(scored["child_scared_total_score"], "41")
        self.assertEqual(scored["child_scared_total_cutoff_met"], "Yes")
        self.assertEqual(scored["child_scared_panic_somatic_score"], "13")
        self.assertEqual(scored["child_scared_social_anxiety_score"], "7")
        self.assertEqual(scored["child_scared_social_anxiety_cutoff_met"], "No")
        self.assertEqual(scored["vanderbilt_parent_inattention"], "9")
        self.assertEqual(scored["vanderbilt_parent_hyperactive_impulsive"], "9")
        self.assertEqual(scored["vanderbilt_parent_oppositional"], "8")
        self.assertEqual(scored["vanderbilt_parent_conduct"], "15")
        self.assertEqual(scored["vanderbilt_parent_anxiety_depression"], "7")
        self.assertEqual(scored["vanderbilt_parent_performance_4_count"], "7")
        self.assertEqual(scored["vanderbilt_parent_performance_5_count"], "1")
        self.assertEqual(scored["vanderbilt_parent_impairment_present"], "Yes")


if __name__ == "__main__":
    unittest.main()
