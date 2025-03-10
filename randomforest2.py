import pandas as pd
from sklearn.model_selection import train_test_split, KFold, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
from sklearn.metrics import r2_score

# 讀取資料
file_path = 'total+Advance_2.xlsx'
data = pd.read_excel(file_path)

# 特徵和目標變數
X = data.drop(columns=['salary24_25'])
y = data['salary24_25']

# 1. 分割測試集 (20% 的資料)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"訓練集大小: {len(X_train)} 筆 ({len(X_train)/len(data)*100:.1f}%)")
print(f"測試集大小: {len(X_test)} 筆 ({len(X_test)/len(data)*100:.1f}%)")

# 2. 定義超參數搜尋空間
param_grid = {
    'n_estimators': [50, 100, 150, 200], # 決策樹的數量
    'max_depth': [None, 10, 15, 20, 30], # 樹的最大深度
    'min_samples_split': [2, 5, 10], # 內部節點再劃分所需的最小樣本數
    'min_samples_leaf': [1, 2, 4], # 葉節點最少樣本數
    'max_features': [None, 'sqrt'] # 最大特徵數
}

# 3. 設定基礎模型和 GridSearchCV
rf = RandomForestRegressor(random_state=42) #random_state是隨機種子
kf = KFold(n_splits=5, shuffle=True, random_state=42) 
grid_search = GridSearchCV(
    estimator=rf,
    param_grid=param_grid,
    cv=kf,
    scoring='neg_mean_squared_error',
    n_jobs = -1,  # 使用所有可用的 CPU 核心
    verbose = 2
)

# 4. 執行網格搜尋
print("開始執行網格搜尋...")
grid_search.fit(X_train, y_train)

# 5. 輸出訓練集最佳參數和 RMSE
print("\n最佳參數組合:")
print(grid_search.best_params_)
# 計算並印出 RMSE
print(f"\n訓練集最佳 RMSE: {np.sqrt(-grid_search.best_score_):,.2f}")

# 計算並印出 R²
y_pred = grid_search.best_estimator_.predict(X_train)
r2 = r2_score(y_train, y_pred)
print(f"訓練集 R²: {r2:.3f}")

# 6. 使用最佳參數的模型進行預測
best_rf = grid_search.best_estimator_
y_pred_test = best_rf.predict(X_test)
test_rmse = np.sqrt(np.mean((y_test - y_pred_test) ** 2))
test_r2 = best_rf.score(X_test, y_test)

print("\n測試集結果:")
print(f"測試集 RMSE: {test_rmse:,.2f}")
print(f"測試集 R²: {test_r2:.3f}")

# 7. 繪製測試集的預測vs實際值散點圖
plt.figure(figsize=(8, 6))
plt.scatter(y_test / 1_000_000, y_pred_test / 1_000_000, alpha=0.6)
plt.plot(
    [min(y_test / 1_000_000), max(y_test / 1_000_000)],
    [min(y_test / 1_000_000), max(y_test / 1_000_000)],
    color='red', linestyle='--'
)
plt.title('Test Set: Actual vs Predicted Salary (Millions)')
plt.xlabel('Actual Salary (Millions)')
plt.ylabel('Predicted Salary (Millions)')
plt.grid(True)
plt.tight_layout()
plt.show()

# 8. 顯示特徵重要性
feature_importance = pd.DataFrame({
    'Feature': X_train.columns,
    'Importance': best_rf.feature_importances_
}).sort_values('Importance', ascending=False)

print("\n前10個最重要的特徵:")
print(feature_importance.head(10))

plt.figure(figsize=(10, 6))
sns.barplot(x='Importance', y='Feature', data=feature_importance.head(10))
plt.title('Top 10 Important Features in Random Forest')
plt.xlabel('Importance')
plt.ylabel('Feature')
plt.tight_layout()
plt.show()

# 9. 顯示所有參數組合的表現（選擇性）
cv_results = pd.DataFrame(grid_search.cv_results_)
cv_results['RMSE'] = np.sqrt(-cv_results['mean_test_score'])
best_results = cv_results.sort_values('RMSE').head()
print("\n最佳的5組參數組合:")
print(best_results[['params', 'RMSE']].to_string())  # 完整顯示參數
