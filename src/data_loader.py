"""Data Loader module for CustomerAtlas."""

from pathlib import Path
from typing import Optional, Tuple, Union
import pandas as pd
from analytics import load_dataset, validate_dataset, REQUIRED_COLUMNS


class DataLoader:
    """Robust data loader and validator."""

    def __init__(self, data_dir: Optional[Union[str, Path]] = None):
        self.data_dir = Path(data_dir) if data_dir else None

    def load_customer_features(self) -> pd.DataFrame:
        """Load canonical customer 360 feature store."""
        return load_dataset("customer_360_features.csv", data_dir=self.data_dir)

    def load_fact_orders(self) -> pd.DataFrame:
        """Load order transaction fact records."""
        return load_dataset("fact_orders.csv", data_dir=self.data_dir, parse_dates=("purchase_date",))

    def load_recommendations(self) -> pd.DataFrame:
        """Load Next-Best-Category recommendations."""
        return load_dataset("recommendations.csv", data_dir=self.data_dir)

    def validate(self, df: pd.DataFrame) -> bool:
        """Check if dataset conforms to schema contract."""
        return validate_dataset(df).get("is_valid", False)
