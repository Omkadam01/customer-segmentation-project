"""
PROJECT 2 — CUSTOMER SEGMENTATION
Script 01: RFM Feature Engineering + K-Means Clustering
Full pipeline: raw sales → RFM scores → scaled features → optimal k → segment labels
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import warnings, os, sys
warnings.filterwarnings('ignore')

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_PATH    = os.path.dirname(os.path.abspath(__file__))
DATA_PATH    = os.path.join(BASE_PATH, 'sales_data.csv')
REPORTS_PATH = os.path.join(BASE_PATH, 'reports')
MODELS_PATH  = os.path.join(BASE_PATH, 'models')
os.makedirs(REPORTS_PATH, exist_ok=True)
os.makedirs(MODELS_PATH, exist_ok=True)

PALETTE  = ['#1a56db', '#0e9f6e', '#e02424']
SNAPSHOT = pd.Timestamp('2024-01-01')


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: Load & compute RFM
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 55)
print("  CUSTOMER SEGMENTATION — RFM + K-Means Pipeline")
print("=" * 55)

sales = pd.read_csv(DATA_PATH, parse_dates=['Date'])
print(f"\nLoaded {len(sales):,} transactions from {sales['CustomerID'].nunique()} customers")

rfm = (
    sales.groupby('CustomerID')
    .agg(
        Recency   = ('Date',    lambda x: (SNAPSHOT - x.max()).days),
        Frequency = ('OrderID', 'count'),
        Monetary  = ('Revenue', 'sum')
    )
    .reset_index()
)

print(f"\nRFM Summary:")
print(rfm[['Recency', 'Frequency', 'Monetary']].describe().round(1).to_string())


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: Scale features
# ─────────────────────────────────────────────────────────────────────────────
scaler  = StandardScaler()
rfm_s   = scaler.fit_transform(rfm[['Recency', 'Frequency', 'Monetary']])

print(f"\nFeature scaling: StandardScaler applied")
print(f"Scaled shape: {rfm_s.shape}")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: Find optimal k (Elbow + Silhouette)
# ─────────────────────────────────────────────────────────────────────────────
k_range   = range(2, 9)
inertias  = []
sil_scores = []

for k in k_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(rfm_s)
    inertias.append(km.inertia_)
    sil_scores.append(silhouette_score(rfm_s, km.labels_))
    print(f"  k={k} | Inertia={km.inertia_:>10,.1f} | Silhouette={sil_scores[-1]:.4f}")

best_k = k_range.start + sil_scores.index(max(sil_scores))
print(f"\n✅ Optimal k = {best_k} (silhouette = {max(sil_scores):.4f})")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: Fit final model
# ─────────────────────────────────────────────────────────────────────────────
km_final  = KMeans(n_clusters=best_k, random_state=42, n_init=10)
rfm['Cluster'] = km_final.fit_predict(rfm_s)

# Label by descending monetary mean
means  = rfm.groupby('Cluster')['Monetary'].mean().sort_values(ascending=False)
rank   = {c: i for i, c in enumerate(means.index)}
labels = {0: 'Champions', 1: 'Loyal Customers', 2: 'At-Risk'}
rfm['Segment'] = rfm['Cluster'].map(rank).map(labels)

print(f"\nCluster → Segment mapping:")
for c, m in means.items():
    print(f"  Cluster {c} → {labels[rank[c]]:20s} (avg monetary ₹{m:,.0f})")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: Segment summary
# ─────────────────────────────────────────────────────────────────────────────
summary = (
    rfm.groupby('Segment')
    .agg(
        Count          = ('CustomerID', 'count'),
        Avg_Recency    = ('Recency', 'mean'),
        Avg_Frequency  = ('Frequency', 'mean'),
        Avg_Monetary   = ('Monetary', 'mean'),
        Total_Revenue  = ('Monetary', 'sum')
    )
    .round(1)
    .reset_index()
)
summary['Revenue_Share_%'] = (summary['Total_Revenue'] / summary['Total_Revenue'].sum() * 100).round(1)
summary['Customer_Share_%'] = (summary['Count'] / summary['Count'].sum() * 100).round(1)

print("\n" + "=" * 65)
print("  SEGMENT PERFORMANCE SUMMARY")
print("=" * 65)
print(summary.to_string(index=False))

# Save CSVs
rfm.to_csv(os.path.join(BASE_PATH, 'rfm_segments.csv'), index=False)
summary.to_csv(os.path.join(BASE_PATH, 'segment_summary.csv'), index=False)
print("\n✅ Saved: rfm_segments.csv & segment_summary.csv")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 6: Visualisations
# ─────────────────────────────────────────────────────────────────────────────

# 6a. Elbow + Silhouette curves
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
fig.suptitle('Optimal K Selection', fontsize=13, fontweight='bold')

axes[0].plot(list(k_range), inertias, 'o-', color='#1a56db', linewidth=2, markersize=7)
axes[0].set_xlabel('Number of Clusters (k)')
axes[0].set_ylabel('Inertia (WCSS)')
axes[0].set_title('Elbow Method')
axes[0].axvline(best_k, color='#e02424', linestyle='--', linewidth=1.5, label=f'Optimal k={best_k}')
axes[0].legend(fontsize=9)

axes[1].plot(list(k_range), sil_scores, 's-', color='#0e9f6e', linewidth=2, markersize=7)
axes[1].set_xlabel('Number of Clusters (k)')
axes[1].set_ylabel('Silhouette Score')
axes[1].set_title('Silhouette Analysis')
axes[1].axvline(best_k, color='#e02424', linestyle='--', linewidth=1.5, label=f'Best k={best_k}')
axes[1].legend(fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(REPORTS_PATH, '01_optimal_k.png'), bbox_inches='tight', dpi=150)
plt.close()
print("✅ Saved: 01_optimal_k.png")


# 6b. RFM Distributions per Segment
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('RFM Distribution by Customer Segment', fontsize=13, fontweight='bold')
colors = {'Champions': '#1a56db', 'Loyal Customers': '#0e9f6e', 'At-Risk': '#e02424'}
dims   = ['Recency', 'Frequency', 'Monetary']

for ax, dim in zip(axes, dims):
    for seg in ['Champions', 'Loyal Customers', 'At-Risk']:
        subset = rfm[rfm['Segment'] == seg][dim]
        ax.hist(subset, bins=20, alpha=0.6, color=colors[seg], label=seg, edgecolor='white')
    ax.set_xlabel(dim)
    ax.set_ylabel('Count')
    ax.set_title(f'{dim} Distribution')
    ax.legend(fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(REPORTS_PATH, '02_rfm_distributions.png'), bbox_inches='tight', dpi=150)
plt.close()
print("✅ Saved: 02_rfm_distributions.png")


# 6c. 2D PCA scatter
pca    = PCA(n_components=2, random_state=42)
coords = pca.fit_transform(rfm_s)
rfm['PCA1'] = coords[:, 0]
rfm['PCA2'] = coords[:, 1]

fig, ax = plt.subplots(figsize=(10, 7))
for seg, color in colors.items():
    mask = rfm['Segment'] == seg
    ax.scatter(rfm.loc[mask, 'PCA1'], rfm.loc[mask, 'PCA2'],
               c=color, label=seg, alpha=0.7, s=50, edgecolors='white', linewidths=0.5)
ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)')
ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)')
ax.set_title('Customer Segments — PCA 2D Projection', fontsize=13, fontweight='bold')
ax.legend(fontsize=11, framealpha=0.9)
ax.grid(alpha=0.2)
plt.tight_layout()
plt.savefig(os.path.join(REPORTS_PATH, '03_pca_scatter.png'), bbox_inches='tight', dpi=150)
plt.close()
print("✅ Saved: 03_pca_scatter.png")


# 6d. Revenue share donut
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
sizes  = summary['Revenue_Share_%'].values
clrs   = [colors[s] for s in summary['Segment']]
segs   = summary['Segment'].values

axes[0].pie(sizes, labels=segs, colors=clrs, autopct='%1.1f%%',
            startangle=90, pctdistance=0.8, wedgeprops=dict(width=0.55))
axes[0].set_title('Revenue Share by Segment', fontsize=12, fontweight='bold')

axes[1].barh(summary['Segment'], summary['Count'], color=clrs, alpha=0.9)
axes[1].set_xlabel('Number of Customers')
axes[1].set_title('Customer Count by Segment', fontsize=12, fontweight='bold')
for i, v in enumerate(summary['Count']):
    axes[1].text(v + 1, i, str(v), va='center', fontsize=10)

plt.tight_layout()
plt.savefig(os.path.join(REPORTS_PATH, '04_segment_overview.png'), bbox_inches='tight', dpi=150)
plt.close()
print("✅ Saved: 04_segment_overview.png")


# 6e. RFM heatmap (avg per segment)
rfm_avg = rfm.groupby('Segment')[['Recency', 'Frequency', 'Monetary']].mean().round(1)
rfm_norm = (rfm_avg - rfm_avg.min()) / (rfm_avg.max() - rfm_avg.min())

fig, ax = plt.subplots(figsize=(8, 4))
sns.heatmap(rfm_norm, annot=rfm_avg, fmt='.1f', cmap='Blues',
            linewidths=0.5, ax=ax, cbar_kws={'label': 'Normalised Score'})
ax.set_title('RFM Profile Heatmap by Segment (raw values annotated)', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(REPORTS_PATH, '05_rfm_heatmap.png'), bbox_inches='tight', dpi=150)
plt.close()
print("✅ Saved: 05_rfm_heatmap.png")

print("\n✅ Full pipeline complete.")
print(f"   Model: KMeans k={best_k}, silhouette={max(sil_scores):.4f}")
print(f"   Data:  {len(rfm)} customers segmented")
