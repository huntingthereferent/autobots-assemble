import assert from "node:assert/strict";
import { calculateHealth, fallbackInsight } from "./logic.mjs";

const profitable = calculateHealth({
  initialInvestment: 5000,
  monthlyFixedCosts: 2200,
  unitCost: 8,
  unitPrice: 20,
  monthlySales: 250,
});
assert.equal(profitable.contributionPerUnit, 12);
assert.equal(profitable.breakEvenUnits, 184);
assert.equal(profitable.unitsToBreakEven, 0);
assert.equal(profitable.monthlyProfit, 800);
assert.equal(profitable.status, "green");
assert.ok(profitable.paybackMonths > 6 && profitable.paybackMonths < 7);

const below = calculateHealth({
  initialInvestment: 5000,
  monthlyFixedCosts: 2200,
  unitCost: 8,
  unitPrice: 20,
  monthlySales: 150,
});
assert.equal(below.monthlyProfit, -400);
assert.equal(below.breakEvenUnits, 184);
assert.equal(below.unitsToBreakEven, 34);
assert.equal(below.status, "yellow");
assert.match(fallbackInsight(below), /break-even|contribution/i);

assert.throws(() => calculateHealth({
  initialInvestment: 0,
  monthlyFixedCosts: 100,
  unitCost: 10,
  unitPrice: 8,
  monthlySales: 50,
}), /greater than product cost/);

console.log("All calculation tests passed.");