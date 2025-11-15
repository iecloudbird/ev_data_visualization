"""
Data loading and preprocessing utilities for the EV Dashboard.
Handles loading datasets and calculating derived metrics.
"""

import pandas as pd
import numpy as np
from pathlib import Path


class EVDataLoader:
    """Load and process EV datasets for dashboard visualization."""
    
    def __init__(self, data_dir='data/processed'):
        """
        Initialize data loader.
        
        Args:
            data_dir: Path to processed data directory (relative to project root)
        """
        # Get project root (2 levels up from this file: dash/utils/data_loader.py)
        project_root = Path(__file__).parent.parent.parent
        self.data_dir = project_root / data_dir
        self._cache = {}
    
    def load_merged_dataset(self):
        """Load the main merged EV dataset with caching."""
        if 'merged' not in self._cache:
            file_path = self.data_dir / 'merged_dataset.csv'
            df = pd.read_csv(file_path)
            self._cache['merged'] = df
        return self._cache['merged'].copy()
    
    def load_stations_dataset(self):
        """Load the enhanced charging stations dataset with caching."""
        if 'stations' not in self._cache:
            file_path = self.data_dir / 'stations_enhanced.csv'
            df = pd.read_csv(file_path)
            self._cache['stations'] = df
        return self._cache['stations'].copy()
    
    def get_ev_stock_by_region_year(self):
        """
        Get aggregated EV stock data by region and year.
        
        Returns:
            DataFrame with columns: region, year, total_ev_stock, total_stations, stations_per_ev
        """
        df = self.load_merged_dataset()
        
        # Filter for EV stock data
        ev_stock = df[df['ev_stock'].notna()].copy()
        
        # Aggregate by region and year
        agg_data = ev_stock.groupby(['region', 'year']).agg({
            'ev_stock': 'sum',
            'total_stations': 'first',
            'stations_per_million_evs': 'first'
        }).reset_index()
        
        agg_data.columns = ['region', 'year', 'total_ev_stock', 'total_stations', 'stations_per_million_evs']
        
        # Calculate stations per EV (handle division by zero)
        agg_data['stations_per_ev'] = np.where(
            agg_data['total_ev_stock'] > 0,
            agg_data['total_stations'] / agg_data['total_ev_stock'],
            0
        )
        
        return agg_data
    
    def get_top_regions(self, n=10, year=None):
        """
        Get top N regions by EV stock.
        
        Args:
            n: Number of top regions to return
            year: Specific year to filter (if None, uses latest year)
        
        Returns:
            List of region names
        """
        df = self.get_ev_stock_by_region_year()
        
        if year is None:
            year = df['year'].max()
        
        df_year = df[df['year'] == year]
        top_regions = df_year.nlargest(n, 'total_ev_stock')['region'].tolist()
        
        return top_regions
    
    def get_powertrain_data(self):
        """
        Get BEV vs PHEV comparison data.
        
        Returns:
            DataFrame with powertrain breakdown by region and year
        """
        df = self.load_merged_dataset()
        
        # Filter for BEV and PHEV data
        powertrain_data = df[
            (df['powertrain'].isin(['BEV', 'PHEV', 'FCEV'])) &
            (df['ev_stock'].notna())
        ].copy()
        
        # Aggregate
        agg_data = powertrain_data.groupby(['region', 'year', 'powertrain']).agg({
            'ev_stock': 'sum'
        }).reset_index()
        
        return agg_data
    
    def get_charging_infrastructure_summary(self, year=None):
        """
        Get charging infrastructure summary statistics.
        
        Args:
            year: Year to filter (if None, uses latest year)
        
        Returns:
            DataFrame with infrastructure metrics by region
        """
        df = self.load_merged_dataset()
        
        if year is None:
            year = df['year'].max()
        
        df_year = df[df['year'] == year].copy()
        
        # Aggregate charging points by region
        infra_summary = df_year.groupby('region').agg({
            'ev_charging_points': 'sum',
            'total_stations': 'first',
            'ev_stock': 'sum'
        }).reset_index()
        
        # Calculate EVs per charging point
        infra_summary['evs_per_charging_point'] = np.where(
            infra_summary['ev_charging_points'] > 0,
            infra_summary['ev_stock'] / infra_summary['ev_charging_points'],
            np.nan
        )
        
        # Categorize infrastructure adequacy
        def categorize_infrastructure(ratio):
            if pd.isna(ratio):
                return 'No Data'
            elif ratio <= 50:
                return 'Well Served (≤50 EVs/station)'
            elif ratio <= 100:
                return 'Adequate (51-100 EVs/station)'
            elif ratio <= 200:
                return 'Strained (101-200 EVs/station)'
            else:
                return 'Insufficient (>200 EVs/station)'
        
        infra_summary['infrastructure_category'] = infra_summary['evs_per_charging_point'].apply(
            categorize_infrastructure
        )
        
        return infra_summary
    
    def get_year_range(self):
        """Get the min and max years available in the dataset."""
        df = self.load_merged_dataset()
        return int(df['year'].min()), int(df['year'].max())
    
    def get_available_regions(self):
        """Get list of all available regions."""
        df = self.load_merged_dataset()
        return sorted(df['region'].dropna().unique().tolist())
    
    def calculate_summary_stats(self, year=None):
        """
        Calculate summary statistics for KPI cards.
        
        Args:
            year: Year to calculate stats for (if None, uses latest)
        
        Returns:
            Dictionary with summary statistics
        """
        df = self.get_ev_stock_by_region_year()
        
        if year is None:
            year = df['year'].max()
        
        df_year = df[df['year'] == year]
        
        # Calculate global totals
        total_ev_stock = df_year['total_ev_stock'].sum()
        total_stations = df_year['total_stations'].sum()
        avg_stations_per_ev = total_stations / total_ev_stock if total_ev_stock > 0 else 0
        
        # Calculate YoY growth (if previous year exists)
        if year > df['year'].min():
            df_prev_year = df[df['year'] == year - 1]
            prev_total = df_prev_year['total_ev_stock'].sum()
            yoy_growth = ((total_ev_stock - prev_total) / prev_total * 100) if prev_total > 0 else 0
        else:
            yoy_growth = 0
        
        return {
            'total_ev_stock': total_ev_stock,
            'total_stations': total_stations,
            'avg_stations_per_ev': avg_stations_per_ev,
            'yoy_growth_pct': yoy_growth,
            'year': year
        }


# Create a global instance for easy import
data_loader = EVDataLoader()
