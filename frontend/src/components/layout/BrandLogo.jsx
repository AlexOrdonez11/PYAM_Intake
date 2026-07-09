export function BrandLogo({ tone = "light", compact = false, subtitle }) {
  return (
    <div className={`brand-logo brand-logo-${tone} ${compact ? "brand-logo-compact" : ""}`}>
      <span className="brand-logo-frame">
        <img src="/images/pyam_logo.jpg" alt="Pediatric & Young Adult Medicine" />
      </span>
      {subtitle ? <span className="brand-logo-subtitle">{subtitle}</span> : null}
    </div>
  );
}
