export const formatBrl = (val) => {
  if (val === null || val === undefined || isNaN(val)) return 'R$ 0.00';
  return `R$ ${Number(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

export const formatPct = (val) => {
  if (val === null || val === undefined || isNaN(val)) return '0.0%';
  return `${(Number(val) * 100).toFixed(1)}%`;
};

export const formatNum = (val) => {
  if (val === null || val === undefined || isNaN(val)) return '0';
  return Number(val).toLocaleString('en-US');
};

export const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A';
  try {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
};
