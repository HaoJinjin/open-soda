"""
测试预测功能
用于验证 fork_pridiction.py 的封装函数是否正常工作
"""

from fork_pridiction import predict_target_column
import json

# 测试参数
csv_path = r"C:\Users\22390\Desktop\OpenSODA\backendData\top_300_metrics.csv"
target_column = "forks"  # 可以改成其他列，如 "stars", "watchers" 等

print("=" * 60)
print("🧪 测试预测功能")
print("=" * 60)
print(f"CSV 路径: {csv_path}")
print(f"目标列: {target_column}")
print("-" * 60)

try:
    # 调用预测函数
    result = predict_target_column(csv_path, target_column)
    
    print("\n✅ 预测成功！\n")
    
    # 显示元数据
    print("📊 模型元数据:")
    metadata = result["predictions"]["metadata"]
    print(f"  目标列: {metadata['target_column']}")
    print(f"  总样本数: {metadata['total_samples']}")
    print(f"  有效样本数: {metadata['valid_samples']}")
    print(f"  训练样本数: {metadata['train_samples']}")
    print(f"  测试样本数: {metadata['test_samples']}")
    
    # 显示评估指标
    print("\n📈 模型评估指标:")
    metrics = metadata['metrics']
    print(f"  R² Score: {metrics['R2_score']}")
    print(f"  RMSE: {metrics['RMSE']}")
    print(f"  MAE: {metrics['MAE']}")
    
    # 显示前5个预测结果
    print("\n🎯 预测结果（前5条）:")
    predictions = result["predictions"]["predictions"][:5]
    for i, pred in enumerate(predictions, 1):
        print(f"\n  [{i}] {pred['project_name']}")
        print(f"      真实值: {pred['true_value']}")
        print(f"      预测值: {pred['predicted_value']}")
        print(f"      绝对误差: {pred['absolute_error']}")
        print(f"      相对误差: {pred['relative_error_percent']}%")
    
    # 显示前5个特征重要性
    print("\n⭐ 特征重要性（前5个）:")
    importance = result["feature_importance"]["feature_importance"][:5]
    for i, feat in enumerate(importance, 1):
        print(f"  [{i}] {feat['feature_name']}: {feat['importance']:.4f}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！函数工作正常。")
    print("=" * 60)
    
    # 可选：保存结果到文件
    save_result = input("\n是否保存结果到文件？(y/n): ").strip().lower()
    if save_result == 'y':
        output_file = "test_prediction_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ 结果已保存到: {output_file}")

except Exception as e:
    print(f"\n❌ 预测失败: {str(e)}")
    import traceback
    traceback.print_exc()

