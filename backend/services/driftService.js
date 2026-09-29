const calculatePsi = (baselineArr, targetArr, numBuckets = 10) => {
  const bClean = baselineArr.filter((v) => v !== null && !isNaN(v)).sort((a, b) => a - b);
  const tClean = targetArr.filter((v) => v !== null && !isNaN(v)).sort((a, b) => a - b);

  if (bClean.length === 0 || tClean.length === 0) return 0.0;

  // Calculate quantile bin edges based on baseline
  const binEdges = [];
  for (let i = 0; i <= numBuckets; i++) {
    const p = i / numBuckets;
    const idx = Math.min(bClean.length - 1, Math.floor(p * bClean.length));
    binEdges.push(bClean[idx]);
  }

  // Deduplicate bin edges
  const uniqueEdges = [...new Set(binEdges)];
  if (uniqueEdges.length < 2) return 0.0;

  uniqueEdges[0] = -Infinity;
  uniqueEdges[uniqueEdges.length - 1] = Infinity;

  const bCounts = new Array(uniqueEdges.length - 1).fill(0);
  const tCounts = new Array(uniqueEdges.length - 1).fill(0);

  bClean.forEach((v) => {
    for (let i = 0; i < uniqueEdges.length - 1; i++) {
      if (v >= uniqueEdges[i] && v < uniqueEdges[i + 1]) {
        bCounts[i]++;
        break;
      }
    }
  });

  tClean.forEach((v) => {
    for (let i = 0; i < uniqueEdges.length - 1; i++) {
      if (v >= uniqueEdges[i] && v < uniqueEdges[i + 1]) {
        tCounts[i]++;
        break;
      }
    }
  });

  const eps = 1e-4;
  const bProps = bCounts.map((c) => c / Math.max(1, bClean.length) + eps);
  const tProps = tCounts.map((c) => c / Math.max(1, tClean.length) + eps);

  const bPropSum = bProps.reduce((s, v) => s + v, 0);
  const tPropSum = tProps.reduce((s, v) => s + v, 0);

  let psi = 0.0;
  for (let i = 0; i < bProps.length; i++) {
    const bp = bProps[i] / bPropSum;
    const tp = tProps[i] / tPropSum;
    psi += (tp - bp) * Math.log(tp / bp);
  }

  return parseFloat(Math.max(0.0, psi).toFixed(4));
};

const runFeatureDriftAudit = (baselineCustomers, currentCustomers) => {
  const monitoredFeatures = [
    'recency_days',
    'frequency',
    'monetary',
    'avg_order_value',
    'predicted_clv',
    'churn_probability',
  ];

  let overallDriftDetected = false;
  const features = [];

  const calcMeanStd = (arr) => {
    if (arr.length === 0) return { mean: 0, std: 0 };
    const mean = arr.reduce((s, v) => s + v, 0) / arr.length;
    const variance = arr.reduce((s, v) => s + Math.pow(v - mean, 2), 0) / arr.length;
    return { mean: parseFloat(mean.toFixed(2)), std: parseFloat(Math.sqrt(variance).toFixed(2)) };
  };

  monitoredFeatures.forEach((feat) => {
    const bVals = baselineCustomers.map((c) => c[feat]).filter((v) => v !== undefined);
    const tVals = currentCustomers.map((c) => c[feat]).filter((v) => v !== undefined);

    const psi = calculatePsi(bVals, tVals);
    let status = 'Stable 🟢';
    let alertTier = 'Normal';

    if (psi >= 0.25) {
      status = 'Significant Drift 🔴';
      alertTier = 'Action Required';
      overallDriftDetected = true;
    } else if (psi >= 0.1) {
      status = 'Moderate Shift 🟡';
      alertTier = 'Monitor';
    }

    const bStats = calcMeanStd(bVals);
    const tStats = calcMeanStd(tVals);

    features.push({
      Feature: feat,
      'PSI Score': psi,
      Status: status,
      'Alert Tier': alertTier,
      'Baseline Mean': bStats.mean,
      'Current Mean': tStats.mean,
      'Baseline Std': bStats.std,
      'Current Std': tStats.std,
    });
  });

  return {
    overall_status: overallDriftDetected ? 'Drift Alert Triggered ⚠️' : 'Distributions Stable 🟢',
    monitored_features_count: features.length,
    drift_detected: overallDriftDetected,
    features,
    governance_policy: 'Drift values >= 0.25 trigger review & human audit before any scheduled model retraining.',
  };
};

module.exports = {
  calculatePsi,
  runFeatureDriftAudit,
};
