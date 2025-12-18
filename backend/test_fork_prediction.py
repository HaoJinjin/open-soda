"""
测试 fork_prediction.py 的封装函数
"""

from fork_prediction import predict_fork_count
import json

print("=" * 60)
print("🧪 测试 Fork 预测函数")
print("=" * 60)

try:
    print("\n开始预测...")
    result = predict_fork_count()
    
    print("\n✅ 预测成功！")
    print(f"\n📊 元数据信息:")
    print(f"  目标列: {result['predictions']['metadata']['target_column']}")
    print(f"  总样本数: {result['predictions']['metadata']['total_samples']}")
    print(f"  有效样本数: {result['predictions']['metadata']['valid_samples']}")
    print(f"  训练样本数: {result['predictions']['metadata']['train_samples']}")
    print(f"  测试样本数: {result['predictions']['metadata']['test_samples']}")
    
    print(f"\n📈 模型评估指标:")
    metrics = result['predictions']['metadata']['metrics']
    print(f"  R² Score: {metrics['R2_score']}")
    print(f"  RMSE: {metrics['RMSE']}")
    print(f"  MAE: {metrics['MAE']}")
    
    print(f"\n🎯 预测结果（前5条）:")
    for i, pred in enumerate(result['predictions']['predictions'][:5]):
        print(f"  [{i+1}] {pred['project_name']}")
        print(f"      真实值: {pred['true_value']}")
        print(f"      预测值: {pred['predicted_value']}")
        print(f"      绝对误差: {pred['absolute_error']}")
        print(f"      相对误差: {pred['relative_error_percent']}%")
    
    print(f"\n🔍 特征重要性（Top 5）:")
    for i, feat in enumerate(result['feature_importance']['feature_importance'][:5]):
        print(f"  [{i+1}] {feat['feature_name']}: {feat['importance']:.4f}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！函数可以正常使用。")
    print("=" * 60)
    
    # 保存结果到文件（可选）
    with open('backendData/fork_prediction_test_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\n💾 结果已保存到: backendData/fork_prediction_test_result.json")
    
except Exception as e:
    print(f"\n❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()

