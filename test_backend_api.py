"""
测试后端 API 是否正常工作
"""
import requests
import json

def test_fork_prediction():
    """测试 Fork 预测接口"""
    print("=" * 60)
    print("测试 Fork 预测接口")
    print("=" * 60)
    
    try:
        response = requests.post('http://localhost:8000/api/predict/fork', timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 请求成功")
            print(f"success: {data.get('success')}")
            
            if data.get('success'):
                result_data = data.get('data', {})
                print(f"\n数据结构:")
                print(f"  - predictions: {type(result_data.get('predictions'))}")
                print(f"  - feature_importance: {type(result_data.get('feature_importance'))}")
                
                if 'predictions' in result_data:
                    pred = result_data['predictions']
                    print(f"\npredictions 结构:")
                    print(f"  - metadata: {type(pred.get('metadata'))}")
                    print(f"  - predictions: {type(pred.get('predictions'))}")
                    
                    if 'metadata' in pred:
                        meta = pred['metadata']
                        print(f"\nmetadata 内容:")
                        for key, value in meta.items():
                            print(f"  - {key}: {value}")
                
                print(f"\n✅ Fork 预测接口正常")
            else:
                print(f"❌ success=False")
        else:
            print(f"❌ HTTP 错误: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端已启动：python backend/main.py")
    except Exception as e:
        print(f"❌ 错误: {e}")


def test_indicator_statistics():
    """测试指标统计接口"""
    print("\n" + "=" * 60)
    print("测试指标统计接口")
    print("=" * 60)
    
    try:
        response = requests.get('http://localhost:8000/api/statistics/indicators', timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 请求成功")
            print(f"success: {data.get('success')}")
            
            if data.get('success'):
                result_data = data.get('data', {})
                print(f"\n数据结构:")
                for key in result_data.keys():
                    print(f"  - {key}: {type(result_data[key])}")
                
                if 'metadata' in result_data:
                    print(f"\nmetadata 内容:")
                    for key, value in result_data['metadata'].items():
                        print(f"  - {key}: {value}")
                
                if 'correlation_matrix' in result_data:
                    corr = result_data['correlation_matrix']
                    print(f"\ncorrelation_matrix 指标:")
                    for indicator in corr.keys():
                        print(f"  - {indicator}")
                
                print(f"\n✅ 指标统计接口正常")
            else:
                print(f"❌ success=False")
        else:
            print(f"❌ HTTP 错误: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端已启动：python backend/main.py")
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    print("\n🔍 开始测试后端 API...\n")
    test_fork_prediction()
    test_indicator_statistics()
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

