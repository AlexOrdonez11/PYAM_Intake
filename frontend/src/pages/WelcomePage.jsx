export function calculateAge(dateOfBirth) {
  if (!dateOfBirth) return null;
  const birth = new Date(`${dateOfBirth}T00:00:00`);
  if (Number.isNaN(birth.getTime())) return null;
  const today = new Date();
  let years = today.getFullYear() - birth.getFullYear();
  let months = today.getMonth() - birth.getMonth();
  if (today.getDate() < birth.getDate()) months -= 1;
  if (months < 0) {
    years -= 1;
    months += 12;
  }
  return { years, months, totalMonths: years * 12 + months };
}

function wellVisitFormId(age, location) {
  if (!age) return "well-child-visit";
  const months = age.totalMonths;
  if (months < 1) return "newborn-2-5-days";
  if (months < 2) return "1-month-visit";
  if (months < 4) return "2-months-visit";
  if (months < 6) return "4-months-visit";
  if (months < 7) return "6-months-visit";
  if (months < 9) return "7-8-months-visit";
  if (months < 10) return "9-months-visit";
  if (months < 12) return "10-months-visit";
  if (months < 14) return location === "maplewood" ? "12-months-visit-maplewood" : "12-months-visit-eagan";
  if (months < 15) return "14-months-visit";
  if (months < 18) return "15-months-visit";
  if (months < 20) return "18-months-visit";
  if (months < 22) return "20-months-visit";
  if (months < 24) return "22-months-visit";
  if (months < 27) return location === "maplewood" ? "2-year-visit-maplewood" : "2-year-visit-eagan";
  if (months < 30) return "27-months-visit";
  if (months < 33) return "30-months-visit";
  if (months < 36) return "33-months-visit";
  if (months < 42) return "3-year-visit";
  if (months < 48) return "42-months-visit";
  if (months < 54) return "4-year-visit";
  if (months < 60) return "54-months-visit";
  if (months < 72) return "5-year-visit";
  const year = age.years;
  if (year <= 6) return "6-year-visit";
  if (year <= 7) return "7-year-visit";
  if (year <= 8) return "8-year-visit";
  if (year <= 9) return "9-year-visit";
  if (year <= 10) return "10-year-visit";
  if (year <= 11) return "11-year-visit";
  if (year <= 12) return "12-year-visit";
  if (year <= 14) return "13-14-year-visit";
  if (year <= 17) return "15-17-year-visit";
  if (year <= 21) return "18-21-year-visit";
  return "well-child-visit";
}

function portalFormId(age) {
  if (!age) return "patient-portal-18-plus";
  if (age.years < 12) return "patient-portal-under-11";
  if (age.years < 18) return "patient-portal-12-17";
  return "patient-portal-18-plus";
}

function unique(values) {
  return [...new Set(values.filter(Boolean))];
}

export function recommendFormsFromRouting(formData) {
  const age = calculateAge(formData.get("dateOfBirth"));
  const visitType = formData.get("visitType");
  const location = formData.get("location");
  const extras = formData.getAll("extras");
  const ids = [];

  if (visitType === "well") ids.push(wellVisitFormId(age, location));
  if (visitType === "portal") ids.push(portalFormId(age));
  if (visitType === "records") ids.push("roi-2026");
  if (visitType === "asthma") ids.push(age && age.years < 12 ? "child-act-4-11" : "asthma-act-12-plus");
  if (visitType === "injury") ids.push("acute-concussion-evaluation");
  if (visitType === "procedure") ids.push("wart-consent");
  if (visitType === "behavioral" || extras.includes("adhd")) ids.push(age && age.years >= 18 ? "adult-adhd-asrs" : "vanderbilt-parent");
  if (extras.includes("teacher")) ids.push("vanderbilt-teacher");
  if (extras.includes("anxiety")) ids.push("initial-anxiety-6-12");
  if (extras.includes("asthma") && visitType !== "asthma") ids.push(age && age.years < 12 ? "child-act-4-11" : "asthma-act-12-plus");

  return unique(ids);
}

export function WelcomePage({ onRoute, onShowAllForms, onStartOver, isStaff }) {
  return (
    <section className="view active" aria-label="Start intake">
      <div className="welcome-layout">
        <BrandLogo tone="light" compact={false} />
        <section className="panel welcome-panel" aria-label="Start intake">
          <button className="ghost-button welcome-start-over" onClick={onStartOver} type="button">Start over</button>
          <div className="welcome-copy">
            <h2>Let's find the right forms for this visit.</h2>
            <p>Answer these questions first. The next screen will show only the packets that match the patient's age and visit reason.</p>
          </div>
          <form className="routing-form routing-form-large" onSubmit={(event) => {
            event.preventDefault();
            onRoute(new FormData(event.currentTarget));
          }}>
            <div className="field full">
              <label htmlFor="routing-dob">Patient date of birth <span className="required">*</span></label>
              <input id="routing-dob" className="field-control" name="dateOfBirth" type="date" required />
            </div>
            <div className="field full">
              <label htmlFor="routing-visit-type">What is this for? <span className="required">*</span></label>
              <select id="routing-visit-type" className="field-control" name="visitType" required>
                <option value="">Select</option>
                <option value="well">Well visit / physical</option>
                <option value="portal">Patient portal access</option>
                <option value="records">Medical records release</option>
                <option value="behavioral">ADHD, anxiety, or behavioral health</option>
                <option value="asthma">Asthma follow up</option>
                <option value="injury">Concussion or head injury</option>
                <option value="procedure">Procedure or treatment consent</option>
              </select>
            </div>
            <div className="field full">
              <label htmlFor="routing-location">Clinic location</label>
              <select id="routing-location" className="field-control" name="location">
                <option value="">No preference / not sure</option>
                <option value="eagan">Eagan</option>
                <option value="maplewood">Maplewood</option>
              </select>
            </div>
            <div className="field full">
              <span className="choice-label">Anything else that applies?</span>
              <div className="choice-group compact">
                {[
                  ["adhd", "ADHD evaluation or follow up"],
                  ["anxiety", "Anxiety concerns"],
                  ["teacher", "Teacher form needed"],
                  ["asthma", "Asthma control test"]
                ].map(([value, label]) => (
                  <label className="choice-option" key={value}>
                    <input type="checkbox" name="extras" value={value} />
                    <span>{label}</span>
                  </label>
                ))}
              </div>
            </div>
            <div className="form-footer onboarding-actions">
              {isStaff ? <button className="secondary-button" onClick={onShowAllForms} type="button">Staff: show all</button> : null}
              <button className="primary-button" type="submit">Continue</button>
            </div>
          </form>
        </section>
      </div>
    </section>
  );
}
import { BrandLogo } from "../components/layout/BrandLogo";
