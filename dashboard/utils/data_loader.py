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

    def load_iea_sales_dataset(self):
        """Load the original IEA Global EV Sales dataset used in the notebook."""
        if 'iea_sales' not in self._cache:
            file_path = self.data_dir / 'IEA_Global_EV_Data_2024_filled.csv'
            df = pd.read_csv(file_path)
            # Apply notebook-style cleaning: remove EU27 aggregate and percent rows
            if {'region', 'unit'}.issubset(df.columns):
                df = df[~((df['region'] == 'EU27') | (df['unit'] == 'percent'))]
            self._cache['iea_sales'] = df
        return self._cache['iea_sales'].copy()
    
    def load_stations_dataset(self):
        """Load the merged global charging stations dataset with caching."""
        if 'stations' not in self._cache:
            file_path = self.data_dir / 'merged_charging_station' / 'ev_stations_merged_global.csv'
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

    def get_charging_points_distribution_2023(self):
        """
        Replicate notebook Cell 12 aggregation: 2023 charging points by region.

        Filters the IEA sales dataset for parameter contains 'charging points' and year==2023,
        sums by region, identifies top 5 regions, aggregates all other regions into
        'Rest of the world', and drops 'World' from the dataset.
        Returns the final aggregated DataFrame.
        """

        # Load dataset
        df_sales = self.load_iea_sales_dataset()

        # Filter charging points for 2023
        df_charging = df_sales[
            df_sales['parameter'].str.contains('charging points', case=False, na=False)
        ].copy()
        df_charging = df_charging[df_charging['year'] == 2023]

        # Aggregate charging points by region
        charging_latest = df_charging.groupby('region')['value'].sum().reset_index()
        charging_latest.columns = ['region', 'total_charging_points']

        # Remove 'World' before top-5 comparison
        charging_latest = charging_latest[charging_latest['region'] != 'World']

        # Identify top 5 regions with highest charging points
        top5 = charging_latest.nlargest(5, 'total_charging_points')
        top5_names = set(top5['region'].tolist())

        # Merge non-top5 regions into 'Rest of the world'
        charging_latest['region'] = charging_latest['region'].apply(
            lambda r: r if r in top5_names else 'Rest of the world'
        )

        # Final aggregation after region relabel
        charging_final = (
            charging_latest.groupby('region')['total_charging_points']
            .sum()
            .reset_index()
        )

        return charging_final
        
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
        total_stations = self.get_total_stations()
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
            'total_stations': total_stations,  # Always from 2025
            'avg_stations_per_ev': avg_stations_per_ev,
            'yoy_growth_pct': yoy_growth,
            'year': year
        }
    
    def get_total_stations(self):
        """
        Return the global total number of EV charging stations (static value).
        Uses the stations dataset, counts all rows as stations.
        """
        df = self.load_stations_dataset()
        
        # If 'total_stations' column exists, use it; otherwise, count rows
        if 'total_stations' in df.columns:
            total = int(df['total_stations'].sum())
        else:
            # Each row = one station
            total = len(df)
        
        return total

# Create a global instance for easy import
data_loader = EVDataLoader()
