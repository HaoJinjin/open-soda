"""
测试 Fork 预测修复后的结果
"""
import sys
sys.path.append('backend')

from fork_prediction import predict_fork_count
import json

print("=" * 60)
print("测试 Fork 预测修复")
print("=" * 60)

try:
    print("\n🔄 开始预测...")
    result = predict_fork_count()
    
    print("\n✅ 预测完成！")
    
    # 检查数据结构
    print("\n📊 数据结构检查:")
    print(f"  - predictions: {'✅' if 'predictions' in result else '❌'}")
    print(f"  - feature_importance: {'✅' if 'feature_importance' in result else '❌'}")
    
    # 检查 metadata
    if 'predictions' in result and 'metadata' in result['predictions']:
        meta = result['predictions']['metadata']
        print(f"\n📋 Metadata:")
        print(f"  - target_column: {meta.get('target_column')}")
        print(f"  - valid_samples: {meta.get('valid_samples')}")
        print(f"  - R2_score: {meta.get('metrics', {}).get('R2_score')}")
        print(f"  - RMSE: {meta.get('metrics', {}).get('RMSE')}")
        print(f"  - MAE: {meta.get('metrics', {}).get('MAE')}")
    
    # 检查预测结果
    if 'predictions' in result and 'predictions' in result['predictions']:
        preds = result['predictions']['predictions']
        print(f"\n🎯 预测结果样本（前3条）:")
        for i, pred in enumerate(preds[:3]):
            print(f"\n  [{i+1}] {pred.get('project_name')}")
            print(f"      真实值: {pred.get('true_value')} (类型: {type(pred.get('true_value')).__name__})")
            print(f"      预测值: {pred.get('predicted_value')} (类型: {type(pred.get('predicted_value')).__name__})")
            print(f"      绝对误差: {pred.get('absolute_error')}")
            print(f"      相对误差: {pred.get('relative_error_percent')}%")
    
    # 检查特征重要性
    if 'feature_importance' in result and 'feature_importance' in result['feature_importance']:
        feat_imp = result['feature_importance']['feature_importance']
        print(f"\n🎯 特征重要性（Top 5）:")
        for i, feat in enumerate(feat_imp[:5]):
            print(f"  [{i+1}] {feat.get('feature_name')}: {feat.get('importance'):.6f}")
    
    # 验证数据类型
    print("\n✅ 数据类型验证:")
    if 'predictions' in result and 'predictions' in result['predictions']:
        first_pred = result['predictions']['predictions'][0]
        true_val = first_pred.get('true_value')
        pred_val = first_pred.get('predicted_value')
        
        # 检查是否为数值
        is_true_numeric = isinstance(true_val, (int, float))
        is_pred_numeric = isinstance(pred_val, (int, float))
        
        print(f"  - true_value 是数值: {'✅' if is_true_numeric else '❌ (是 ' + type(true_val).__name__ + ')'}")
        print(f"  - predicted_value 是数值: {'✅' if is_pred_numeric else '❌ (是 ' + type(pred_val).__name__ + ')'}")
        
        if is_true_numeric and is_pred_numeric:
            print(f"\n🎉 修复成功！数据现在是数值类型了！")
        else:
            print(f"\n⚠️ 警告：数据仍然不是数值类型")
    
    # 保存结果到文件
    output_file = 'test_fork_prediction_result.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n💾 完整结果已保存到: {output_file}")
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

