export function calculateHealth(raw) {
  const input = {
    initialInvestment: Number(raw.initialInvestment),
    monthlyFixedCosts: Number(raw.monthlyFixedCosts),
    unitCost: Number(raw.unitCost),
    unitPrice: Number(raw.unitPrice),
    monthlySales: Number(raw.monthlySales),
  };

  for (const [key, value] of Object.entries(input)) {
    if (!Number.isFinite(value) || value < 0) {
      throw new Error(`Invalid value for ${key}`);
    }
  }

  const contributionPerUnit = input.unitPrice - input.unitCost;
  if (contributionPerUnit <= 0) {
    throw new Error("Selling price must be greater than product cost.");
  }

  const revenue = input.unitPrice * input.monthlySales;
  const variableCosts = input.unitCost * input.monthlySales;
  const contribution = contributionPerUnit * input.monthlySales;
  const monthlyProfit = contribution - input.monthlyFixedCosts;
  const breakEvenUnits = Math.ceil(input.monthlyFixedCosts / contributionPerUnit);
  const unitsToBreakEven = Math.max(0, breakEvenUnits - input.monthlySales);
  const paybackMonths = monthlyProfit > 0
    ? input.initialInvestment / monthlyProfit
    : null;
  const profitMargin = revenue > 0 ? monthlyProfit / revenue : 0;
  const breakEvenGapRatio = breakEvenUnits > 0 ? unitsToBreakEven / breakEvenUnits : 0;

  let status = "red";
  if (monthlyProfit > 0 && profitMargin >= 0.10) {
    status = "green";
  } else if (monthlyProfit >= 0 || breakEvenGapRatio <= 0.20) {
    status = "yellow";
  }

  return {
    ...input,
    contributionPerUnit,
    revenue,
    variableCosts,
    contribution,
    monthlyProfit,
    breakEvenUnits,
    unitsToBreakEven,
    paybackMonths,
    profitMargin,
    status,
  };
}

export function fallbackInsight(result) {
  if (result.monthlyProfit > 0) {
    if (result.profitMargin < 0.10) {
      return "You are profitable, but the margin is thin. Test a small price increase or reduce one recurring cost before chasing more volume.";
    }
    return "You are above break-even. Protect the margin first, then test whether extra sales can be added without raising fixed costs.";
  }

  if (result.unitsToBreakEven <= Math.max(3, Math.ceil(result.breakEvenUnits * 0.1))) {
    return `You are close to break-even. Focus on selling ${result.unitsToBreakEven} more unit${result.unitsToBreakEven === 1 ? "" : "s"} before making a larger change.`;
  }

  return "You are below break-even. Start with the biggest lever: contribution per sale. Review price and product cost before adding more fixed expense.";
}